from fastapi import FastAPI, APIRouter, Request, Header, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

import stripe
import resend
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
import httpx
import base64
import math


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# ─── Premium subscription config (Stripe + Firebase + Resend) ───
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase_service_account.json')
PREMIUM_COLLECTION = os.environ.get('PREMIUM_COLLECTION', 'premium_emails')
PREMIUM_FROM_EMAIL = os.environ.get('PREMIUM_FROM_EMAIL', 'Essenciel O Naturel <onboarding@resend.dev>')
PREMIUM_ADMIN_EMAIL = os.environ.get('PREMIUM_ADMIN_EMAIL', '')

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Lazy Firebase init
_firestore_client = None

def get_firestore():
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client
    try:
        cred_path = ROOT_DIR / FIREBASE_CREDENTIALS_PATH
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
    except Exception as e:
        logging.getLogger(__name__).error(f"Firebase init failed: {e}")
        _firestore_client = None
    return _firestore_client


def iso_now():
    return datetime.now(timezone.utc).isoformat()


def update_premium_status(email: str, active: bool, source: str = 'stripe'):
    """Write/update premium status doc in Firestore (read by the keto app)."""
    fs = get_firestore()
    if not fs:
        raise RuntimeError("Firestore unavailable")
    email_key = (email or '').strip().lower()
    if not email_key:
        raise ValueError("empty email")
    doc_ref = fs.collection(PREMIUM_COLLECTION).document(email_key)
    if active:
        data = {"active": True, "source": source, "since": iso_now(), "expires": None}
    else:
        data = {"active": False}
    doc_ref.set(data, merge=True)
    return email_key


def send_premium_email(to_email: str):
    """Send subscription confirmation email via Resend (non-blocking caller)."""
    if not RESEND_API_KEY:
        return
    params = {
        "from": PREMIUM_FROM_EMAIL,
        "to": [to_email],
        "subject": "Bienvenue dans Keto Premium 🌿",
        "html": (
            "<div style=\"font-family:Arial,sans-serif;max-width:520px;margin:auto;color:#2a2114\">"
            "<h1 style=\"color:#236648\">Bienvenue dans Keto Premium</h1>"
            "<p>Merci pour votre abonnement à <strong>Keto Premium — Essenciel O Naturel</strong>.</p>"
            "<p>Votre accès Premium est désormais activé : modes alimentaires, suivi avancé et toutes les recettes sont débloqués dans l'application.</p>"
            "<p>Connectez-vous avec l'email de votre paiement pour en profiter immédiatement.</p>"
            "<p style=\"margin-top:24px;color:#8a7659\">Belle cétose,<br>Essenciel O Naturel · Naturopathie</p>"
            "</div>"
        ),
    }
    resend.Emails.send(params)


def notify_admin_new_subscriber(email: str):
    if not RESEND_API_KEY or not PREMIUM_ADMIN_EMAIL:
        return
    params = {
        "from": PREMIUM_FROM_EMAIL,
        "to": [PREMIUM_ADMIN_EMAIL],
        "subject": "🎉 Nouvel abonné Premium",
        "html": f"<p>Nouvel abonnement Keto Premium : <strong>{email}</strong></p>",
    }
    resend.Emails.send(params)



# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.get("/app")
async def serve_keto_app():
    return FileResponse(ROOT_DIR / "keto_app.html", media_type="text/html")

@api_router.get("/app-preview")
async def serve_keto_preview():
    return FileResponse(ROOT_DIR / "keto_preview.html", media_type="text/html")

@api_router.get("/download")
async def download_keto_app():
    return FileResponse(
        ROOT_DIR / "keto_app.html",
        media_type="text/html",
        filename="index.html",
    )

@api_router.get("/download-functions")
async def download_functions():
    return FileResponse(
        ROOT_DIR / "keto-firebase-functions.zip",
        media_type="application/zip",
        filename="keto-firebase-functions.zip",
    )

@api_router.get("/promo-pack")
async def download_promo_pack():
    return FileResponse(
        ROOT_DIR / "promo_pack.zip",
        media_type="application/zip",
        filename="keto-visuels-promo.zip",
    )

@api_router.get("/promo/{name}")
async def get_promo_image(name: str):
    safe = os.path.basename(name)
    path = ROOT_DIR / "promo" / safe
    if not path.exists():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="image/png", filename=safe)

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# ─────────────── PREMIUM / STRIPE WEBHOOK ───────────────

