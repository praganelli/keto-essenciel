#!/usr/bin/env python3
# 1) Dashboard : composition complète des repas (entrée/plat/dessert) + refresh immédiat
# 2) Nouveau logo horizontal partout DANS l'app (pas le login) : splash, header, landing
# 3) Splash relooké identité claire ; 4) icônes PWA GCS ; 5) version 2.0
import io, base64, re, sys, urllib.parse

PATH = '/app/keto.html'
src = io.open(PATH, encoding='utf-8').read()
LOGO_BIG = 'data:image/webp;base64,' + base64.b64encode(open('/tmp/logo_h.webp', 'rb').read()).decode()
LOGO_SM = 'data:image/webp;base64,' + base64.b64encode(open('/tmp/logo_h_small.webp', 'rb').read()).decode()
ICON192 = 'https://storage.googleapis.com/testprojet-721cb-recipes/app/icon-192.png'
ICON512 = 'https://storage.googleapis.com/testprojet-721cb-recipes/app/icon-512.png'
APPLE = 'https://storage.googleapis.com/testprojet-721cb-recipes/app/apple-touch-icon.png'


def rep(old, new, label, count=1):
    global src
    if src.count(old) != count:
        print('FAIL:', label, src.count(old)); sys.exit(1)
    src = src.replace(old, new)
    print('OK:', label)


# ═══ A — Composition des repas dans « Repas du jour » ═══
rep('''  var cards=[];
  try{
    if(meals.breakfast&&d.bfast!=null&&BFAST_RECIPES[d.bfast]) cards.push(mealCard(BFAST_RECIPES[d.bfast],'Petit-déj'));
    if(meals.lunch){ var lr=recipeAtSlot(d,'lunch'); if(lr) cards.push(mealCard(lr,'Déjeuner')); }
    if(meals.dinner){ var dr=recipeAtSlot(d,'dinner'); if(dr) cards.push(mealCard(dr,'Dîner')); }
  }catch(e){}''',
    '''  var cards=[];
  try{
    var courses=(typeof getCourses==='function')?getCourses():{starter:true,dessert:true};
    function pushSlot(slot,badge){ var r=recipeAtSlot(d,slot); if(r) cards.push(mealCard(r,badge)); }
    if(meals.breakfast&&d.bfast!=null&&BFAST_RECIPES[d.bfast]) cards.push(mealCard(BFAST_RECIPES[d.bfast],'Petit-déj'));
    if(meals.lunch){
      if(courses.starter&&d.lunchStarter!=null) pushSlot('lunchStarter','Déjeuner · Entrée');
      pushSlot('lunch','Déjeuner · Plat');
      if(courses.dessert&&d.lunchDessert!=null) pushSlot('lunchDessert','Déjeuner · Dessert');
    }
    if(meals.dinner){
      if(courses.starter&&d.dinnerStarter!=null) pushSlot('dinnerStarter','Dîner · Entrée');
      pushSlot('dinner','Dîner · Plat');
      if(courses.dessert&&d.dinnerDessert!=null) pushSlot('dinnerDessert','Dîner · Dessert');
    }
  }catch(e){}''',
    'A1 composition repas')

# refresh immédiat : préserver le scroll + wrapper save()
rep('''  host.innerHTML=greet+resume+goal+mealsCard;
  var sc=$id('kpdScroll'), dt=$id('kpdDots');''',
    '''  var _prevSc=$id('kpdScroll'); var _prevLeft=_prevSc?_prevSc.scrollLeft:0;
  host.innerHTML=greet+resume+goal+mealsCard;
  var sc=$id('kpdScroll'), dt=$id('kpdDots');
  if(sc&&_prevLeft) sc.scrollLeft=_prevLeft;''',
    'A2 scroll préservé')

rep('''function boot(){ try{ kpRenderDashboard(); }catch(e){} }''',
    '''/* Refresh immédiat dès qu'une donnée change (swap de repas, régénération, profil…) */
var _kpdT=null;
function kpdQueue(){ clearTimeout(_kpdT); _kpdT=setTimeout(function(){ try{ kpRenderDashboard(); }catch(e){} },350); }
if(typeof window.save==='function'){
  var _kpdSave=window.save;
  window.save=function(){ var r=_kpdSave.apply(this,arguments); kpdQueue(); return r; };
}
function boot(){ try{ kpRenderDashboard(); }catch(e){} }''',
    'A3 refresh immédiat')

# ═══ B — SPLASH identité claire + logo horizontal + v2.0 ═══
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 390 844" preserveAspectRatio="xMidYMid slice">'
       '<rect width="390" height="844" fill="#faf8f0"/>'
       '<path d="M0 0 H390 V236 Q322 300 218 288 Q96 274 44 322 Q12 350 0 344 Z" fill="#f2f2e3"/>'
       '<circle cx="404" cy="392" r="98" fill="#e9eed8"/>'
       '<circle cx="-26" cy="475" r="72" fill="#eef1de"/>'
       '<ellipse cx="42" cy="856" rx="165" ry="115" fill="#e6ecd2"/>'
       '<ellipse cx="362" cy="868" rx="175" ry="125" fill="#e2e9ca"/>'
       '</svg>')
