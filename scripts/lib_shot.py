import asyncio, time, os
from playwright.async_api import async_playwright
APP="http://localhost:8001/api/app"
TS=int(time.time()); EMAIL=f"libshot.{TS}@gmail.com"; PWD="DemoKeto2026!"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        ctx=await b.new_context(viewport={"width":430,"height":932},device_scale_factor=2)
        pg=await ctx.new_page()
        await pg.goto(APP,wait_until="domcontentloaded")
        await pg.wait_for_selector('[data-testid="welcome-cta-signup"]',timeout=30000)
        await pg.wait_for_timeout(1000); await pg.click('[data-testid="welcome-cta-signup"]')
        await pg.wait_for_selector('[data-testid="auth-tab-register"]',timeout=15000,state="visible")
        await pg.click('[data-testid="auth-tab-register"]'); await pg.wait_for_timeout(400)
        await pg.fill('#regFirstname','Lib'); await pg.fill('#regLastname','Shot'); await pg.fill('#regEmail',EMAIL)
        await pg.click('[data-testid="reg-step1-next"]')
        await pg.wait_for_selector('#regPassword',timeout=10000,state="visible")
        await pg.fill('#regPassword',PWD); await pg.fill('#regPassword2',PWD)
        await pg.click('[data-testid="reg-step2-next"]')
        await pg.wait_for_selector('#btnRegister',timeout=10000,state="visible"); await pg.click('#btnRegister')
        await pg.wait_for_timeout(5000)
        await pg.evaluate("()=>{try{if(typeof obFinish==='function')obFinish();}catch(e){}}")
        await pg.wait_for_timeout(4000)
        await pg.evaluate("window.switchTab && window.switchTab('library')")
        await pg.wait_for_timeout(4500)
        await pg.evaluate("()=>{const e=document.querySelector('#libGrid'); if(e) e.scrollIntoView({block:'start'});}")
        await pg.wait_for_timeout(2500)
        os.makedirs("/app/promo_raw",exist_ok=True)
        await pg.screenshot(path="/app/promo_raw/lib_photos.png",full_page=False)
        print("saved lib_photos")
        await b.close()
asyncio.run(main())