@api_router.get("/premium-status")
async def premium_status(email: str):
    fs = get_firestore()
    email_key = (email or '').strip().lower()
    if not fs:
        raise HTTPException(status_code=503, detail="Firestore unavailable")
    doc = fs.collection(PREMIUM_COLLECTION).document(email_key).get()
    if not doc.exists:
        return {"email": email_key, "active": False}
    data = doc.to_dict() or {}
    return {
        "email": email_key,
        "active": data.get("active", False) is not False,
        "source": data.get("source"),
        "since": data.get("since"),
        "expires": data.get("expires"),
    }

@api_router.post("/premium/test-activate")
async def premium_test_activate(payload: dict):
    """Debug-only: activate premium for an email + send email, without Stripe.
    Requires {"email": ..., "token": ...} where token == STRIPE_SECRET_KEY (server secret)."""
    if payload.get("token") != STRIPE_SECRET_KEY or not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=403, detail="forbidden")
    email = payload.get("email", "")
    try:
        key = update_premium_status(email, True, source='stripe_test')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"firestore: {e}")
    email_sent = False
    try:
        send_premium_email(email)
        email_sent = True
    except Exception as e:
        logger.error(f"Resend email failed: {e}")
    return {"ok": True, "email": key, "email_sent": email_sent}

@api_router.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    payload = await request.body()
    # Verify signature if a webhook secret is configured
    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid payload")

    event_type = event.get("type")
    obj = (event.get("data") or {}).get("object") or {}
    logger.info(f"[stripe webhook] received: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            details = obj.get("customer_details") or {}
            email = details.get("email") or obj.get("customer_email")
            if email:
                update_premium_status(email, True, source='stripe')
                try:
                    send_premium_email(email)
                    notify_admin_new_subscriber(email)
                except Exception as e:
                    logger.error(f"Resend email failed: {e}")
        elif event_type == "customer.subscription.deleted":
            customer_id = obj.get("customer")
            email = None
            if customer_id:
                try:
                    cust = stripe.Customer.retrieve(customer_id)
                    email = cust.get("email")
                except Exception as e:
                    logger.error(f"Stripe customer retrieve failed: {e}")
            if email:
                update_premium_status(email, False, source='stripe')
        elif event_type == "customer.subscription.created":
            customer_id = obj.get("customer")
            if customer_id:
                try:
                    cust = stripe.Customer.retrieve(customer_id)
                    email = cust.get("email")
                    if email:
                        update_premium_status(email, True, source='stripe')
                except Exception as e:
                    logger.error(f"Stripe customer retrieve failed: {e}")
    except Exception as e:
        logger.error(f"[stripe webhook] handler error: {e}")
        # Still return 200 so Stripe does not retry indefinitely on our internal errors
    return {"received": True}


# ═══════════════ GÉNÉRATEUR DE CONTENU FACEBOOK (admin) ═══════════════
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
CONTENT_GCS_BUCKET = os.environ.get('CONTENT_GCS_BUCKET', 'testprojet-721cb-recipes')
GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'testprojet-721cb')
OPENAI_TEXT_MODEL = 'gpt-5.5'
OPENAI_IMAGE_MODEL = 'gpt-image-1.5'
CONTENT_PREFIX = 'content-photos'

CONTENT_THEMES = [
    {"day": "Lundi", "theme": "Mythe Keto"},
    {"day": "Mardi", "theme": "Choix impossible"},
    {"day": "Mercredi", "theme": "Astuce Naturo"},
    {"day": "Jeudi", "theme": "Question"},
    {"day": "Vendredi", "theme": "Conseil"},
    {"day": "Samedi", "theme": "Défi photo"},
    {"day": "Dimanche", "theme": "Motivation"},
]

BRAND_VOICE = (
    "Tu es le rédacteur de la page Facebook \"Essenciel O Naturel\", tenue par une naturopathe "
    "spécialisée en alimentation cétogène (keto) à Lunéville. Ton : chaleureux, bienveillant, expert "
    "mais accessible, tutoiement doux (\"tu\"), positif, jamais culpabilisant. Public : surtout des femmes "
    "35-60 ans qui veulent perdre du poids et retrouver de l'énergie sans frustration. Marque : couleurs "
    "vert forêt profond et or, symbole avocat, valeurs nature/santé/simplicité. Produits : une application "
    "\"Keto Premium\" (menus, recettes, suivi), des ebooks keto, et des consultations de naturopathie. "
    "Chaque publication doit être authentique, apporter de la valeur et inviter subtilement à interagir "
    "ou découvrir l'app/les consultations sans être trop commerciale."
)

