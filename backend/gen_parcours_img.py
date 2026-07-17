#!/usr/bin/env python3
"""Génère les illustrations des 59 chapitres du Parcours (Formation Diabète)
via OpenAI gpt-image-1.5. Idempotent : saute les images déjà présentes.
Sortie : /app/backend/pc_img/m{module}c{chapitre}.jpg (640px, JPEG q80).
Usage : python3 gen_parcours_img.py [--only m0c0,m0c1]  |  log: stdout
"""
import asyncio, base64, io, os, sys
import httpx
from PIL import Image
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
API_KEY = os.environ.get('OPENAI_API_KEY', '')
MODEL = 'gpt-image-1.5'
OUT = os.path.join(os.path.dirname(__file__), 'pc_img')
os.makedirs(OUT, exist_ok=True)

STYLE = ("Soft flat vector illustration, gentle pastel palette (sage green, teal, cream, "
         "soft coral accents), rounded friendly shapes, educational health-and-nutrition "
         "cartoon style, clean plain warm cream background, subtle shadows. "
         "ABSOLUTELY NO text, no letters, no words, no numbers, no labels anywhere. Subject: ")

# (module, chapitre) -> sujet de l'illustration
SUBJECTS = {
 # M1 — Comprendre son diabète
 (0,0): "a friendly smartphone showing a green leaf and avocado icons, surrounded by fresh keto foods, welcoming and warm",
 (0,1): "a cute cartoon pancreas next to a large teal key unlocking a round smiling body cell, small glucose dots floating around",
 (0,2): "a rising curve made of small sugar cubes floating above a plate of pasta and bread, a worried blood drop character watching",
 (0,3): "a blood vessel cross-section with glucose dots stuck inside, a key that does not fit into a locked cell door",
 (0,4): "red blood cells with tiny sugar crystals sticking to them, next to a calendar and a magnifying glass",
 # M2 — Pourquoi le Keto ?
 (1,0): "a seesaw balance with bread, pasta and sugar on one side going down crossed by a soft red ribbon, green vegetables avocado and salmon rising on the other side",
 (1,1): "a friendly liver character transforming golden fat droplets into small glowing flame-shaped energy sparks feeding a happy brain",
 (1,2): "a happy brain character powered by small golden flames, an egg and an avocado nearby, myth clouds fading away",
 (1,3): "a collage of wellness icons: a heart, a slim waist with measuring tape, a happy liver, a downward arrow made of leaves",
 (1,4): "a protective shield with a stethoscope and a doctor silhouette, gentle warning atmosphere, caring medical tone",
 # M3 — Bien manger
 (2,0): "a beautiful basket overflowing with keto foods: avocado, eggs, salmon, broccoli, olive oil bottle, cheese, nuts",
 (2,1): "sugary foods (soda bottle, donut, baguette, candy) behind a soft translucent barrier, fresh vegetables in front, no harsh symbols",
 (2,2): "a magnifying glass examining the back of a plain food package, small sugar cubes hiding behind it",
 (2,3): "a shopping cart filled with fresh vegetables, eggs, fish and cheese, rolling through a bright market aisle",
 (2,4): "neatly organized glass meal-prep containers with colorful keto meals, a small clock and a calm kitchen scene",
 # M4 — Les menus
 (3,0): "a smartphone displaying a weekly meal planner grid with small plate icons, magic sparkles around it",
 (3,1): "two plates exchanging places with curved swap arrows between them, both filled with healthy keto food",
 (3,2): "zucchini spiral noodles on a plate next to a cauliflower shaped like rice grains, chef hat nearby",
 (3,3): "a tiny stack of sugar cubes on a kitchen scale next to a large abundant keto plate, balance concept",
 # M5 — Les recettes
 (4,0): "a sunny breakfast scene: fluffy omelette on a plate, avocado half, coffee cup, morning light through window",
 (4,1): "a generous lunch salad bowl with grilled chicken, avocado slices, boiled egg and olive oil drizzle",
 (4,2): "a cozy dinner plate with steamed salmon and green vegetables, a crescent moon and stars in the window",
 (4,3): "an elegant chocolate mousse in a glass with a raspberry on top, dark chocolate squares and almonds around",
 (4,4): "a small snack board with almonds, walnuts, cheese cubes, olives and two squares of dark chocolate",
 (4,5): "a batch cooking scene: big pot on stove, roasted chicken, trays of vegetables and stacked storage containers",
 # M6 — Perte de poids
 (5,0): "a friendly body silhouette with a storage vault door on the belly held by a hormone key, fat droplets waiting outside",
 (5,1): "a measuring tape wrapping gently around a waist, inner organs silhouette showing melting soft orange fat around them",
 (5,2): "a bathroom scale showing a flat line graph plateau, a calm person shrugging while their waistline still shrinks",
 (5,3): "a strong friendly muscle character with a bright steady flame inside, dumbbells and protein foods around",
 (5,4): "a festive dinner table scene with a calm person choosing grilled meat and vegetables, walking shoes waiting by the door",
 # M7 — Comprendre ses analyses
 (6,0): "a laboratory blood test tube with floating red blood cells and a small calendar, clean medical illustration",
 (6,1): "two groups of round lipid particles in a blood vessel: big fluffy friendly golden ones and small dense grey ones",
 (6,2): "a cute pancreas character next to a pressure gauge dial, small insulin droplets around, calm diagnostic mood",
 (6,3): "a body silhouette with a small flame inside the belly being soothed by water drops and fish omega oil droplets",
 (6,4): "a happy liver character and two kidney characters being examined with a magnifying glass, sparkling clean",
 # M8 — Activité physique
 (7,0): "a smiling muscle cell opening wide doors to let glucose dots flow in from a blood vessel, no key needed",
 (7,1): "a happy person walking briskly in a park after a meal, sun setting, footsteps trail behind",
 (7,2): "a person doing squats at home in the living room using a chair, water bottle and yoga mat nearby",
 (7,3): "a person holding a solid forearm plank position on a mat, straight aligned body, focused and calm",
 (7,4): "a relaxed person stretching gently in the evening, soft lamp light, calm cozy room",
 # M9 — Stress et sommeil
 (8,0): "a stressed person at a desk with storm cloud above, a gland releasing dots that raise a small liquid gauge",
 (8,1): "serene lungs illustration with slow air flow arrows, one short inhale wave and one long exhale wave, zen mood",
 (8,2): "a person meditating cross-legged with closed eyes, muscles relaxing shown as soft waves leaving the body",
 (8,3): "a heart and lungs breathing in harmony, smooth synchronized sine waves flowing between them, teal and coral",
 (8,4): "a peaceful bedtime scene: bed with moon and stars through window, phone face down on nightstand, herbal tea",
 # M10 — Compléments
 (9,0): "magnesium-rich foods (almonds, spinach, dark chocolate) beside omega-3 sources (sardines, salmon) and a fish-oil capsule",
 (9,1): "a bright sun shining on a happy person, a vitamin capsule glowing, broccoli and eggs on a table",
 (9,2): "herbal supplement capsules with a berberine plant, cinnamon sticks and a mortar and pestle, apothecary style",
 (9,3): "a doctor and patient discussing supplement bottles on a table, a protective shield above them, trust and caution",
 # M11 — Les traitements
 (10,0): "a friendly liver character gently slowed by a round white pill, glucose dots decreasing, calm medical scene",
 (10,1): "an insulin pen and a glucose meter with a small blood drop character, caring safe atmosphere",
 (10,2): "an injection pen next to a calm stomach character and a satisfied brain, appetite dial turned low",
 (10,3): "two kidney characters filtering glucose dots out through a small stream of water, protective heart nearby",
 (10,4): "a doctor and patient shaking hands as a team over a table with charts and a pill organizer, warm trust",
 # M12 — Le suivi
 (11,0): "a bathroom scale and a measuring tape with a small weekly calendar, morning light, tidy bathroom",
 (11,1): "a glucose meter with a fingertip blood drop test, a phone logging a smooth curve, daily routine feel",
 (11,2): "a quarterly calendar with a blood test tube and a slowly descending smooth curve, hopeful progress mood",
 (11,3): "an archery target with an arrow in the center, small stepping stones leading to it, goal-setting concept",
 (11,4): "a joyful person raising arms on top of a small hill at sunrise, a golden trophy and confetti, celebration",
}

