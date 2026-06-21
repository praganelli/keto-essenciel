import asyncio, time, os
from playwright.async_api import async_playwright
APP="http://localhost:8001/api/app-preview"
OUT="/app/promo_raw"; os.makedirs(OUT,exist_ok=True)
TS=int(time.time()); PWD="DemoKeto2026!"; E=f"desk.{TS}@gmail.com"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        ctx=await b.new_context(viewport={"width":1440,"height":900},device_scale_factor=1.5)
        pg=await ctx.new_page()
        await pg.goto(APP,wait_until="domcontentloaded")
        await pg.wait_for_selector('[data-testid="welcome-cta-signup"]',timeout=30000)
        await pg.wait_for_timeout(1000); await pg.click('[data-testid="welcome-cta-signup"]')
        await pg.wait_for_selector('[data-testid="auth-tab-register"]',timeout=15000,state="visible")
        await pg.click('[data-testid="auth-tab-register"]'); await pg.wait_for_timeout(400)
        await pg.fill('#regFirstname','Desk'); await pg.fill('#regLastname','Top'); await pg.fill('#regEmail',E)
        await pg.click('[data-testid="reg-step1-next"]')
        await pg.wait_for_selector('#regPassword',timeout=10000,state="visible")
        await pg.fill('#regPassword',PWD); await pg.fill('#regPassword2',PWD)
        await pg.click('[data-testid="reg-step2-next"]')
        await pg.wait_for_selector('#btnRegister',timeout=10000,state="visible"); await pg.click('#btnRegister')
        await pg.wait_for_timeout(6000)
        await pg.evaluate("()=>{try{if(typeof obFinish==='function')obFinish();}catch(e){}}")
        await pg.wait_for_timeout(5000)
        await pg.evaluate("()=>{try{generateMenu();}catch(e){}}")
        await pg.wait_for_timeout(3500)
        async def shot(name,tab):
            await pg.evaluate(f"window.switchTab && window.switchTab('{tab}')")
            await pg.wait_for_timeout(2800)
            await pg.evaluate("window.scrollTo(0,0)")
            await pg.wait_for_timeout(600)
            await pg.screenshot(path=os.path.join(OUT,name),full_page=False)
            print("saved",name)
        await shot("desktop_plan.png","plan")
        await shot("desktop_library.png","library")
        await shot("desktop_profile.png","profile")
        await b.close()
asyncio.run(main())