enc = urllib.parse.quote(svg, safe="~()*!.'")

rep('''  background:linear-gradient(160deg,#051209 0%,#0a2015 40%,#0d2818 70%,#061510 100%);
  transition:opacity .9s cubic-bezier(.4,0,.2,1),transform .9s cubic-bezier(.4,0,.2,1);
}''',
    '''  background:url("data:image/svg+xml,''' + enc + '''") center/cover no-repeat #faf8f0;
  transition:opacity .9s cubic-bezier(.4,0,.2,1),transform .9s cubic-bezier(.4,0,.2,1);
}''',
    'B1 splash fond')

rep('''#splash::before{
  content:'';position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(45,122,82,.07) 1px,transparent 1px),
    linear-gradient(90deg,rgba(45,122,82,.07) 1px,transparent 1px);
  background-size:48px 48px;
  animation:grid-drift 20s linear infinite;
}''',
    '''#splash::before{ content:none; }''',
    'B2 grille off')

rep('''#splash::after{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 60% at 50% 50%, rgba(45,122,82,.18) 0%, transparent 70%);
  animation:glow-pulse 4s ease-in-out infinite;
}''',
    '''#splash::after{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 62% 55% at 50% 46%, rgba(163,190,140,.28) 0%, transparent 70%);
  animation:glow-pulse 4s ease-in-out infinite;
}''',
    'B3 glow sage')

rep('''.splash-ring{
  position:absolute;border-radius:50%;border:1px solid rgba(45,122,82,.25);''',
    '''.splash-ring{
  position:absolute;border-radius:50%;border:1px solid rgba(94,124,97,.22);''',
    'B4 rings')

rep('''.splash-version{
  margin-top:14px;
  padding:4px 14px;border-radius:100px;
  background:rgba(45,122,82,.2);border:1px solid rgba(45,122,82,.35);
  font-size:11px;font-weight:700;letter-spacing:.1em;color:rgba(255,255,255,.6);''',
    '''.splash-version{
  margin-top:14px;
  padding:4px 14px;border-radius:100px;
  background:rgba(94,124,97,.12);border:1px solid rgba(94,124,97,.28);
  font-size:11px;font-weight:700;letter-spacing:.1em;color:#3c5a2c;''',
    'B5 pill version')

rep('''.splash-progress-track{
  height:3px;border-radius:3px;
  background:rgba(255,255,255,.1);overflow:hidden;
}''',
    '''.splash-progress-track{
  height:3px;border-radius:3px;
  background:rgba(30,42,30,.12);overflow:hidden;
}''',
    'B6 progress track')

rep('''  color:rgba(255,255,255,.35);
  animation:splash-dots 1.4s ease-in-out 1.2s infinite;''',
    '''  color:#8a9086;
  animation:splash-dots 1.4s ease-in-out 1.2s infinite;''',
    'B7 progress label')

rep('''.splash-tag{
  font-family:var(--font-body);font-size:13px;font-weight:400;
  color:rgba(255,255,255,.45);letter-spacing:.18em;text-transform:uppercase;''',
    '''.splash-tag{
  font-family:var(--font-body);font-size:13px;font-weight:500;
  color:#7d857a;letter-spacing:.18em;text-transform:uppercase;''',
    'B8 tag couleur')

# markup : logo horizontal à la place du SVG avocat + nom
i = src.index('    <!-- Avocado SVG -->')
j = src.index('    <div class="splash-tag">')
assert '<div class="splash-name">' in src[i:j]
src = src[:i] + '''    <img class="splash-logo-img" src="''' + LOGO_BIG + '''" alt="Keto-Essenciel" draggable="false">
''' + src[j:]
print('OK: B9 splash logo markup')

rep('''/* Avocado SVG container */
.splash-avo{
  width:180px;height:180px;margin-bottom:8px;
  animation:splash-avo-in 1s cubic-bezier(.16,1,.3,1) .1s both;
  filter:drop-shadow(0 0 40px rgba(45,122,82,.5));
}''',
    '''/* Logo horizontal */
.splash-logo-img{
  width:min(78vw,430px);height:auto;margin-bottom:14px;
  animation:splash-avo-in 1s cubic-bezier(.16,1,.3,1) .1s both;
  filter:drop-shadow(0 12px 30px rgba(46,74,34,.22));
}''',
    'B10 splash logo css')

