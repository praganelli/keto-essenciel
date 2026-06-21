import asyncio, time, json
from playwright.async_api import async_playwright

APP="http://localhost:8001/api/app"
TS=int(time.time())
PAR_EMAIL=f"parrain.{TS}@gmail.com"
FIL_EMAIL=f"filleul.{TS}@gmail.com"
PWD="DemoKeto2026!"

async def signup(pg, first, last, email, referral=None):
    await pg.goto(APP, wait_until="domcontentloaded")
    await pg.wait_for_selector('[data-testid="welcome-cta-signup"]',timeout=30000)
    await pg.wait_for_timeout(1000)
    await pg.click('[data-testid="welcome-cta-signup"]')
    await pg.wait_for_selector('[data-testid="auth-tab-register"]',timeout=15000,state="visible")
    await pg.click('[data-testid="auth-tab-register"]'); await pg.wait_for_timeout(400)
    await pg.fill('#regFirstname',first); await pg.fill('#regLastname',last); await pg.fill('#regEmail',email)
    await pg.click('[data-testid="reg-step1-next"]')
    await pg.wait_for_selector('#regPassword',timeout=10000,state="visible")
    await pg.fill('#regPassword',PWD); await pg.fill('#regPassword2',PWD)
    await pg.click('[data-testid="reg-step2-next"]')
    await pg.wait_for_selector('#btnRegister',timeout=10000,state="visible")
    if referral:
        await pg.fill('#regReferralCode', referral)

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        # ---- PARRAIN ----
        c1=await b.new_context(viewport={"width":430,"height":932})
        pg1=await c1.new_page()
        await signup(pg1,"Paul","Parrain",PAR_EMAIL)
        await pg1.click('#btnRegister')
        await pg1.wait_for_timeout(5000)
        await pg1.evaluate("()=>{try{if(typeof obFinish==='function')obFinish();}catch(e){}}")
        await pg1.wait_for_timeout(5000)
        code=None
        for _ in range(8):
            code=await pg1.evaluate("()=>localStorage.getItem('kp_referral_code')")
            if code: break
            await pg1.wait_for_timeout(1500)
        print("PARRAIN_EMAIL=",PAR_EMAIL)
        print("PARRAIN_CODE=",code)
        await c1.close()
        if not code:
            print("NO CODE - abort"); await b.close(); return

        # ---- FILLEUL ----
        c2=await b.new_context(viewport={"width":430,"height":932})
        pg2=await c2.new_page()
        await signup(pg2,"Fanny","Filleul",FIL_EMAIL,referral=code)
        try:
            async with pg2.expect_response(lambda r: "referralReward" in r.url, timeout=20000) as ri:
                await pg2.click('#btnRegister')
            resp=await ri.value
            body=await resp.text()
            print("REFERRAL_FN_STATUS=",resp.status)
            print("REFERRAL_FN_BODY=",body[:200])
        except Exception as e:
            print("referralReward response not captured:",e)
            await pg2.wait_for_timeout(6000)
        await pg2.wait_for_timeout(4000)
        await c2.close()
        await b.close()
        print("FILLEUL_EMAIL=",FIL_EMAIL)

asyncio.run(main())