BRAND_IMAGE_STYLE = (
    "Style photographique Keto — Essenciel O Naturel : palette vert forêt profond et touches dorées, "
    "ambiance naturopathe chaleureuse et lumineuse, aliments keto sains et appétissants (avocat, légumes "
    "verts, bons gras), végétaux frais, lin naturel et bois clair, lumière du jour douce, faible profondeur "
    "de champ, élégant et haut de gamme, style magazine. Aucun texte, aucun logo, aucune personne."
)


def _iso_week_id(d: datetime) -> str:
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _verify_admin(authorization: Optional[str]) -> str:
    """Vérifie le token Firebase et que l'email == admin. Renvoie l'email ou lève HTTPException."""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="no_token")
    token = authorization.split(' ', 1)[1]
    try:
        get_firestore()  # ensure firebase app is initialised
        decoded = firebase_auth.verify_id_token(token)
    except Exception as e:
        logging.getLogger(__name__).error(f"verify token: {e}")
        raise HTTPException(status_code=401, detail="invalid_token")
    email = (decoded.get('email') or '').strip().lower()
    if not email or email != (PREMIUM_ADMIN_EMAIL or '').strip().lower():
        raise HTTPException(status_code=403, detail="forbidden")
    return email


def _gcs_bucket():
    from google.cloud import storage
    cred_path = ROOT_DIR / FIREBASE_CREDENTIALS_PATH
    gcs = storage.Client.from_service_account_json(str(cred_path), project=GCP_PROJECT_ID)
    return gcs.bucket(CONTENT_GCS_BUCKET)


