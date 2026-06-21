import asyncio, time
from playwright.async_api import async_playwright
APP="http://localhost:8001/api/app"
TS=int(time.time()); PWD="DemoKeto2026!"; CODE="PAULPA4781"
A=f"leakA.{TS}@gmail.com"; B=f"leakB.{TS}@gmail.com"

async def do_signup(pg, first, last, email, referral=None):
    await pg.wait_for_selector('[data-testid="welcome-cta-signup"]',timeout=30000)
    await pg.wait_for_timeout(800); await pg.click('[data-testid="welcome-cta-signup"]')
    await pg.wait_for_selector('[data-testid="auth-tab-register"]',timeout=15000,state="visible")
    await pg.click('[data-testid="auth-tab-register"]'); await pg.wait_for_timeout(400)
    await pg.fill('#regFirstname',first); await pg.fill('#regLastname',last); await pg.fill('#regEmail',email)
    await pg.click('[data-testid="reg-step1-next"]')
    await pg.wait_for_selector('#regPassword',timeout=10000,state="visible")
    await pg.fill('#regPassword',PWD); await pg.fill('#regPassword2',PWD)
    await pg.click('[data-testid="reg-step2-next"]')
    await pg.wait_for_selector('#btnRegister',timeout=10000,state="visible")
    if referral: await pg.fill('#regReferralCode', referral)
    await pg.click('#btnRegister')
    await pg.wait_for_timeout(6000)
    await pg.evaluate("()=>{try{if(typeof obFinish==='function')obFinish();}catch(e){}}")
    await pg.wait_for_timeout(5000)

async def check_parrain(pg):
    await pg.evaluate("window.switchTab && window.switchTab('profile')")
    await pg.wait_for_timeout(4000)
    return await pg.evaluate("()=>!!document.querySelector('[data-testid=parrain-card]')")

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        ctx=await b.new_context(viewport={"width":430,"height":932})  # SAME context => same localStorage
        pg=await ctx.new_page()
        await pg.goto(APP,wait_until="domcontentloaded")
        # User A uses a referral code
        await do_signup(pg,"Anna","Aaa",A,referral=CODE)
        hasA=await check_parrain(pg)
        print("UserA (used code) parrain-card present:", hasA, "(attendu True)")
        # Logout
        await pg.evaluate("()=>{try{authLogout();}catch(e){}}")
        await pg.wait_for_timeout(3500)
        # reload to land on welcome screen (localStorage is preserved in same context)
        await pg.goto(APP, wait_until="domcontentloaded")
        await pg.wait_for_timeout(1500)
        # User B (NO code) on same browser
        await do_signup(pg,"Bob","Bbb",B,referral=None)
        hasB=await check_parrain(pg)
        print("UserB (no code, same browser) parrain-card present:", hasB, "(attendu False)")
        print("RESULT:", "PASS - pas de fuite" if (hasA and not hasB) else "FAIL")
        await b.close()
asyncio.run(main())