# Images supplémentaires (pages internes de chapitres) : nom de fichier -> sujet
EXTRAS = {
 "m3c0b": "a friendly person silhouette in the center surrounded by floating soft icons: a small birthday cake, a vertical height ruler, a bathroom scale and a pair of walking shoes, personal profile setup concept",
 "m3c0c": "a wooden signpost with four gentle curved paths leading to: a slimmer happy silhouette, a balanced scale in equilibrium, a calm smiling blood drop, and a glowing full energy battery",
 "m3c0d": "a large dinner plate seen from above divided into three zones: golden olive oil avocado salmon and nuts, a piece of meat with eggs and tofu, and fresh green leafy vegetables, harmony and balance",
 "m3c0e": "two different people standing side by side: a tall larger older man and a smaller athletic sporty woman, each with a different sized plate of healthy food floating in front of them, comparison concept",
 "m3c0f": "a happy person drinking a big glass of fresh water, water droplets and tiny sparkling mineral crystals floating around, light fresh hydration mood",
 "m4c0": "a bright welcoming home kitchen with neatly organized fresh keto ingredients on the counter: olive oil bottle, eggs, avocado, vegetables, cheese, a pan hanging, cozy and tidy",
 "m4c0b": "an open pantry cupboard with olive oil, butter, ghee jar, avocado oil and a colorful row of small spice jars with herbs, cozy organized shelves",
 "m4c0c": "an open refrigerator drawer scene with fresh broccoli, zucchini, spinach, peppers, mushrooms on one side and chicken, salmon, eggs, cheese on the other side",
 "m4c0d": "essential kitchen tools neatly arranged: a frying pan, a chef knife, a wooden cutting board, a saucepan, a baking dish, a small kitchen scale and glass storage boxes",
 "m4c0e": "four cooking methods in a gentle grid: a sizzling frying pan, a warm oven with a tray, an air fryer, and a simmering pot with steam, cozy kitchen mood",
 "m4c1b": "a croissant, white bread, sugary cereal bowl and orange juice glass on a table, with a rising then crashing wavy curve floating above them, a tired sleepy person slumped nearby",
 "m4c1c": "three gentle pillars or podiums: one holding eggs cheese and smoked salmon, one holding an avocado butter and olive oil bottle, one holding tomatoes cucumber and spinach leaves",
 "m4c1d": "a beautiful breakfast spread seen from above: a plate with fried eggs avocado and cherry tomatoes, a nordic plate with smoked salmon and cream cheese, and a small glass of greek yogurt with chia seeds and berries",
 "m4c1e": "a steaming coffee cup, a teapot with a cup of tea and a large glass of water glowing warmly, while a soda can and orange juice box sit far away faded in the background",
 "m4c2b": "a dinner plate seen from above divided in three parts: half filled with colorful low-carb vegetables, a quarter with grilled chicken and fish, a quarter with avocado slices olive oil and cheese",
 "m4c2d": "a vibrant keto plate with three distinct colors: green broccoli and salad, red bell peppers and tomatoes, white cauliflower with grilled fish, artistic and appetizing composition",
}

