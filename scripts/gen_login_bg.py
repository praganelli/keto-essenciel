import asyncio, os, io, base64, sys
from dotenv import load_dotenv
from PIL import Image
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv("/app/backend/.env")
API_KEY = os.getenv("EMERGENT_LLM_KEY")

PROMPT = (
    "Photographie d'ambiance en fort flou artistique (bokeh prononcé, defocus complet) : "
    "feuillage vert frais et lumineux en arrière-plan, avocats mûrs coupés en deux avec noyau "
    "posés sur une table en bois clair, tissu de lin vert sauge froissé, lumière naturelle douce "
    "et aérée du matin, tons vert tendre, sauge et crème, atmosphère fraîche et apaisante. "
    "TOUT est flou (aucune zone nette), style fond d'écran de téléphone, orientation verticale. "
    "Aucun texte, aucun logo, aucune personne, aucun objet net."
)

async def main(n):
    for i in range(n):
        chat = LlmChat(api_key=API_KEY, session_id=f"login-bg-{i}",
                       system_message="You generate beautiful photorealistic background photography.")
        chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(modalities=["image", "text"])
        text, images = await chat.send_message_multimodal_response(UserMessage(text=PROMPT))
        if not images:
            print("NO IMAGE", i, "|", (text or "")[:100]); continue
        raw = base64.b64decode(images[0]["data"])
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        print("got", i, im.size)
        im.save(f"/tmp/login_bg_{i}.png")

if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 2))
