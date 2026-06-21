import re, sys
from google.cloud import storage
SA="/app/backend/firebase_service_account.json"
BUCKET="testprojet-721cb-recipes"; PREFIX="recipe-photos/"
gcs=storage.Client.from_service_account_json(SA, project="testprojet-721cb")
keys=[]
for b in gcs.list_blobs(BUCKET, prefix=PREFIX):
    n=b.name[len(PREFIX):]
    if n.endswith(".jpg"): keys.append(n[:-4])
keys=sorted(set(keys))
arr=",".join('"'+k+'"' for k in keys)
new_block='var KP_RECIPE_PHOTOS = new Set(['+arr+']);'
for path in ["/app/keto.html","/app/backend/keto_app.html"]:
    s=open(path).read()
    s2=re.sub(r"/\* KP_RECIPE_PHOTOS_START \*/.*?/\* KP_RECIPE_PHOTOS_END \*/",
              "/* KP_RECIPE_PHOTOS_START */\n"+new_block+"\n/* KP_RECIPE_PHOTOS_END */",
              s, flags=re.S)
    open(path,"w").write(s2)
print("manifest updated:", len(keys), "photos")