async def gen_one(client, sem, fname, subject):
    fname = fname + ".jpg"
    path = os.path.join(OUT, fname)
    if os.path.exists(path):
        print(f"SKIP {fname} (existe)", flush=True)
        return True
    async with sem:
        for attempt in range(3):
            try:
                r = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json={"model": MODEL, "prompt": STYLE + subject, "size": "1024x1024",
                          "quality": "medium", "n": 1},
                )
                data = r.json()
                if r.status_code != 200:
                    msg = (data.get('error') or {}).get('message', f'HTTP {r.status_code}')
                    print(f"ERR {fname} try{attempt+1}: {msg}", flush=True)
                    await asyncio.sleep(15)
                    continue
                img_bytes = base64.b64decode(data["data"][0]["b64_json"])
                im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                im.thumbnail((640, 640), Image.LANCZOS)
                im.save(path, "JPEG", quality=80, optimize=True)
                print(f"OK {fname} ({os.path.getsize(path)//1024} Ko)", flush=True)
                return True
            except Exception as e:
                print(f"EXC {fname} try{attempt+1}: {e}", flush=True)
                await asyncio.sleep(15)
    print(f"FAIL {fname}", flush=True)
    return False

async def main():
    if not API_KEY:
        print("ERREUR: OPENAI_API_KEY manquante"); sys.exit(1)
    only = None
    if len(sys.argv) > 2 and sys.argv[1] == '--only':
        only = set(sys.argv[2].split(','))
    pairs = [(f"m{k[0]}c{k[1]}", v) for k, v in SUBJECTS.items()]
    pairs += list(EXTRAS.items())
    items = [(n, s) for n, s in pairs if only is None or n in only]
    sem = asyncio.Semaphore(1)
    async with httpx.AsyncClient(timeout=240) as client:
        res = await asyncio.gather(*[gen_one(client, sem, n, s) for n, s in items])
    ok = sum(1 for x in res if x)
    print(f"TERMINÉ : {ok}/{len(items)} images", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