@api_router.post("/content/generate-text")
async def content_generate_text(request: Request, authorization: Optional[str] = Header(None)):
    _verify_admin(authorization)
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="no_openai_key")
    now = datetime.now(timezone.utc)
    week_id = _iso_week_id(now)
    calendar = " ; ".join([f"{t['day']} = {t['theme']}" for t in CONTENT_THEMES])
    user_msg = (
        f"Nous sommes la semaine {week_id}. Génère un plan de publications Facebook COMPLET et ORIGINAL "
        "pour les 7 jours de cette semaine (contenu inédit). Calendrier éditorial fixe : " + calendar + ". "
        "Pour CHAQUE jour, respecte son thème :\n"
        "- Mythe Keto : démonte une idée reçue sur le keto.\n"
        "- Choix impossible : un jeu \"tu préfères A ou B ?\" avec 2 options keto pour engager les commentaires.\n"
        "- Astuce Naturo : un conseil naturopathique concret.\n"
        "- Question : une question ouverte à la communauté.\n"
        "- Conseil : un conseil keto pratique et actionnable.\n"
        "- Défi photo : invite à poster une photo (assiette keto, etc.).\n"
        "- Motivation : un message inspirant et bienveillant.\n"
        "Réponds STRICTEMENT en JSON avec ce schéma : { \"days\": [ { \"day\": string, \"theme\": string, "
        "\"post\": string (publication Facebook prête, 3-6 phrases avec émojis et appel à l'action), "
        "\"story\": string (version courte percutante, 1-2 phrases), \"hashtags\": string[] (6 à 10 hashtags "
        "français avec le #), \"replies\": string[] (3 réponses types bienveillantes), \"image_prompt\": string "
        "(description en français d'un visuel carré illustrant le post, SANS texte), \"story_prompt\": string "
        "(description d'un visuel vertical pour la story, SANS texte) } ] }. "
        "Le tableau days doit contenir exactement 7 éléments, dans l'ordre Lundi->Dimanche."
    )
    payload = {
        "model": OPENAI_TEXT_MODEL,
        "messages": [
            {"role": "system", "content": BRAND_VOICE},
            {"role": "user", "content": user_msg},
        ],
        "response_format": {"type": "json_object"},
    }
    try:
        async with httpx.AsyncClient(timeout=180) as http:
            r = await http.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json=payload,
            )
        data = r.json()
        if r.status_code != 200:
            err = (data.get('error') or {}).get('message', f'HTTP {r.status_code}')
            code = (data.get('error') or {}).get('code', '')
            raise HTTPException(status_code=502, detail=f"openai: {code or err}")
        content = json.loads(data["choices"][0]["message"]["content"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"content_generate_text: {e}")
        raise HTTPException(status_code=500, detail=f"server_error: {e}")

    raw_days = content.get("days") if isinstance(content, dict) else None
    raw_days = raw_days if isinstance(raw_days, list) else []
    days = []
    for i, t in enumerate(CONTENT_THEMES):
        d = raw_days[i] if i < len(raw_days) and isinstance(raw_days[i], dict) else {}
        days.append({
            "day": t["day"],
            "theme": t["theme"],
            "post": d.get("post", ""),
            "story": d.get("story", ""),
            "hashtags": d.get("hashtags", []) if isinstance(d.get("hashtags"), list) else [],
            "replies": d.get("replies", []) if isinstance(d.get("replies"), list) else [],
            "image_prompt": d.get("image_prompt", ""),
            "story_prompt": d.get("story_prompt", ""),
            "square_url": None,
            "story_url": None,
        })
    result = {"weekId": week_id, "generatedAt": iso_now(), "days": days}
    # Sauvegarde dans Firestore (facultatif — n'échoue pas la requête si indispo)
    try:
        fs = get_firestore()
        if fs:
            fs.collection("generated_content").document(week_id).set(result, merge=True)
    except Exception as e:
        logger.error(f"content firestore save: {e}")
    return {"ok": True, "weekId": week_id, "content": result}


@api_router.post("/content/generate-image")
async def content_generate_image(payload: dict, authorization: Optional[str] = Header(None)):
    _verify_admin(authorization)
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="no_openai_key")
    week_id = str(payload.get("weekId", "")).strip()
    try:
        day_idx = int(payload.get("dayIdx"))
    except Exception:
        day_idx = -1
    kind = "story" if payload.get("kind") == "story" else "square"
    prompt = str(payload.get("prompt", "")).strip()
    if not week_id or day_idx < 0 or day_idx > 6 or not prompt:
        raise HTTPException(status_code=400, detail="bad_request")

    size = "1024x1536" if kind == "story" else "1024x1024"
    full_prompt = prompt + ". " + BRAND_IMAGE_STYLE
    try:
        async with httpx.AsyncClient(timeout=180) as http:
            r = await http.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": OPENAI_IMAGE_MODEL, "prompt": full_prompt, "size": size, "n": 1},
            )
        data = r.json()
        if r.status_code != 200:
            err = (data.get('error') or {}).get('message', f'HTTP {r.status_code}')
            code = (data.get('error') or {}).get('code', '')
            raise HTTPException(status_code=502, detail=f"openai: {code or err}")
        b64 = data["data"][0]["b64_json"]
        img_bytes = base64.b64decode(b64)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"content_generate_image openai: {e}")
        raise HTTPException(status_code=500, detail=f"server_error: {e}")

    filename = f"{CONTENT_PREFIX}/{week_id}/{day_idx}-{kind}.png"
    try:
        bucket = _gcs_bucket()
        blob = bucket.blob(filename)
        blob.cache_control = "public, max-age=86400"
        blob.upload_from_string(img_bytes, content_type="image/png")
        try:
            blob.make_public()
        except Exception:
            pass
        url = f"https://storage.googleapis.com/{CONTENT_GCS_BUCKET}/{filename}?v={int(now_ms())}"
    except Exception as e:
        logger.error(f"content_generate_image gcs: {e}")
        raise HTTPException(status_code=500, detail=f"storage_error: {e}")

    # Met à jour Firestore
    try:
        fs = get_firestore()
        if fs:
            ref = fs.collection("generated_content").document(week_id)
            snap = ref.get()
            if snap.exists:
                doc = snap.to_dict() or {}
                arr = doc.get("days") or []
                if 0 <= day_idx < len(arr):
                    arr[day_idx]["story_url" if kind == "story" else "square_url"] = url
                    ref.set({"days": arr}, merge=True)
    except Exception as e:
        logger.error(f"content image firestore: {e}")
    return {"ok": True, "url": url, "kind": kind, "dayIdx": day_idx}


def now_ms():
    return datetime.now(timezone.utc).timestamp() * 1000


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
