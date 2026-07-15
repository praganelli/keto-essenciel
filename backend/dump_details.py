"""Dump recipe_details Firestore collection to /tmp/recipe_details.json"""
import os, json
os.chdir('/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import server
fs = server.get_firestore()
if not fs:
    print("NO FIRESTORE")
    raise SystemExit(1)
docs = list(fs.collection('recipe_details').stream())
data = {}
for d in docs:
    v = d.to_dict() or {}
    if v.get('steps'):
        data[d.id] = {'steps': v['steps'], 'tip': v.get('tip', '')}
js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
open('/tmp/recipe_details.json', 'w', encoding='utf-8').write(js)
print("docs:", len(docs), "with steps:", len(data), "size KB:", len(js.encode('utf-8')) // 1024)
