import asyncio, time, os
from playwright.async_api import async_playwright

APP="http://localhost:8001/api/app"
TS=int(time.time())
EMAIL=f"verif.{TS}@gmail.com"; PWD="DemoKeto2026!"

async def main():
    errors=[]; failed=[]; stale=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        ctx=await b.new_context(viewport={"width":430,"height":932})
        pg=await ctx.new_page()
        pg.on("console", lambda m: errors.append(m.text[:160]) if m.type=="error" else None)
        def on_resp(r):
            try:
                if r.status>=400: failed.append(f"{r.status} {r.url[:90]}")
                if "menu-responder" in r.url: stale.append(r.url[:90])
            except: pass
        pg.on("response", on_resp)
        await pg.goto(APP, wait_until="domcontentloaded")
        await pg.wait_for_selector('[data-testid="welcome-cta-signup"]',timeout=30000)
        await pg.wait_for_timeout(1200)
        await pg.click('[data-testid="welcome-cta-signup"]')
        await pg.wait_for_selector('[data-testid="auth-tab-register"]',timeout=15000,state="visible")
        await pg.click('[data-testid="auth-tab-register"]'); await pg.wait_for_timeout(500)
        await pg.fill('#regFirstname','Test'); await pg.fill('#regLastname','Perf'); await pg.fill('#regEmail',EMAIL)
        await pg.click('[data-testid="reg-step1-next"]')
        await pg.wait_for_selector('#regPassword',timeout=10000,state="visible")
        await pg.fill('#regPassword',PWD); await pg.fill('#regPassword2',PWD)
        await pg.click('[data-testid="reg-step2-next"]')
        await pg.wait_for_selector('#btnRegister',timeout=10000,state="visible")
        await pg.click('#btnRegister')
        await pg.wait_for_timeout(5000)
        await pg.evaluate("()=>{try{if(typeof obFinish==='function')obFinish();}catch(e){}}")
        await pg.wait_for_timeout(4000)
        await pg.evaluate("()=>{try{generateMenu();}catch(e){}}")
        await pg.wait_for_timeout(3000)
        await pg.evaluate("window.switchTab && window.switchTab('library')")
        await pg.wait_for_timeout(3500)
        cards=await pg.evaluate("()=>document.querySelectorAll('.lib-card').length")
        emojis=await pg.evaluate("()=>document.querySelectorAll('.lib-card-emoji-icon').length")
        imgs=await pg.evaluate("()=>document.querySelectorAll('.lib-card-emoji-photo').length")
        await b.close()
        print("lib-card count:",cards,"| emoji icons:",emojis,"| leftover photo <img>:",imgs)
        print("console errors:",len(errors))
        for e in errors[:8]: print("  ERR:",e)
        print("failed requests (>=400):",len(failed))
        for f in failed[:8]: print("  FAIL:",f)
        print("stale menu-responder requests:",len(stale))
        for s in stale[:5]: print("  STALE:",s)
asyncio.run(main())
