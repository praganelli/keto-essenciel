import asyncio, json
from playwright.async_api import async_playwright
APP="http://localhost:8001/api/app"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        pg=await (await b.new_context()).new_page()
        await pg.goto(APP, wait_until="domcontentloaded")
        await pg.wait_for_function("typeof BFAST_RECIPES !== 'undefined' && typeof MAIN_RECIPES !== 'undefined'", timeout=30000)
        data=await pg.evaluate("""() => {
            const cats={breakfast:BFAST_RECIPES,main:MAIN_RECIPES,starter:STARTER_RECIPES,dessert:DESSERT_RECIPES,sauces:SAUCE_RECIPES,snacks:SNACK_RECIPES};
            const out=[];
            for(const k in cats){ (cats[k]||[]).forEach(r=>{
                out.push({cat:r.cat||k,id:r.id,name:r.name,desc:r.desc||'',
                  ingredients:(r.ingredients||[]).map(i=>i.name).slice(0,5)});
            });}
            return out;
        }""")
        await b.close()
        open("/app/scripts/recipes.json","w").write(json.dumps(data,ensure_ascii=False,indent=1))
        from collections import Counter
        c=Counter(r["cat"] for r in data)
        print("total recipes:",len(data),"| by cat:",dict(c))
asyncio.run(main())
