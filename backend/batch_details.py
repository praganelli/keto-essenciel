"""Génération en masse des préparations détaillées (ChatGPT) → Firestore recipe_details.
Usage : python batch_details.py  (logs dans /tmp/batch_details.log)"""
import json, os, time, threading, queue
import httpx
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
import server  # noqa: E402  (réutilise get_firestore, OPENAI_API_KEY, OPENAI_TEXT_MODEL)

LOG = open('/tmp/batch_details.log', 'a', buffering=1)

def log(msg):
    LOG.write(time.strftime('%H:%M:%S ') + msg + '\n')

fs = server.get_firestore()
assert fs, "Firestore indisponible"

recipes = json.load(open('/tmp/recipes_dump.json', encoding='utf-8'))
existing = {doc.id for doc in fs.collection('recipe_details').stream()}
todo = [r for r in recipes if str(r.get('id')) not in existing and r.get('name')]
log(f"total={len(recipes)} déjà détaillées={len(existing)} à générer={len(todo)}")

q = queue.Queue()
for r in todo:
    q.put(r)
done = 0
errors = 0
lock = threading.Lock()

SYSTEM = ("Tu es un chef cuisinier spécialisé en cuisine cétogène (keto), pédagogue et précis. "
          "Tu rédiges des préparations détaillées, claires et infaillibles, en français, au tutoiement doux.")

def gen(r):
    ing = "; ".join([str(i) for i in (r.get('ingredients') or []) if i]) or "(non précisés)"
    sp = ", ".join([str(s) for s in (r.get('spices') or []) if s]) or "(aucune)"
    cur = " | ".join([str(s) for s in (r.get('steps') or []) if s]) or "(aucune)"
    user_msg = (
        f"Recette : \"{r['name']}\".\nIngrédients : {ing}.\nÉpices/assaisonnements : {sp}.\n"
        f"Étapes actuelles (à enrichir) : {cur}.\n\n"
        "Rédige une PRÉPARATION DÉTAILLÉE, pas-à-pas, plus complète que les étapes actuelles. "
        "Chaque étape doit être une phrase actionnable et précise : indique les TEMPS de cuisson, "
        "les TEMPÉRATURES/feux, les repères visuels, les gestes techniques et 1-2 astuces de chef. "
        "Reste 100% cohérent avec les ingrédients fournis, ne rajoute pas d'ingrédient majeur. "
        "Réponds STRICTEMENT en JSON : { \"steps\": string[] (6 à 10 étapes détaillées, "
        "sans numérotation au début), \"tip\": string (une astuce de chef finale, courte) }."
    )
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {server.OPENAI_API_KEY}"},
        json={"model": server.OPENAI_TEXT_MODEL,
              "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_msg}],
              "response_format": {"type": "json_object"}},
        timeout=120,
    )
    data = resp.json()
    if resp.status_code != 200:
        raise RuntimeError((data.get('error') or {}).get('message', f'HTTP {resp.status_code}'))
    d = json.loads(data["choices"][0]["message"]["content"])
    steps = [str(s).strip() for s in (d.get("steps") or []) if str(s).strip()]
    if not steps:
        raise RuntimeError("réponse sans étapes")
    fs.collection('recipe_details').document(str(r['id'])).set({
        "name": r['name'], "steps": steps, "tip": (d.get("tip") or "").strip(),
        "generatedAt": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    })

def worker():
    global done, errors
    while True:
        try:
            r = q.get_nowait()
        except queue.Empty:
            return
        for attempt in (1, 2):
            try:
                gen(r)
                with lock:
                    done += 1
                    if done % 10 == 0:
                        log(f"progression : {done}/{len(todo)}")
                break
            except Exception as e:
                if attempt == 2:
                    with lock:
                        errors += 1
                    log(f"ERREUR id={r.get('id')} {r.get('name')}: {e}")
                else:
                    time.sleep(5)
        q.task_done()

threads = [threading.Thread(target=worker, daemon=True) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
log(f"TERMINÉ : {done} générées, {errors} erreurs")
