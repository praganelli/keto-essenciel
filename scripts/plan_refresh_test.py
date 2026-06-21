import asyncio, time
from playwright.async_api import async_playwright
APP="http://localhost:8001/api/app"
TS=int(time.time()); PWD="DemoKeto2026!"; E=f"planrefresh.{TS}@gmail.com"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        pg=await (await b.new_context(viewport={"width":430,"height":932})).new_page()
        await pg.goto(APP,wait_until="domcontentloaded")
        await pg.wait_for_selector('[data-testid="welcome-cta-signup"]',timeout=30000)
        await pg.wait_for_timeout(800); await pg.click('[data-testid="welcome-cta-signup"]')
        await pg.wait_for_selector('[data-testid="auth-tab-register"]',timeout=15000,state="visible")
        await pg.click('[data-testid="auth-tab-register"]'); await pg.wait_for_timeout(400)
        await pg.fill('#regFirstname','Plan'); await pg.fill('#regLastname','Refresh'); await pg.fill('#regEmail',E)
        await pg.click('[data-testid="reg-step1-next"]')
        await pg.wait_for_selector('#regPassword',timeout=10000,state="visible")
        await pg.fill('#regPassword',PWD); await pg.fill('#regPassword2',PWD)
        await pg.click('[data-testid="reg-step2-next"]')
        await pg.wait_for_selector('#btnRegister',timeout=10000,state="visible"); await pg.click('#btnRegister')
        await pg.wait_for_timeout(6000)
        await pg.evaluate("()=>{try{if(typeof obFinish==='function')obFinish();}catch(e){}}")
        await pg.wait_for_timeout(5000)
        await pg.evaluate("window.switchTab && window.switchTab('plan')")
        await pg.wait_for_timeout(3000)
        before=await pg.evaluate("()=>{var h=document.getElementById('planPremiumStatusHost'); return h?h.innerText.replace(/\\s+/g,' ').trim().slice(0,120):'(no host)';}")
        print("AVANT changement abonnement:", before)
        # Simule un changement d'abonnement : écrit le doc premium (propre compte)
        await pg.evaluate("""() => {
            try { _grantPremiumDays((currentUser.email||'').toLowerCase(), currentUser.uid, 90, 'test_subscription'); }
            catch(e){ console.warn('grant err', e); }
        }""")
        # NE PAS appeler renderPlan manuellement — on teste la MAJ auto via onSnapshot
        await pg.wait_for_timeout(5000)
        after=await pg.evaluate("()=>{var h=document.getElementById('planPremiumStatusHost'); return h?h.innerText.replace(/\\s+/g,' ').trim().slice(0,120):'(no host)';}")
        print("APRES (auto, sans reload):", after)
        changed = before != after
        prem = ('jour' in after.lower()) or ('premium' in after.lower()) or ('restant' in after.lower())
        print("RESULT:", "PASS - cadre mis à jour automatiquement" if (changed and prem) else "FAIL")
        await b.close()
asyncio.run(main())
