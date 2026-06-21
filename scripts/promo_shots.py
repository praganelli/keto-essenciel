import asyncio, time, os
from playwright.async_api import async_playwright

APP_URL = "http://localhost:8001/api/app"
OUT = "/app/promo_raw"
os.makedirs(OUT, exist_ok=True)

TS = int(time.time())
EMAIL = f"demo.keto.{TS}@gmail.com"
PWD = "DemoKeto2026!"
FIRST = "Sophie"
LAST = "Martin"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=3,
            locale="fr-FR",
        )
        page = await ctx.new_page()
        page.on("console", lambda m: print("CONSOLE:", m.type, m.text[:140]))
        await page.goto(APP_URL, wait_until="domcontentloaded")
        print("loaded")

        # wait landing
        await page.wait_for_selector('[data-testid="welcome-cta-signup"]', timeout=30000)
        await page.wait_for_timeout(1500)
        await page.click('[data-testid="welcome-cta-signup"]')
        print("clicked signup")

        # ensure register tab active
        await page.wait_for_selector('[data-testid="auth-tab-register"]', timeout=15000, state="visible")
        await page.wait_for_timeout(800)
        await page.click('[data-testid="auth-tab-register"]')
        await page.wait_for_timeout(600)

        # reg step 1
        await page.wait_for_selector('#regFirstname', timeout=15000, state="visible")
        await page.fill('#regFirstname', FIRST)
        await page.fill('#regLastname', LAST)
        await page.fill('#regEmail', EMAIL)
        await page.click('[data-testid="reg-step1-next"]')
        print("step1 done")

        # reg step 2
        await page.wait_for_selector('#regPassword', timeout=10000, state="visible")
        await page.fill('#regPassword', PWD)
        await page.fill('#regPassword2', PWD)
        await page.click('[data-testid="reg-step2-next"]')
        print("step2 done")

        # reg step 3 -> create account
        await page.wait_for_selector('#btnRegister', timeout=10000, state="visible")
        await page.click('#btnRegister')
        print("register clicked, waiting for firebase + onboarding...")

        # wait for onboarding wizard to appear then finish it programmatically
        await page.wait_for_timeout(5000)
        # try to finish onboarding with default profile values
        for attempt in range(10):
            done = await page.evaluate("""() => {
                try {
                    if (typeof obFinish === 'function' && typeof obData !== 'undefined') {
                        obFinish();
                        return 'finished';
                    }
                } catch(e){ return 'err:'+e.message; }
                return 'notready';
            }""")
            print("obFinish attempt", attempt, "->", done)
            if done == 'finished':
                break
            await page.wait_for_timeout(1500)

        # let app boot
        await page.wait_for_timeout(5000)

        # Generate the weekly menu so the Plan tab shows real meals
        for attempt in range(8):
            ok = await page.evaluate("""() => {
                try { if(typeof generateMenu==='function'){ generateMenu(); return 'gen'; } }
                catch(e){ return 'err:'+e.message; }
                return 'notready';
            }""")
            print("generateMenu attempt", attempt, "->", ok)
            if ok == 'gen':
                break
            await page.wait_for_timeout(1500)
        await page.wait_for_timeout(4000)

        async def shot(name, scroll_sel=None, block="start", settle=2600):
            if scroll_sel:
                await page.evaluate(f"""() => {{
                    const el = document.querySelector('{scroll_sel}');
                    if(el) el.scrollIntoView({{block:'{block}', behavior:'instant'}});
                }}""")
            else:
                await page.evaluate("window.scrollTo(0,0)")
            await page.wait_for_timeout(settle)
            path = os.path.join(OUT, name)
            await page.screenshot(path=path, full_page=False)
            print("saved", path)

        # 1. Plan - week grid (menu generated, meals visible)
        await page.evaluate("window.switchTab && window.switchTab('plan')")
        await page.wait_for_timeout(2500)
        await shot("1_plan_week.png", scroll_sel="#weekGrid", block="start")

        # 2. Day detail with macro rings + meals
        await page.evaluate("try{selectDay(0);}catch(e){}")
        await page.wait_for_timeout(2800)
        await shot("2_day_detail.png", scroll_sel="#day-panel", block="start")

        # 3. Recipes library grid
        await page.evaluate("window.switchTab && window.switchTab('library')")
        await page.wait_for_timeout(3000)
        await shot("3_library.png", scroll_sel="#libGrid", block="start")

        # 4. Recipe modal (open first recipe card)
        try:
            await page.evaluate("""() => {
                const card = document.querySelector('.lib-card');
                if(card) card.click();
            }""")
            await page.wait_for_timeout(2800)
            await shot("4_recipe_modal.png")
            await page.evaluate("""() => { const m=document.querySelector('.recipe-modal'); const x=m&&m.querySelector('[onclick*=close], .recipe-modal-close, button'); if(x) x.click(); }""")
            await page.wait_for_timeout(800)
        except Exception as e:
            print("recipe modal err", e)

        # 5. Suivi (tracking feature)
        await page.evaluate("window.switchTab && window.switchTab('suivi')")
        await page.wait_for_timeout(3000)
        await shot("5_suivi.png")

        # 6. Profile
        await page.evaluate("window.switchTab && window.switchTab('profile')")
        await page.wait_for_timeout(3000)
        await shot("6_profile.png")

        # 7. Premium pricing modal (great for marketing — overlay, no email)
        try:
            await page.evaluate("try{openPremiumModal('plan');}catch(e){}")
            await page.wait_for_timeout(2800)
            await shot("7_premium_modal.png")
            await page.evaluate("""() => { const x=document.querySelector('.kp-modal-close'); if(x) x.click(); }""")
            await page.wait_for_timeout(700)
        except Exception as e:
            print("premium modal err", e)

        # 8. Shopping list
        try:
            await page.evaluate("window.switchTab && window.switchTab('plan')")
            await page.wait_for_timeout(1500)
            await page.evaluate("try{generateShopping();}catch(e){}")
            await page.wait_for_timeout(2000)
            await shot("8_shopping.png", scroll_sel="#shopping-wrap", block="start")
        except Exception as e:
            print("shopping err", e)

        await browser.close()
        print("EMAIL=", EMAIL)

asyncio.run(main())
