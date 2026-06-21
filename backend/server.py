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
from firebase_admin import credentials, firestore


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
