import asyncio, os, io, json, base64, sys
from dotenv import load_dotenv
from PIL import Image
from google.cloud import storage
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv("/app/backend/.env")
API_KEY = os.getenv("EMERGENT_LLM_KEY")
BUCKET = "testprojet-721cb-recipes"
PREFIX = "recipe-photos"
SA = "/app/backend/firebase_service_account.json"

gcs = storage.Client.from_service_account_json(SA, project="testprojet-721cb")
bucket = gcs.bucket(BUCKET)

CAT_FR = {"breakfast":"petit-déjeuner","main":"plat principal","starter":"entrée",
          "dessert":"dessert","sauces":"sauce","snacks":"collation"}

def build_prompt(r):
    ings = ", ".join(r.get("ingredients", [])[:5])
    catfr = CAT_FR.get(r["cat"], "plat")
    return (
        f"Photographie culinaire professionnelle, vue en plongée (top-down), d'un plat keto : "
        f"\"{r['name']}\" ({catfr}). {r.get('desc','')} "
        f"Ingrédients principaux : {ings}. "
        f"Dressé sur une belle assiette en céramique rustique, fond bois clair ou lin naturel, "
        f"lumière du jour douce et chaleureuse, faible profondeur de champ, garniture d'herbes fraîches, "
        f"tons terreux et appétissants, ultra réaliste, haute qualité, style magazine gastronomique. "
        f"Sans texte, sans logo, sans personne, sans couverts en gros plan."
    )

async def gen_one(r):
    key = f"{r['cat']}-{r['id']}"
    blob = bucket.blob(f"{PREFIX}/{key}.jpg")
    if blob.exists():
        print("skip (exists)", key); return True
    try:
        chat = LlmChat(api_key=API_KEY, session_id=f"recipe-{key}",
                       system_message="You generate appetizing photorealistic food photography.")
        chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(modalities=["image","text"])
        msg = UserMessage(text=build_prompt(r))
        text, images = await chat.send_message_multimodal_response(msg)
        if not images:
            print("NO IMAGE", key, "| text:", (text or "")[:80]); return False
        raw = base64.b64decode(images[0]["data"])
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        # center-crop square then resize 640
        w,h = im.size; s=min(w,h)
        im = im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((640,640))
        out = io.BytesIO(); im.save(out, "JPEG", quality=85); out.seek(0)
        blob.upload_from_file(out, content_type="image/jpeg")
        print("OK", key, "->", f"https://storage.googleapis.com/{BUCKET}/{PREFIX}/{key}.jpg")
        return True
    except Exception as e:
        print("ERR", key, str(e)[:120]); return False

async def main(pairs):
    recipes = json.load(open("/app/scripts/recipes.json"))
    by = {(r["cat"], r["id"]): r for r in recipes}
    todo = [by[p] for p in pairs if p in by]
    print(f"generating {len(todo)} images...")
    ok=0
    sem=asyncio.Semaphore(3)
    async def run(r):
        nonlocal ok
        async with sem:
            if await gen_one(r): ok+=1
    await asyncio.gather(*[run(r) for r in todo])
    print(f"DONE {ok}/{len(todo)}")

if __name__ == "__main__":
    import os as _os
    arg = sys.argv[1] if len(sys.argv) > 1 else "test"
    if arg == "test":
        PAIRS = [("breakfast",0),("breakfast",1),("main",300),("main",301),
                 ("starter",400),("dessert",500),("snacks",200),("sauces",100)]
    elif arg == "all":
        _r = json.load(open("/app/scripts/recipes.json"))
        PAIRS = [(x["cat"], x["id"]) for x in _r]
    else:
        PAIRS = []
    asyncio.run(main(PAIRS))
    _os._exit(0)