# ═══ C — HEADER mobile : logo horizontal ═══
pat = re.compile(r'<img class="khh-logo" src="data:image/webp;base64,[^"]+" alt="Keto-Essenciel" draggable="false">\n        <div class="khh-titlewrap">\n          <div class="khh-title">Keto-<em>Essenciel</em></div>')
new = '''<div class="khh-titlewrap">
          <img class="khh-logo-h" src="''' + LOGO_SM + '''" alt="Keto-Essenciel" draggable="false">'''
src2, n = pat.subn(new, src)
assert n == 1, 'C1 header'
src = src2
print('OK: C1 header logo')

rep('''.khh-logo{ width:48px; height:auto; flex:0 0 auto; }''',
    '''.khh-logo-h{ height:48px; width:auto; display:block; margin-left:-4px; }''',
    'C2 header css')

# ═══ D — LANDING hero : logo ═══
rep('''    <div class="kpw-hero-content">
      <div class="kpw-eyebrow">Essenciel O Naturel · Naturopathie · Lunéville</div>''',
    '''    <div class="kpw-hero-content">
      <img class="kpw-hero-logo" id="kpwHeroLogo" alt="Keto-Essenciel" draggable="false">
      <div class="kpw-eyebrow">Essenciel O Naturel · Naturopathie · Lunéville</div>''',
    'D1 landing markup')

rep('''<div id="kpQuickBackdrop" onclick="kpQuickClose()" data-testid="kp-quick-backdrop"></div>''',
    '''<style>
.kpw-hero-logo{ height:58px; width:auto; display:block; margin-bottom:18px;
  filter:drop-shadow(0 0 16px rgba(255,255,255,.75)) drop-shadow(0 4px 14px rgba(0,0,0,.3)); }
@media (max-width:640px){ .kpw-hero-logo{ height:46px; margin-bottom:14px; } }
</style>
<script>
document.addEventListener('DOMContentLoaded',function(){
  try{ var t=document.querySelector('.khh-logo-h'); var d=document.getElementById('kpwHeroLogo'); if(t&&d) d.src=t.src; }catch(e){}
});
</script>
<div id="kpQuickBackdrop" onclick="kpQuickClose()" data-testid="kp-quick-backdrop"></div>''',
    'D2 landing css+js')

# ═══ E — PWA : icônes réelles + couleurs identité + liens head ═══
rep('''        icons: [
          { src: 'data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 192 192%22><rect width=%22192%22 height=%22192%22 rx=%2240%22 fill=%22%23f4ecd9%22/><text x=%2296%22 y=%22130%22 font-size=%22120%22 text-anchor=%22middle%22>🥑</text></svg>', sizes:'192x192', type:'image/svg+xml', purpose:'any maskable' },
          { src: 'data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 512 512%22><rect width=%22512%22 height=%22512%22 rx=%22100%22 fill=%22%23f4ecd9%22/><text x=%22256%22 y=%22350%22 font-size=%22320%22 text-anchor=%22middle%22>🥑</text></svg>', sizes:'512x512', type:'image/svg+xml', purpose:'any maskable' }
        ]''',
    '''        icons: [
          { src: 'ICON192PLACEHOLDER', sizes:'192x192', type:'image/png', purpose:'any maskable' },
          { src: 'ICON512PLACEHOLDER', sizes:'512x512', type:'image/png', purpose:'any maskable' }
        ]''',
    'E1 manifest icons')
src = src.replace("'ICON192PLACEHOLDER'", "'" + ICON192 + "'")
src = src.replace("'ICON512PLACEHOLDER'", "'" + ICON512 + "'")

rep("        background_color: '#f4ecd9',\n        theme_color: '#3d5a40',",
    "        background_color: '#faf8f0',\n        theme_color: '#4e7a36',",
    'E2 manifest couleurs')
rep("      m.name = 'theme-color'; m.content = '#3d5a40';",
    "      m.name = 'theme-color'; m.content = '#4e7a36';",
    'E3 meta theme')
rep('<link rel="dns-prefetch" href="https://identitytoolkit.googleapis.com">',
    '''<link rel="dns-prefetch" href="https://identitytoolkit.googleapis.com">
<link rel="icon" type="image/png" sizes="192x192" href="''' + ICON192 + '''">
<link rel="apple-touch-icon" sizes="180x180" href="''' + APPLE + '''">''',
    'E4 favicon/apple links')

# ═══ F — Version 2.0 ═══
rep('v1.1 · 300+ Recettes · Suivi · PDF', 'v2.0 · 300+ Recettes · Suivi · PDF', 'F1 splash version')
rep('Keto - Essenciel <span style="color:var(--ed-muted);font-size:12px">v1.1</span>',
    'Keto - Essenciel <span style="color:var(--ed-muted);font-size:12px">v2.0</span>', 'F2 réglages version')
rep('<span class="bb-ver">v1.1</span>', '<span class="bb-ver">v2.0</span>', 'F3 badge version')

io.open(PATH, 'w', encoding='utf-8').write(src)
print('DONE', len(src))
