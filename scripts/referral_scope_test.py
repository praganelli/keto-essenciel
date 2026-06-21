import asyncio, time, json
from playwright.async_api import async_playwright
APP="http://localhost:8001/api/app"
TS=int(time.time()); PWD="DemoKeto2026!"; CODE="PAULPA4781"; A=f"scope.{TS}@gmail.com"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        pg=await (await b.new_context(viewport={"width":430,"height":932})).new_page()
        await pg.goto(APP,wait_until="domcontentloaded")
        await pg.wait_for_selector('[data-testid="welcome-cta-signup"]',timeout=30000)
        await pg.wait_for_timeout(800); await pg.click('[data-testid="welcome-cta-signup"]')
        await pg.wait_for_selector('[data-testid="auth-tab-register"]',timeout=15000,state="visible")
        await pg.click('[data-testid="auth-tab-register"]'); await pg.wait_for_timeout(400)
        await pg.fill('#regFirstname','Anna'); await pg.fill('#regLastname','Aaa'); await pg.fill('#regEmail',A)
        await pg.click('[data-testid="reg-step1-next"]')
        await pg.wait_for_selector('#regPassword',timeout=10000,state="visible")
        await pg.fill('#regPassword',PWD); await pg.fill('#regPassword2',PWD)
        await pg.click('[data-testid="reg-step2-next"]')
        await pg.wait_for_selector('#btnRegister',timeout=10000,state="visible")
        await pg.fill('#regReferralCode', CODE); await pg.click('#btnRegister')
        await pg.wait_for_timeout(6000)
        await pg.evaluate("()=>{try{if(typeof obFinish==='function')obFinish();}catch(e){}}")
        await pg.wait_for_timeout(5000)
        res=await pg.evaluate("""() => {
            const out={uid:(currentUser&&currentUser.uid)||null, keys:[], global:null, scopedHasData:false, otherUidData:null};
            out.global = localStorage.getItem('kp_used_referral_v1'); // doit etre null (fuite)
            for(let i=0;i<localStorage.length;i++){ const k=localStorage.key(i); if(k.indexOf('kp_used_referral')===0) out.keys.push(k); }
            const sk = out.uid ? ('kp_used_referral_v1__'+out.uid) : null;
            out.scopedHasData = sk ? !!localStorage.getItem(sk) : false;
            out.otherUidData = localStorage.getItem('kp_used_referral_v1__SOME_OTHER_USER_UID'); // simule un autre compte
            // simulate the render read for another uid via the helper
            return out;
        }""")
        await b.close()
        print("UID:", res["uid"])
        print("clé GLOBALE kp_used_referral_v1 (doit être null):", res["global"])
        print("clés used_referral présentes:", res["keys"])
        print("clé scopée de A contient des données (attendu True):", res["scopedHasData"])
        print("données pour un AUTRE uid (attendu None):", res["otherUidData"])
        ok = (res["global"] is None) and res["scopedHasData"] and (res["otherUidData"] is None)
        print("RESULT:", "PASS - donnée isolée par compte, aucune fuite" if ok else "FAIL")
asyncio.run(main())
