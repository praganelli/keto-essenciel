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
 # M7 — Perte de poids durable
 (6,0): "a friendly body silhouette with a storage vault door on the belly held by a hormone key, fat droplets waiting outside",
 (6,1): "a measuring tape wrapping gently around a waist, inner organs silhouette showing melting soft orange fat around them",
 (6,2): "a strong friendly muscle character with a bright steady flame inside, dumbbells and protein foods around",
 (6,3): "a bathroom scale showing a flat line graph plateau, a calm person shrugging while their waistline still shrinks",
 (6,4): "four friendly hormone messenger characters floating around a body silhouette: a key, a stop sign heart, a hungry stomach and a small storm cloud, balanced teamwork mood",
 (6,5): "a festive dinner table scene with a calm person choosing grilled meat and vegetables, walking shoes waiting by the door",
 (6,6): "a person lifting a rock on a path revealing small hidden icons underneath: a moon, a storm cloud, a chair, a soda glass and a cookie, discovery mood",
 (6,7): "a yo-yo toy transforming into a smooth steady horizontal line on a chart, a calm person holding the line gently, stability concept",
 (6,8): "a personal dashboard of gentle success icons: a measuring tape, a framed before-after photo silhouette, a glowing energy battery and a happy heart",
 (6,9): "a confident person standing at a sunny lookout point holding a simple one-page plan, a stable balanced scale and a small growing tree beside them",
 # M8 — Comprendre ses analyses biologiques (10 chapitres)
 (7,0): "a laboratory blood test tube with floating red blood cells and a small calendar, clean medical illustration",
 (7,1): "red blood cells with tiny sugar crystals sticking to them, a three-month calendar and a small film strip, average over time concept",
 (7,2): "a cute pancreas character next to a pressure gauge dial, small insulin droplets around, calm diagnostic mood",
 (7,3): "a friendly calculator character combining a blood drop and an insulin droplet, a small effort gauge above a pancreas character, early detection mood",
 (7,4): "two groups of round lipid particles in a blood vessel: big fluffy friendly golden ones and small dense grey ones",
 (7,5): "a body silhouette with a small flame inside the belly being soothed by water drops and fish omega oil droplets",
 (7,6): "a happy liver character and two kidney characters being examined with a magnifying glass, sparkling clean",
 (7,7): "two kidney characters filtering a gentle stream of water with tiny particles, a small filtration gauge and a protective shield nearby",
 (7,8): "a neat row of labeled test tubes with soft icons floating above: a sun, a B12 capsule, an iron ingot, a butterfly-shaped thyroid, curious discovery mood",
 (7,9): "an open notebook as a health dashboard with small gently descending charts, a person highlighting results and preparing questions for a doctor visit",
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
 # M9 — Stress, sommeil et équilibre glycémique (10 chapitres)
 (8,0): "a stressed person at a desk with storm cloud above, a gland releasing dots that raise a small liquid gauge",
 (8,1): "a small friendly adrenal gland character beside a day curve going from a morning peak to an evening valley, tiny cortisol dots raising a glucose gauge",
 (8,2): "a tired person carrying a heavy soft grey cloud as a backpack, gentle icons of an affected heart, belly and crescent moon around, compassionate tone",
 (8,3): "serene lungs illustration with slow air flow arrows, one short inhale wave and one long exhale wave, zen mood",
 (8,4): "a heart and lungs breathing in harmony, smooth synchronized sine waves flowing between them, teal and coral",
 (8,5): "a person meditating cross-legged with closed eyes, muscles relaxing shown as soft waves leaving the body",
 (8,6): "a sleeping person with gentle alternating sleep cycle waves floating above the bed, deep and light phases, a moon and a soft clock, educational calm",
 (8,7): "a peaceful bedtime scene: bed with moon and stars through window, phone face down on nightstand, herbal tea",
 (8,8): "a refreshed person stretching happily at sunrise by the window, a fully recharged battery and a calm smiling blood drop character nearby",
 (8,9): "a serene person assembling a personal wellbeing toolbox with soft icons: lungs, heart waves, a herbal tea cup, walking shoes and a crescent moon",
 # M10 — Les compléments alimentaires (10 chapitres)
 (9,0): "a doctor and patient discussing supplement bottles on a table, a protective shield above them, trust and caution",
 (9,1): "magnesium-rich foods (almonds, spinach, dark chocolate) beside omega-3 sources (sardines, salmon) and a fish-oil capsule",
 (9,2): "sardines, salmon fillet and walnuts arranged around golden fish-oil capsules, a friendly glowing heart character nearby",
 (9,3): "a bright sun shining on a happy person, a vitamin capsule glowing, broccoli and eggs on a table",
 (9,4): "a small shiny mineral crystal beside a glucose meter, broccoli, eggs and whole grains on a table, a soft floating question mark, balanced scientific tone",
 (9,5): "herbal supplement capsules with a berberine plant, cinnamon sticks and a mortar and pestle, apothecary style",
 (9,6): "cinnamon sticks and a small bowl of cinnamon powder under a magnifying glass, a gentle myth cloud dissolving into sparkles, curious honest mood",
 (9,7): "a friendly antioxidant shield character gently protecting glowing nerve endings of a foot silhouette, spinach and broccoli nearby",
 (9,8): "a magnifying glass examining a plain supplement bottle label with a green checkmark, a flashy exaggerated bottle faded in the background",
 (9,9): "a doctor and patient building a simple pyramid together: a colorful plate of whole foods at the base and a few capsules at the top, a plan sheet nearby",
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
 # M13 — BONUS : Le guide de survie Keto-Essenciel (12 chapitres)
 (12,0): "a relaxed person reading a restaurant menu at a candlelit table, a grilled fish plate with green vegetables glowing softly, waiter smiling in background",
 (12,1): "a sunny beach vacation scene with a person enjoying a fresh seafood platter under a parasol, sandals and a sunhat nearby, carefree healthy mood",
 (12,2): "a warm dinner party at a friend's home, a guest happily bringing a homemade salad bowl to the table, hosts welcoming with open arms",
 (12,3): "an elegant glass of dry red wine beside a glass of sparkling water with lime, a gentle glucose curve dipping in the background, moderation concept",
 (12,4): "a clock face where one half shows an empty plate and the other half a beautiful keto meal, gentle fasting window concept, calm balanced tone",
 (12,5): "small bowls of natural sweeteners: white erythritol crystals and green stevia leaves, a keto chocolate cake slice beside them, gentle kitchen light",
 (12,6): "a sporty person tying running shoes with a small snack of almonds and a water bottle beside them, a tiny glucose meter in the gym bag",
 (12,7): "an open travel bag packed with healthy snacks: nuts, hard cheese, dark chocolate squares and a sardine tin, a passport and plane ticket nearby",
 (12,8): "a confident shopper with a neat list gliding a cart through the fresh produce section, vegetables meat fish and eggs in the cart, bright market",
 (12,9): "a bunless burger served in a lettuce wrap with a side salad and a glass of water on a fast-food tray, smart choice concept",
 (12,10): "a joyful birthday party table where a guest savors a thin slice of cake slowly, balloons and candles, warm family celebration mood",
 (12,11): "a festive christmas dinner table with oysters, smoked salmon, roasted turkey and a cheese platter, elegant candles and pine branches, abundant and healthy",
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
 "m6c0b": "a seesaw balance with food on one side and activity icons on the other, a curious person examining it with floating hormone messenger dots around",
 "m6c0c": "three friendly messenger characters around a brain: a golden key, a stop-sign holding satiety character and a hungry little stomach character",
 "m6c0d": "a split plate comparison: grilled salmon with vegetables glowing steadily on one side, a soda and donut with a spiky crashing wave above on the other",
 "m6c1b": "a gentle cross-section of a body silhouette showing soft outer fat under the skin and deeper orange fat wrapped around inner organs, educational style",
 "m6c1c": "deep orange belly fat releasing small inflammatory sparks toward a worried liver character, a shield character standing protectively nearby",
 "m6c1d": "a happy person measuring their waist with a tape while a wall calendar shows weekly checkmarks, a downward gentle arrow of progress",
 "m6c2b": "a cozy body silhouette at rest with a warm steady flame in the chest, small icons of a beating heart, lungs and a glowing brain around",
 "m6c2c": "two different friendly people side by side with different sized inner flames, a dumbbell, a birthday cake and a DNA helix floating between them",
 "m6c2d": "a person joyfully taking stairs while another walks during a phone call, small sparkles of burned energy rising from their steps",
 "m6c3b": "a body silhouette adjusting a small energy dial downward while fat melts and a muscle grows, adaptation concept, calm mood",
 "m6c3c": "a magnifying glass comparing two charts: a short wavy fluctuation and a long flat plateau line, a measuring tape showing progress below",
 "m6c3d": "a toolbox opening with gentle tools: a magnifying glass over hidden sugar cubes, a fork on a clock, walking shoes, a moon pillow",
 "m6c4b": "a golden key character calming down next to an empty snack plate and a person walking after a meal, glucose dots entering a muscle",
 "m6c4c": "two characters on a seesaw: a sleepy satiety character with a stop sign and an eager hungry stomach character, a moon balancing them",
 "m6c4d": "a small storm cloud raining on a belly getting rounder, then a person breathing calmly under a clearing sky, before-after serenity",
 "m6c5b": "a calendar week of 21 small plates where only one plate is festive with a tiny party hat, the others green and balanced, perspective concept",
 "m6c5c": "a person gently letting go of a heavy guilt cloud and stepping forward onto three stepping stones toward a fresh balanced meal",
 "m6c5d": "a relaxed person at a festive table choosing grilled meat and vegetables, a sparkling water glass raised in a friendly toast",
 "m6c6b": "a tired person with a short-night moon icon and a storm cloud, reaching toward sweets, a caring alarm clock suggesting sleep",
 "m6c6c": "a person glued to an office chair with muscles shown asleep as little zzz, beside a hand grabbing invisible snacks from a jar absentmindedly",
 "m6c6d": "a lineup of drinks compared: a glowing water glass and herbal tea versus a juice, a cocktail and a whipped coffee with hidden sugar cubes",
 "m6c7b": "a yo-yo toy on a downward-then-upward weight curve, a tired person watching it bounce, restrictive empty plate nearby",
 "m6c7c": "a gentle bridge from a weight-loss slope to a flat stable plateau, a person walking calmly across holding their familiar healthy plate",
 "m6c7d": "a corridor of stability: a weight curve staying between two soft guardrails, a small alarm bell at the upper rail, a weekly calendar checkmark",
 "m6c8b": "a confused bathroom scale character juggling a fat droplet, a muscle, and a water drop, a person looking instead at a measuring tape",
 "m6c8c": "a monthly photo ritual: a person taking a mirror photo in the same outfit, two polaroid silhouettes side by side showing gentle progress",
 "m6c8d": "a joyful person climbing stairs energetically with a glowing battery, a well-fitting pair of jeans and a rising energy meter nearby",
 "m6c9b": "a person looking back proudly at a milestone path with icons: a measuring tape, a plate, walking shoes, a moon and a small trophy",
 "m6c9c": "a simple one-page plan pinned on a wall with three big habit circles, a stable scale zone drawing and a small alarm bell",
 "m6c9d": "a person shielding a small flame from wind with their hands while walking a long scenic path toward the horizon, perseverance mood",
 "m7c0b": "a gentle grid of four icons around a blood test tube: a magnifying glass, a rising chart, a pill being adjusted and a small trophy, purpose of testing concept",
 "m7c0c": "a friendly lab results sheet with small icons beside each line: a blood drop, a calendar, a butter knob, a liver, two kidneys and a tiny flame",
 "m7c0d": "two different laboratory buildings each holding a slightly different measuring ruler, a calm person comparing results within one folder over time",
 "m7c1b": "red blood cells traveling through a vessel with tiny sugar crystals gradually sticking to them, a 120-day calendar floating above",
 "m7c1c": "a gentle gauge with three zones from green to red, a doctor and patient setting a personalized target flag together on the dial",
 "m7c1d": "a three-month hourglass slowly dropping sand while a person walks, eats vegetables and sleeps, patience and steady progress mood",
 "m7c2b": "two small scenes: a sunrise fasting blood test on one side, a plate of food with a two-hour clock and a gentle glucose wave on the other",
 "m7c2c": "a golden key-shaped insulin character opening a round cell door while some doors stay closed, a hardworking pancreas character sweating gently",
 "m7c2d": "four small quadrant scenes combining a glucose gauge and an insulin gauge in different positions, one quadrant glowing as the silent early warning",
 "m7c3b": "a friendly calculator showing a simple formula with a blood drop and an insulin droplet as ingredients, a three-zone result dial below",
 "m7c3c": "a single snapshot photo frame beside a warning sign and a laboratory ruler, honest scientific caution mood, soft colors",
 "m7c3d": "a happy muscle character opening many small doors for glucose dots while a person walks after a meal, sensitivity restored concept",
 "m7c4b": "a soda bottle and pastries pouring tiny golden droplets into a river of blood, a gentle downward arrow appearing as vegetables replace them",
 "m7c4c": "two friendly delivery trucks in a blood vessel: one collecting fat droplets toward a liver, one delivering them outward, teamwork concept",
 "m7c4d": "a full lipid panel sheet viewed as a whole picture puzzle with pieces connecting: triglycerides, HDL, waist tape and a glucose drop",
 "m7c5b": "a gentle thermometer measuring a soft inner glow inside a body silhouette, three zones from cool green to warm red, calm medical tone",
 "m7c5c": "a circular arrow loop between an orange belly fat blob and small inflammation sparks, a pair of scissors gently cutting the loop",
 "m7c5d": "a soothing collage: colorful vegetables and fatty fish, a person sleeping, walking shoes and a calm breathing figure cooling a small flame",
 "m7c6b": "a friendly liver character as an orchestra conductor directing glucose dots, fat droplets and a small storage barrel, warm educational style",
 "m7c6c": "three small gauges labeled with tiny enzyme icons rising gently from a liver character, a magnifying glass checking them kindly",
 "m7c6d": "a happy liver character being pampered: vegetables and berries on one side, faded soda and pastries pushed away, a walking person nearby",
 "m7c7b": "two diligent kidney characters filtering a stream through fine sieves, a small creatinine particle gauge beside them",
 "m7c7c": "a filtration speedometer dial with gentle zones, two kidney characters proudly pointing at the needle in the green zone",
 "m7c7d": "a protective routine scene: a water glass, a blood pressure cuff, a glucose meter and a yearly calendar reminder around two happy kidneys",
 "m7c8b": "two small test tubes with icons: one with a crystal and a toe joint, one with a bright sun, gentle informative style",
 "m7c8c": "a relaxed muscle character with magnesium-rich foods beside an iron storage chest with a ferritin gauge, balanced discovery mood",
 "m7c8d": "a B12 capsule character shaking hands with a metformin pill character, a nerve ending glowing healthily behind them",
 "m7c9b": "constellation lines connecting small analysis icons in a night sky: a blood drop, a butter knob, a liver, a flame and a waist tape forming a clear pattern",
 "m7c9c": "a hand-drawn tracking table with dates and gently improving numbers, a highlighter marking a victory trend line",
 "m7c9d": "a prepared patient at a doctor consultation holding a neat folder and a list of three questions, both smiling over charts on the desk",
 "m8c0b": "two clouds over a person: a small quick white cloud passing by and a heavy long grey cloud settling, acute versus chronic concept",
 "m8c0c": "two messenger characters racing from a gland: a fast lightning courier and a slow steady hourglass courier, both nudging a glucose gauge upward",
 "m8c0d": "a person kindly observing their own reflection with a notebook, a soft heart symbol, no judgment, self-compassion mood",
 "m8c1b": "a sun rising over a small gland character stretching awake, a daily curve peaking at morning and settling into evening calm",
 "m8c1c": "a constantly lit red alarm lamp above a tired body silhouette showing a soft belly, a fragile shield and a rising glucose gauge",
 "m8c1d": "a morning light walk, a balanced plate, an evening dimmed lamp and a breathing figure arranged as a gentle daily cycle around a calm gland",
 "m8c2b": "a tired person reaching toward pastries while a drained battery blinks, a gentle loop arrow showing the craving cycle",
 "m8c2c": "three soft vignettes: a knotted stomach character, a muscle losing glucose dots to a storm cloud, and a person lying awake at night",
 "m8c2d": "a person stepping off a descending grey spiral onto a bright ascending path with tiny footsteps, hope and reversal concept",
 "m8c3b": "a calm brain connected to a slowing heart by a soft glowing nerve cable, a storm cloud dissolving above, physiological calm concept",
 "m8c3c": "two breathing patterns side by side: a belly rising under a resting hand, and a wave with a short inhale and a long slow exhale",
 "m8c3d": "a small daily planner with three tiny breathing session marks, a relaxed person practicing before a meal, no pressure mood",
 "m8c4b": "a heart drawing a perfectly smooth wave on a small screen while lungs breathe in rhythm, harmony and synchronization concept",
 "m8c4c": "a friendly clock showing 5 minutes, the number 6 as gentle breath waves and the number 3 as daily suns, method rhythm concept",
 "m8c4d": "a person peacefully practicing breathing at a desk with a soft glowing aura, a calendar with steady checkmarks building a habit",
 "m8c5b": "a person seated comfortably tensing then releasing a fist, soft tension waves leaving the arm as sparkles, progressive relief",
 "m8c5c": "a person anchored in the present moment surrounded by five gentle sense icons: an eye, an ear, a nose, a hand and lips",
 "m8c5d": "soft sound waves from a singing bowl washing over a relaxed listener with headphones, warm evening light",
 "m8c6b": "a night timeline as a gentle staircase cycling between deep blue valleys and light lavender hills, a moon travelling across",
 "m8c6c": "a sleeping person with a calm glucose gauge on the nightstand, and beside it a short-night version with a slightly raised gauge, comparison",
 "m8c6d": "three sleepers of different ages under one big blanket with small clocks showing slightly different durations, individual needs concept",
 "m8c7b": "a cozy evening path of small stepping stones: a dimmed lamp, a warm herbal tea, a book and a bed at the end, ritual concept",
 "m8c7c": "a phone emitting a cold blue glow being gently placed face down in a drawer, a melatonin moon character reappearing relieved",
 "m8c7d": "an ideal calm bedroom: cool thermometer, blackout curtains, tidy bed, and faded icons of coffee, wine and a heavy late plate outside the door",
 "m8c8b": "a magnifying glass over a night scene revealing small culprits: a coffee cup, a glowing screen, a worry cloud and a 3am clock",
 "m8c8c": "a person calmly getting up to read in an armchair under a dim lamp, leaving the bed without frustration, patience mood",
 "m8c8d": "a caring doctor listening to a tired patient, a sleep diary notebook on the desk, professional support and hope",
 "m8c9b": "a person filling a simple self-assessment sheet with three sliders: stress cloud, sleep moon and energy battery, honest check-in",
 "m8c9c": "a daily wheel with small habit icons around it: breathing waves, a walk, a tea cup, a dimmed lamp and a regular bedtime clock",
 "m8c9d": "a small growing plant being watered beside a weekly review checklist, one new habit sprouting at a time, sustainable growth mood",
 "m9c0b": "a balance scale comparing a certified medicine box with documents and stamps versus a plain supplement jar with a question mark",
 "m9c0c": "a decision path with green flags: a lab result sheet, an empty fish plate, a pill interacting icon, all leading to a doctor conversation",
 "m9c0d": "one single well-chosen supplement jar glowing softly while a cluttered pile of random colorful bottles fades in the background",
 "m9c1b": "a relaxed muscle and a calm nerve spark connected to a magnesium crystal, a small insulin key working smoothly nearby",
 "m9c1c": "a beautiful plate of magnesium-rich foods: almonds, spinach, pumpkin seeds, dark chocolate squares and a small bowl of legumes",
 "m9c1d": "a well-tolerated magnesium capsule beside a gentle stomach character giving a thumbs up, a kidney character watching carefully",
 "m9c2b": "three fish-shaped letters swimming in order from a flax seed toward a heart and a brain, conversion journey concept",
 "m9c2c": "a weekly calendar with two fish meals highlighted: grilled salmon and sardines on toast-free plates, walnuts and rapeseed oil nearby",
 "m9c2d": "a fish-oil capsule beside a blood drop character and an anticoagulant pill character politely keeping distance, caution concept",
 "m9c3b": "a sun character conducting three scenes: a strong bone, a shield with antibodies and a calm pancreas, multitasking vitamin concept",
 "m9c3c": "a person indoors behind a window on a grey winter day, the sun far away, a low vitamin gauge beside them, gentle explanation mood",
 "m9c3d": "a doctor holding a dosage dropper with a measured amount, a calendar with monthly marks, moderation and testing concept",
 "m9c4b": "a tiny chromium crystal helping an insulin key turn slightly better in a cell lock, small honest question marks around the scene",
 "m9c4c": "chromium food sources on a wooden board: broccoli, eggs, whole grains, green beans and a small piece of liver, natural first approach",
 "m9c4d": "a modest supplement jar with a clear measuring line and a doctor consultation bubble, no miracle promises, sober tone",
 "m9c5b": "a golden-root plant character gently slowing a sugar conveyor belt from the intestine and calming a liver character, plant power concept",
 "m9c5c": "a berberine capsule beside a sensitive stomach character and a metformin pill character raising a polite warning hand, interaction caution",
 "m9c5d": "a step-by-step path: a doctor checkmark, a single small capsule, a glucose diary and a three-month review flag, structured approach",
 "m9c6b": "two cinnamon sticks side by side: a thin pale delicate one glowing softly and a thick dark one with a small warning droplet, two varieties concept",
 "m9c6c": "a stack of research papers with gentle up and down arrows, a magnifying glass finding a small positive trend, nuanced science mood",
 "m9c6d": "a spoonful of cinnamon being sprinkled on plain yogurt with berries, a warm tea beside it, simple culinary pleasure",
 "m9c7b": "a shield character comfortable in both a water drop and an oil drop, catching sparks flying toward cells, universal antioxidant concept",
 "m9c7c": "a foot silhouette with nerve endings gently glowing back to life, a research paper stack and a doctor nodding thoughtfully beside it",
 "m9c7d": "an alpha-lipoic capsule beside a glucose meter showing a slightly lower value and a thyroid butterfly, watchful monitoring concept",
 "m9c8b": "a supplement label under a magnifying glass with highlighted zones: dosage line, ingredient list and a tiny additives corner",
 "m9c8c": "a plain trustworthy jar wearing small certification medals, a transparent factory and a batch number tag, quality assurance mood",
 "m9c8d": "a theatrical flashy bottle with fireworks and huge promises deflating like a balloon next to a calm honest jar, marketing traps concept",
 "m9c9b": "a personal map with a you-are-here pin surrounded by icons: a lab sheet, a plate, a pill organizer and a stethoscope, individual starting point",
 "m9c9c": "three capsules introduced one at a time on a monthly timeline, each followed by a small diary and a checkmark, sequenced method",
 "m9c9d": "a food pyramid with a colorful whole-food base, lifestyle icons in the middle and a tiny capsule at the very top, right priorities concept",
 "m12c0b": "a menu card being scanned by a friendly magnifying glass highlighting a grilled steak and vegetables, warning sparkles on breaded and glazed dishes",
 "m12c0c": "a beautiful side dish trio: sauteed green vegetables, a fresh salad and mushrooms, with a small sauce boat served apart on the side",
 "m12c0d": "a smiling customer politely talking to a friendly waiter, a speech bubble showing vegetables replacing fries, easy request mood",
 "m12c1b": "an open suitcase with almond packs, medicines in a pouch and a hotel breakfast plate of eggs cheese and ham in the background",
 "m12c1c": "a person calmly walking around a lavish buffet with an empty plate doing a scouting tour, one composed plate of proteins and vegetables at their table",
 "m12c1d": "a person coming home from vacation putting fresh groceries in the fridge, a calendar with a J+4 scale reminder, smooth restart mood",
 "m12c2b": "a guest arriving at a friends dinner holding a homemade cheese platter as a gift, hosts delighted at the door, warm evening light",
 "m12c2c": "an aperitif table split gently: olives cheese cubes charcuterie and raw vegetables glowing warmly, chips and crackers faded at the edge",
 "m12c2d": "a dessert moment at a family table: one guest enjoying a tiny slice of cake slowly while another sips coffee contentedly, no tension, love mood",
 "m12c3b": "a liver character busy processing a wine glass while a glucose reservoir waits blocked behind him, a clock showing late night, educational tone",
 "m12c3c": "a lineup of drinks with small sugar-cube stacks under each: none under dry wine and spirits, a tall stack under beer and a huge one under a cocktail",
 "m12c3d": "a person at a party holding a sparkling water with lime in a cocktail glass, a small '2 max' reminder note, relaxed social confidence",
 "m12c4b": "a 24-hour circular clock with a highlighted 8-hour eating window showing plates, and a calm moon over the fasting hours",
 "m12c4c": "a balanced signpost with benefits on one side (a key, a calm gauge) and warning signs on the other (a pregnant silhouette, a fragile person), nuanced tone",
 "m12c4d": "a doctor and patient reviewing a fasting plan together, an insulin pen and a glucose meter on the desk, safety first concept",
 "m12c5b": "three labeled families of sweeteners as gentle podiums: erythritol crystals and stevia leaves on top, maltitol with a warning sparkle below",
 "m12c5c": "myth clouds dissolving around a honey jar and a coconut sugar bag revealing sugar cubes hidden inside them, honest revelation mood",
 "m12c5d": "a keto chocolate cake being baked with a small measured spoon of erythritol, a palate character slowly learning to enjoy a strawberry as candy",
 "m12c6b": "a small pre-workout snack (almonds, a boiled egg, cheese) beside sport shoes, and a post-workout plate of chicken and vegetables with a clock",
 "m12c6c": "a runner pausing on a bench drinking water, a small warning kit beside them with sugar cubes, gentle safety awareness mood",
 "m12c6d": "three activity levels as gentle steps: a walker with just water, a cyclist with a small snack, a hiker with a full kit and glucose meter",
 "m12c7b": "a travel checklist on a fridge: meal before departure, snack pouch, medicines in double, a cool bag for insulin, tidy preparation mood",
 "m12c7c": "an airplane tray meal where the protein and vegetables glow warmly while the bread roll and dessert fade, a big water bottle beside",
 "m12c7d": "a traveler eating breakfast at local time under a bright morning sun, a small clock adjusting its hands, jet lag adaptation concept",
 "m12c8b": "a supermarket map from above showing a glowing path around the fresh periphery aisles, the center aisles shaded, smart route concept",
 "m12c8c": "a hand holding a product package flipped to the back label, a magnifying glass on the carbs line, the flashy front marketing ignored",
 "m12c8d": "a person shopping calmly with a list after eating almonds, tempting end-cap displays fading behind them, focused expert mood",
 "m12c9b": "a lettuce-wrapped burger with double steak beside a grilled chicken salad, a fast-food tray transformed into a smart meal",
 "m12c9c": "fast-food traps gently highlighted: a ketchup bottle with sugar cubes, a giant soda, a sundae, versus mustard and water glowing as allies",
 "m12c9d": "a person taking a pleasant walk right after leaving a fast-food restaurant, a glucose curve softening behind them, smart recovery concept",
 "m12c10b": "a festive buffet with a guest holding one beautifully composed plate of shrimp salmon cheese and crudites, chatting away from the table",
 "m12c10c": "a birthday cake with one thin slice being savored slowly with a fork, candles and happy blurred family in the background, guilt-free pleasure",
 "m12c10d": "the day after a party: a normal light dinner of soup and omelette, a big water glass, a scale with a friendly 'wait 4 days' note",
 "m12c11b": "an elegant french christmas table starring oysters, smoked salmon, foie gras and roasted poultry, the bread basket discreetly far away",
 "m12c11c": "a chocolate box stored high in a cupboard while two chosen dark chocolates rest on a small plate with coffee, mindful treat concept",
 "m12c11d": "a fresh january scene: a person writing one simple quarterly goal in a notebook, a normal breakfast of eggs and avocado, no crash diet, serene restart",
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
