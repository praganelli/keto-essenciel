import base64, asyncio, os
from PIL import Image
from playwright.async_api import async_playwright

RAW = "/app/promo_raw"
SHOT = os.path.join(RAW, "2_day_detail.png")  # phone mockup content

# prepare base64 of the screenshot resized to ~560 wide
im = Image.open(SHOT)
w = 560
h = int(im.size[1] * w / im.size[0])
im2 = im.resize((w, h))
crop_h = 1180  # show the top portion (rings + first meal)
im2 = im2.crop((0, 0, w, min(crop_h, h)))
tmp = "/tmp/_shot_small.png"
im2.save(tmp)
b64 = base64.b64encode(open(tmp, "rb").read()).decode()

HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden}
body{
  font-family:'Plus Jakarta Sans',sans-serif;
  background:
    radial-gradient(120% 60% at 50% -10%, rgba(255,255,255,.10) 0%, rgba(255,255,255,0) 55%),
    linear-gradient(158deg, #233a28 0%, #2f4a33 42%, #3d5a40 70%, #4a6b4e 100%);
  color:#f6efe0;position:relative;
}
.grain{position:absolute;inset:0;opacity:.06;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");}
.wrap{position:relative;z-index:2;height:100%;display:flex;flex-direction:column;
  align-items:center;text-align:center;padding:120px 90px 96px}
.eyebrow{font-size:23px;font-weight:700;letter-spacing:.42em;text-transform:uppercase;
  color:#d8b25f;margin-bottom:34px}
.h1{font-family:'Fraunces',serif;line-height:.94;font-weight:400}
.h1 .l1{display:block;font-size:118px;color:#f8f2e4;letter-spacing:-.02em}
.h1 .l2{display:block;font-style:italic;font-size:96px;color:#e7c372;margin-top:6px}
.rule{width:120px;height:2px;background:linear-gradient(90deg,transparent,#d8b25f,transparent);margin:42px auto 34px}
.lead{font-size:33px;line-height:1.5;color:#e8e0cf;max-width:780px;font-weight:400}
.lead b{color:#f6efe0;font-weight:700}
.phone{margin:58px auto 0;width:600px;border-radius:54px;padding:18px;
  background:linear-gradient(180deg,#11201600,#0d1a1240);
  border:2px solid rgba(255,255,255,.16);
  box-shadow:0 40px 90px -20px rgba(0,0,0,.55), 0 0 0 1px rgba(255,255,255,.05) inset;}
.phone-screen{width:100%;border-radius:38px;overflow:hidden;display:block;
  box-shadow:0 10px 30px -10px rgba(0,0,0,.5)}
.phone-screen img{width:100%;display:block}
.chips{display:flex;gap:18px;justify-content:center;margin:54px auto 0;flex-wrap:wrap}
.chip{font-size:25px;font-weight:600;color:#f3ead7;padding:16px 28px;border-radius:999px;
  background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);
  backdrop-filter:blur(6px)}
.cta{margin-top:auto;display:inline-flex;align-items:center;gap:16px;
  font-size:34px;font-weight:700;color:#2a2114;padding:30px 66px;border-radius:999px;
  background:linear-gradient(135deg,#f0cd78 0%,#d8a94a 60%,#caa043 100%);
  box-shadow:0 20px 50px -12px rgba(202,160,67,.55), 0 2px 0 rgba(255,255,255,.4) inset;
  letter-spacing:.01em}
.cta .arr{font-size:30px}
.foot{margin-top:30px;font-size:24px;letter-spacing:.16em;text-transform:uppercase;color:#bcd0bb;font-weight:600}
</style></head>
<body><div class="grain"></div>
<div class="wrap">
  <div class="eyebrow">Essenciel O Naturel · Naturopathie · Lunéville</div>
  <h1 class="h1"><span class="l1">Le keto</span><span class="l2">par un naturopathe</span></h1>
  <div class="rule"></div>
  <div class="lead">Votre <b>programme cétogène personnalisé</b> :<br>menus, 305 recettes &amp; suivi, pensés pour votre profil.</div>
  <div class="phone"><div class="phone-screen"><img src="data:image/png;base64,__B64__"></div></div>
  <div class="chips"><div class="chip">🥑 305 recettes</div><div class="chip">📊 Suivi des macros</div><div class="chip">🌿 Modes adaptés</div></div>
  <div class="cta"><span>Disponible maintenant</span><span class="arr">→</span></div>
  <div class="foot">Téléchargez l'application</div>
</div>
</body></html>""".replace("__B64__", b64)

html_path = os.path.join(RAW, "story.html")
open(html_path, "w").write(HTML)

async def render():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":1080,"height":1920}, device_scale_factor=2)
        pg = await ctx.new_page()
        await pg.goto("file://"+html_path, wait_until="load")
        await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(1500)
        out2x = os.path.join(RAW, "story_fb_2x.png")
        await pg.screenshot(path=out2x, full_page=False)
        await b.close()
        # downscale to exact 1080x1920
        Image.open(out2x).resize((1080,1920)).save(os.path.join(RAW,"story_fb.png"))
        print("story rendered")

asyncio.run(render())
