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
 (6,0): "a friendly body silhouette with a storage vault door on the belly held by a hormone key, fat droplets waiting outside",
 (6,1): "a measuring tape wrapping gently around a waist, inner organs silhouette showing melting soft orange fat around them",
 (6,2): "a bathroom scale showing a flat line graph plateau, a calm person shrugging while their waistline still shrinks",
 (6,3): "a strong friendly muscle character with a bright steady flame inside, dumbbells and protein foods around",
 (6,4): "a festive dinner table scene with a calm person choosing grilled meat and vegetables, walking shoes waiting by the door",
 # M7 — Comprendre ses analyses
 (7,0): "a laboratory blood test tube with floating red blood cells and a small calendar, clean medical illustration",
 (7,1): "two groups of round lipid particles in a blood vessel: big fluffy friendly golden ones and small dense grey ones",
 (7,2): "a cute pancreas character next to a pressure gauge dial, small insulin droplets around, calm diagnostic mood",
 (7,3): "a body silhouette with a small flame inside the belly being soothed by water drops and fish omega oil droplets",
 (7,4): "a happy liver character and two kidney characters being examined with a magnifying glass, sparkling clean",
 # M8 — Activité physique
 (5,1): "a happy person walking briskly in a park after a meal, sun setting, footsteps trail behind",
 (5,2): "a person doing squats at home in the living room using a chair, water bottle and yoga mat nearby",
 (5,3): "a person sleeping peacefully in a cozy bed under a soft blanket, crescent moon and stars through the window, gentle floating sparkles, calm restorative night mood",
 (5,4): "a calm person breathing deeply with eyes closed and one hand on chest, a small storm cloud dissolving into soft green leaves above their head, serene mood",
 (5,5): "a happy person drinking a large glass of fresh water in a bright kitchen, a water carafe and a herbal tea cup nearby, sparkling droplets floating",
 (5,6): "a relaxed person calmly looking at a gently rising progress curve in a notebook, a measuring tape and a bathroom scale nearby, confident serene mood",
 (5,7): "a person happily walking on a path of stepping stones towards a sunrise, a small calendar with checkmarks floating nearby, steady progress mood",
 (5,8): "a person holding a magnifying glass in front of dissolving myth clouds, a bright lightbulb shining above, discerning truth mood",
 (5,9): "a serene person walking a gentle path through a green landscape dotted with icons: walking shoes, a bed, a water glass, a heart and a small chart, sunrise ahead",
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
 "m4c3b": "a thoughtful person pausing in front of an open refrigerator at evening, one hand on chin, a soft thought bubble with a question mark above their head",
 "m4c3c": "simple keto snacks neatly arranged on a small board: a boiled egg cut in half, cheese cubes, cucumber and celery sticks with cream cheese dip, avocado slices, olives and sardines",
 "m4c3d": "a large glass of fresh water in the foreground with a small clock beside it, faded processed snack bars and cookies pushed far in the blurry background",
 "m4c4b": "keto baking ingredients arranged on a kitchen counter: eggs, butter, a jug of cream, mascarpone jar, shredded coconut bowl, almond flour sack, dark chocolate bar and a few raspberries",
 "m4c4c": "an elegant spread of keto desserts: a chocolate mousse in a glass, almond muffins, greek yogurt with red berries, a vanilla coconut cream and a mini cheesecake",
 "m4c4d": "a warm cup of fragrant tea with steam and a single square of dark chocolate on a small plate, cozy comforting evening mood",
 "m4c5b": "a calm sunday kitchen prep scene: a weekly menu planner sheet, a shopping list, a clean counter and a stack of empty glass containers ready to be filled",
 "m4c5c": "batch cooked food portions on a counter: grilled chicken pieces, a tray of roasted broccoli zucchini and peppers, a bowl of boiled eggs and a jar of homemade vinaigrette",
 "m4c5d": "an open refrigerator with neatly stacked labeled glass containers of prepared meals, small date labels, and a freezer drawer with individual portions",
 "m4c6": "a wallet and a few coins next to a generous basket of affordable keto foods: eggs, canned sardines, chicken legs, cheese and seasonal vegetables, smart budget mood",
 "m4c6b": "budget-friendly whole foods on a market stall: a tray of eggs, chicken legs, ground meat, canned sardines, cheese wedge, seasonal green vegetables and a bag of frozen vegetables",
 "m4c6c": "a person comparing prices in a grocery aisle holding a shopping list, a small price tag per kilo visible as a blank tag, cart with simple whole foods",
 "m4c6d": "a homemade simple keto meal glowing warmly on one side, and on the other side faded expensive packaged products with blank flashy labels, comparison concept",
 "m4c7": "a happy couple dining at a cozy restaurant table with grilled fish, green salad and sparkling water, warm evening ambiance, waiter in the background",
 "m4c7b": "a joyful multigenerational family sharing a convivial meal around a big table, one plate in focus with grilled meat and colorful vegetables, warm celebration mood",
 "m4c7c": "a travel scene: an open cooler bag with boiled eggs, cheese portions, olives, vegetable sticks and a canned sardine tin, a road and suitcase in the background",
 "m4c7d": "a relaxed person at home browsing a restaurant menu on a smartphone, small dish icons floating above the screen, calm anticipation mood",
 "m4c8": "a person calmly walking on a winding path with small gentle obstacles, stepping over them confidently, a bright horizon ahead, learning journey concept",
 "m4c8b": "a split scene: a rushed stressed person running with a clock, versus a calm person walking steadily on stepping stones, with a plate of grilled chicken and eggs glowing nearby",
 "m4c8c": "a colorful portion of green vegetables glowing warmly next to faded packaged snack bars and cookies pushed to the side, whole foods winning concept",
 "m4c8d": "a person drinking a big glass of water with a small droplet trail, and behind them a fallen plate being gently picked back up, resilience and fresh restart mood",
 "m4c9": "a confident happy home cook wearing an apron in a bright kitchen, freely composing a plate with grilled chicken, green vegetables and avocado, no cookbook, creative freedom mood",
 "m4c9b": "three numbered-free steps shown as a gentle visual flow: a raw chicken fillet and eggs, then fresh green vegetables being added to a plate, then a drizzle of olive oil and avocado finishing the dish",
 "m4c9c": "cooking swaps illustration: grated cauliflower in a bowl next to rice fading away, zucchini spirals next to fading pasta, and a keto pizza with a golden almond crust",
 "m4c9d": "a curious cook joyfully smelling fresh herbs at a market stall with colorful new vegetables and spice jars around, discovery and pleasure mood",
 "m5c0": "a smiling middle-aged person walking energetically in a sunny park, light glowing around them, small floating icons of a heart and a droplet, vitality and fresh energy mood",
 "m5c0c": "a joyful grid of everyday activities: a person walking, someone gardening, a person riding a bicycle, someone climbing stairs and a person dancing at home",
 "m5c0d": "a person taking a small first step on a gentle ascending path of stepping stones, a friendly doctor giving a thumbs up nearby, encouraging safe start mood",
 "m5c1b": "a gentle split scene: on one side a person cycling and another swimming, on the other side a person doing squats from a chair holding water bottles as weights, an elastic band nearby",
 "m5c1c": "a serene person doing yoga stretching at sunrise next to an elderly person practicing tai-chi, and a weekly calendar with small activity dots spread across the days",
 "m5c1d": "a happy person choosing joyfully among floating activity bubbles: dancing, walking, swimming, gardening, cycling, with a water bottle and good sneakers at their feet",
 "m5c2b": "a friendly strong muscle character catching small glucose dots with open arms, surrounded by soft icons of a bone, a balance scale and shopping bags being carried easily",
 "m5c2c": "a cozy living room home workout: a person rising from a chair, another doing push-ups against a wall, a green elastic band and two water bottles used as dumbbells on the floor",
 "m5c2d": "a weekly calendar with two highlighted training days and rest days between them, a person gently warming up their shoulders beside it, calm and safe mood",
 "m5c3b": "a peaceful sleeping person with soft glowing icons floating above the bed: a gently repairing heart, a calm smiling blood drop, a recharging battery and a small clock showing a full night, restful mood",
 "m5c3c": "a calm evening bedroom scene: a phone placed face down on a nightstand, an open book, a cup of herbal tea, a dim warm lamp and a crescent moon through a slightly open window",
 "m5c3d": "a cozy three-step evening ritual connected by a soft dotted path towards a bed: a steaming herbal infusion cup, an open book with reading glasses, and a person breathing deeply with closed eyes",
 "m5c4b": "a small gland releasing tiny dots that gently raise a round glucose gauge, a slightly worried blood drop character watching, soft educational style",
 "m5c4c": "a person sitting comfortably practicing slow breathing, a gentle symmetric wave pattern flowing in and out beside them, a calm heart shape nearby",
 "m5c4d": "a soft collage of relaxing moments: a person walking among trees, two friends sharing herbal tea, a person reading under a lamp, green plants around",
 "m5c5b": "a friendly water droplet character helping a body silhouette: two kidneys being gently rinsed, blood flowing smoothly in a vessel, a small gauge calming down",
 "m5c5c": "a wilted plant and a tired person holding their forehead next to an empty glass, then the same plant revived and the person smiling beside a full water glass",
 "m5c5d": "a pleasant daily hydration set: a graduated water bottle, a glass of water on a meal table, a cup of herbal tea and a bowl of clear broth",
 "m5c6b": "a gentle dashboard of health icons: a bathroom scale, a measuring tape around a waist, a glucose meter, a charged battery and walking shoes",
 "m5c6c": "a wavy line chart going up and down but gently trending downward overall, a calm smiling person shrugging kindly at one small daily spike",
 "m5c6d": "a smartphone showing a simple wellness tracking screen with a smooth curve and a round score ring, a weekly calendar with one highlighted day beside it",
 "m5c7b": "a battery gauge slowly going from full to half while a small steady flame keeps burning next to a repeating calendar, perseverance concept",
 "m5c7c": "three connected stepping stones forming a loop: an alarm clock, a person doing a tiny simple action, and a small glowing reward star, habit loop concept",
 "m5c7d": "a person celebrating a small victory with soft confetti next to a jar filling with golden tokens, a friend applauding gently in the background",
 "m5c8b": "myth clouds being gently blown away from a friendly pancreas character and a smiling blood drop, a bright warm sun appearing behind them",
 "m5c8c": "an elderly person and a younger person walking happily together in a park, a dark cloud dissolving behind them, encouraging safe exercise mood",
 "m5c8d": "a magnifying glass examining floating foods: a glowing avocado and olive oil bottle on one side, a dull suspicious packaged snack on the other",
 "m5c9b": "a person looking back at a beautiful path of milestone stones decorated with small icons: shoes, a dumbbell, a moon, a leaf, a water drop and a chart",
 "m5c9c": "a person writing a simple plan in a notebook with three big priority circles, a weekly planner and a small compass on the table",
 "m5c9d": "a person watering a small growing tree, gentle moon phases passing above, a supportive doctor and a friend standing warmly nearby",
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
