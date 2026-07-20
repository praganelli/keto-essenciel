#!/usr/bin/env python3
# Refonte présentation app (mockup accueil) : header mobile, dashboard Plan,
# nav mobile 5 items avec FAB "+", feuille "Accès rapides" glissante,
# + login : Bienvenue plus petit, logo sur carte blanche distincte.
import io, base64, sys

PATH = '/app/keto.html'
src = io.open(PATH, encoding='utf-8').read()
AVO = 'data:image/webp;base64,' + base64.b64encode(open('/tmp/dash_avo.webp', 'rb').read()).decode()
EMB = 'data:image/webp;base64,' + base64.b64encode(open('/tmp/logo_emblem.webp', 'rb').read()).decode()


def rep(old, new, label):
    global src
    if src.count(old) != 1:
        print('FAIL:', label, src.count(old)); sys.exit(1)
    src = src.replace(old, new)
    print('OK:', label)


# ═══ P1 — LOGIN : titre plus petit + logo carte blanche ═══
rep(".kpl-title{ font-family:'Plus Jakarta Sans',sans-serif; font-size:31px; font-weight:800; letter-spacing:-.02em; color:#3f7d3a; margin:0 0 8px; }",
    ".kpl-title{ font-family:'Plus Jakarta Sans',sans-serif; font-size:23px; font-weight:800; letter-spacing:-.02em; color:#3f7d3a; margin:0 0 6px; }",
    'P1 titre base')
rep(".kpl-title-leaf{ font-size:24px; }", ".kpl-title-leaf{ font-size:18px; }", 'P1 leaf base')
rep("  .kpl-title{ font-size:28px; }", "  .kpl-title{ font-size:21px; }", 'P1 titre desktop')
rep("  .kpl-title{ font-size:clamp(21px, 3dvh, 28px); margin-bottom:clamp(3px, .7dvh, 7px); }",
    "  .kpl-title{ font-size:clamp(18px, 2.5dvh, 22px); margin-bottom:clamp(3px, .6dvh, 6px); }",
    'P1 titre mobile')
rep("  .kpl-title-leaf{ font-size:clamp(16px, 2.4dvh, 22px); }",
    "  .kpl-title-leaf{ font-size:clamp(13px, 1.9dvh, 17px); }",
    'P1 leaf mobile')
rep(".kpl-logo{ width:clamp(210px, 52vw, 285px); max-width:100%; height:auto; display:block; margin:0 auto; filter:drop-shadow(0 8px 22px rgba(46,74,34,.14)); }",
    ".kpl-logo{ width:clamp(210px, 52vw, 285px); max-width:100%; height:auto; display:block; margin:0 auto; background:#fff; padding:14px 22px 11px; border-radius:26px; border:1px solid rgba(94,124,97,.12); box-shadow:0 18px 40px -22px rgba(46,74,34,.4), 0 2px 8px -4px rgba(46,74,34,.12); box-sizing:border-box; }",
    'P1 logo carte')

# ═══ P2 — HEADER mobile façon mockup ═══
rep('''  <header>
    <div class="eyebrow">''',
    '''  <header>
    <div id="kpHomeHeader" data-testid="kp-home-header">
      <div class="khh-left">
        <img class="khh-logo" src="''' + EMB + '''" alt="Keto-Essenciel" draggable="false">
        <div class="khh-titlewrap">
          <div class="khh-title">Keto-<em>Essenciel</em></div>
          <button type="button" class="khh-status" id="kpHomeStatus" onclick="openPremiumModal&&openPremiumModal('header')">🎁 GRATUIT</button>
        </div>
      </div>
      <button type="button" class="khh-bell" onclick="openPrefs()" aria-label="Rappels &amp; notifications" data-testid="kp-home-bell">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 9a6 6 0 1 0-12 0c0 5-2 6-2 6h16s-2-1-2-6Z"/><path d="M10.3 19a2 2 0 0 0 3.4 0"/></svg>
        <span class="khh-bell-dot"></span>
      </button>
    </div>
    <div class="eyebrow">''',
    'P2 header')

# ═══ P3 — Host dashboard en tête de l'onglet Plan ═══
rep('''  <div id="tab-plan">
    <!-- 💎 Votre formule actuelle (Plan) -->''',
    '''  <div id="tab-plan">
    <div id="kpDashHost" data-testid="kp-dash"></div>
    <!-- 💎 Votre formule actuelle (Plan) -->''',
    'P3 dash host')

# ═══ P4 — Bouton "+" central dans la barre mobile ═══
rep('''    <button class="bnav-fab" id="bnavFab"''',
    '''    <button class="bnav-plus" id="bnavPlus" type="button" onclick="kpQuickOpen()" aria-label="Accès rapides" data-testid="bnav-plus">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
    </button>
    <button class="bnav-fab" id="bnavFab"''',
    'P4 bouton +')

# ═══ P5 — pcNavSync : onglet Parcours seulement dans la sidebar desktop ═══
rep("  if(b) b.style.setProperty('display', diab?'flex':'none','important');",
    "  if(b) b.style.setProperty('display', (diab && window.matchMedia('(min-width:981px)').matches)?'flex':'none','important');",
    'P5 pcNavSync')

# ═══ P6 — Feuille « Accès rapides » (markup avant .app) ═══
rep('''<div class="app">
  <header>''',
    '''<div id="kpQuickBackdrop" onclick="kpQuickClose()" data-testid="kp-quick-backdrop"></div>
<div id="kpQuickSheet" role="dialog" aria-label="Accès rapides" data-testid="kp-quick-sheet">
  <div class="kpq-handle" onclick="kpQuickClose()"></div>
  <div class="kpq-title">Accès rapides</div>
  <div class="kpq-grid" id="kpQuickGrid"></div>
</div>

<div class="app">
  <header>''',
    'P6 quick sheet')

# ═══ P7 — CSS + JS module (inséré avant le module Parcours) ═══
MODULE = '''<style id="kpHomeStyles">
/* ═══ ACCUEIL v2 — header + dashboard + FAB (mockup) ═══ */
#kpHomeHeader{ display:none; align-items:center; justify-content:space-between; gap:10px; padding:2px 2px 0; }
.khh-left{ display:flex; align-items:center; gap:11px; min-width:0; }
.khh-logo{ width:48px; height:auto; flex:0 0 auto; }
.khh-titlewrap{ display:flex; flex-direction:column; align-items:flex-start; }
.khh-title{ font-family:'Plus Jakarta Sans',sans-serif; font-size:21.5px; font-weight:800; color:#2f6b2b; letter-spacing:-.02em; line-height:1.05; }
.khh-title em{ font-style:normal; color:#71a441; }
.khh-status{ margin-top:5px; display:inline-flex; align-items:center; gap:5px; border:1.5px solid rgba(94,124,97,.35); background:rgba(255,255,255,.75); color:#3c5a2c; border-radius:99px; padding:3px 12px; font-family:'Plus Jakarta Sans',sans-serif; font-size:10.5px; font-weight:800; letter-spacing:.12em; cursor:pointer; }
.khh-status.is-premium{ border-color:rgba(176,122,34,.5); color:#7a4f15; background:linear-gradient(135deg,#fbf3dd,#f6e7bd); }
.khh-bell{ position:relative; width:44px; height:44px; border-radius:50%; border:none; background:transparent; color:#2c342c; cursor:pointer; display:flex; align-items:center; justify-content:center; flex:0 0 auto; }
.khh-bell svg{ width:25px; height:25px; }
.khh-bell-dot{ position:absolute; top:9px; right:10px; width:8px; height:8px; border-radius:50%; background:#5b8a40; border:2px solid #f8f7f1; }
@media(max-width:980px){
  header .eyebrow, header #appTitle, header .brand-badge, header .kp-hero-date{ display:none !important; }
  header #headerLogoutBtn{ display:none !important; }
  #kpHomeHeader{ display:flex; }
}
/* ── Dashboard (mobile) ── */
#kpDashHost{ display:none; }
@media(max-width:980px){ #kpDashHost{ display:block; margin-bottom:16px; } }
.kpd-greet{ display:flex; align-items:center; justify-content:space-between; gap:6px; margin:4px 0 14px; }
.kpd-greet h2{ font-family:'Plus Jakarta Sans',sans-serif; font-size:26px; font-weight:800; color:#232b22; margin:0 0 6px; letter-spacing:-.02em; }
.kpd-greet p{ font-family:'Plus Jakarta Sans',sans-serif; font-size:14.5px; font-weight:500; line-height:1.4; color:#5c645a; margin:0; max-width:225px; }
.kpd-avo{ width:132px; height:auto; flex:0 0 auto; margin-right:-14px; filter:drop-shadow(0 10px 18px rgba(30,42,30,.18)); }
.kpd-card{ background:#fff; border:1px solid rgba(30,42,30,.05); border-radius:20px; padding:16px; margin-bottom:14px; box-shadow:0 12px 30px -22px rgba(30,42,30,.3); }
.kpd-card-title{ font-family:'Plus Jakarta Sans',sans-serif; font-size:16.5px; font-weight:700; color:#232b22; }
.kpd-stats{ display:grid; grid-template-columns:repeat(4,1fr); gap:6px; margin-top:14px; }
.kpd-stat{ text-align:center; min-width:0; }
.kpd-stat-ico{ width:46px; height:46px; margin:0 auto 8px; border-radius:50%; background:#fff; border:1px solid rgba(30,42,30,.08); box-shadow:0 6px 14px -8px rgba(30,42,30,.25); display:flex; align-items:center; justify-content:center; font-size:20px; }
.kpd-stat-val{ font-family:'Plus Jakarta Sans',sans-serif; font-size:17px; font-weight:800; color:#232b22; line-height:1.1; }
.kpd-stat-val small{ display:block; font-size:10px; font-weight:700; color:#6b7266; }
.kpd-stat-lab{ font-family:'Plus Jakarta Sans',sans-serif; font-size:11px; font-weight:600; color:#6b7266; margin-top:3px; }
.kpd-goal{ display:flex; align-items:center; gap:14px; justify-content:space-between; }
.kpd-goal p{ font-family:'Plus Jakarta Sans',sans-serif; font-size:13.5px; font-weight:500; line-height:1.45; color:#5c645a; margin:8px 0 0; max-width:200px; }
.kpd-ring{ position:relative; width:88px; height:88px; border-radius:50%; flex:0 0 auto; background:conic-gradient(#5b8a40 calc(var(--pct)*1%), #e7ecdd 0); display:flex; align-items:center; justify-content:center; }
.kpd-ring span{ width:66px; height:66px; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; font-family:'Plus Jakarta Sans',sans-serif; font-size:18px; font-weight:800; color:#232b22; }
.kpd-meals-head{ display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.kpd-seeall{ background:none; border:none; font-family:'Plus Jakarta Sans',sans-serif; font-size:13.5px; font-weight:700; color:#3f7d3a; cursor:pointer; padding:4px; }
.kpd-meals-scroll{ display:flex; gap:12px; overflow-x:auto; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; margin:0 -4px; padding:0 4px 2px; scrollbar-width:none; }
.kpd-meals-scroll::-webkit-scrollbar{ display:none; }
.kpd-meal{ flex:0 0 88%; scroll-snap-align:start; display:flex; gap:12px; align-items:center; background:#fbfaf6; border:1px solid rgba(30,42,30,.05); border-radius:16px; padding:10px; cursor:pointer; }
.kpd-meal-photo{ width:96px; height:96px; border-radius:12px; object-fit:cover; flex:0 0 auto; background:#eef0e4; display:flex; align-items:center; justify-content:center; font-size:36px; }
.kpd-meal-body{ min-width:0; }
.kpd-meal-name{ font-family:'Plus Jakarta Sans',sans-serif; font-size:14.5px; font-weight:700; line-height:1.3; color:#232b22; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.kpd-meal-badge{ display:inline-block; margin-top:6px; font-family:'Plus Jakarta Sans',sans-serif; font-size:10.5px; font-weight:700; color:#3c5a2c; background:#e9efdb; border-radius:8px; padding:3px 9px; }
.kpd-meal-meta{ display:flex; gap:12px; margin-top:7px; font-family:'Plus Jakarta Sans',sans-serif; font-size:11.5px; font-weight:600; color:#6b7266; }
.kpd-dots{ display:flex; gap:5px; justify-content:center; margin-top:10px; }
.kpd-dot{ width:6px; height:6px; border-radius:50%; background:#d8ddcc; transition:background .2s; }
.kpd-dot.on{ background:#5b8a40; }
/* ── FAB "+" barre mobile ── */
.bnav-plus{ display:none; }
@media(max-width:980px){
  .bottom-nav, .bottom-nav .bottom-nav-inner{ overflow:visible !important; }
  .bnav-plus{ display:flex; align-items:center; justify-content:center; width:56px; height:56px; border-radius:50%; border:none; margin-top:-24px; flex:0 0 auto;
    background:linear-gradient(135deg,#5b8a40,#3f6b2c); color:#fff;
    box-shadow:0 10px 22px -8px rgba(63,107,44,.65), inset 0 1px 0 rgba(255,255,255,.22); cursor:pointer; }
  .bnav-plus svg{ width:26px; height:26px; }
  .bnav-plus:active{ transform:scale(.94); }
  #nt-lpev, #nt-muscle{ display:none !important; }
}
/* ── Feuille « Accès rapides » ── */
#kpQuickBackdrop{ position:fixed; inset:0; background:rgba(20,28,18,.45); opacity:0; pointer-events:none; transition:opacity .28s ease; z-index:1195; }
#kpQuickSheet{ position:fixed; left:0; right:0; bottom:0; z-index:1200; background:#fbfaf5; border-radius:24px 24px 0 0;
  box-shadow:0 -18px 50px -20px rgba(20,28,18,.45); transform:translateY(105%); transition:transform .34s cubic-bezier(.16,1,.3,1);
  padding:8px 18px calc(20px + env(safe-area-inset-bottom)); }
body.kp-quick-open #kpQuickBackdrop{ opacity:1; pointer-events:auto; }
body.kp-quick-open #kpQuickSheet{ transform:translateY(0); }
.kpq-handle{ width:44px; height:5px; border-radius:99px; background:rgba(30,42,30,.15); margin:6px auto 12px; cursor:pointer; }
.kpq-title{ font-family:'Plus Jakarta Sans',sans-serif; font-size:17px; font-weight:800; color:#232b22; margin-bottom:14px; }
.kpq-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
.kpq-tile{ background:#eef2e2; border:1px solid rgba(30,42,30,.05); border-radius:18px; padding:17px 8px 14px; text-align:center; cursor:pointer; transition:transform .15s ease; }
.kpq-tile:active{ transform:scale(.95); }
.kpq-tile-ico{ font-size:27px; display:block; margin-bottom:8px; }
.kpq-tile-lab{ font-family:'Plus Jakarta Sans',sans-serif; font-size:12.5px; font-weight:700; color:#2c342c; display:block; }
</style>
<script id="kpHomeModule">
(function(){
var KPD_AVO='__AVO__';
function $id(i){ return document.getElementById(i); }

/* ── Feuille Accès rapides ── */
window.kpQuickOpen=function(){
  var g=$id('kpQuickGrid'); if(!g) return;
  var diab=false; try{ diab=(typeof kpDiabIsActive==='function')?kpDiabIsActive():false; }catch(e){}
  var tiles=[];
  if(diab){
    tiles.push({e:'🩸',l:'Diabète',k:'diab'});
    tiles.push({e:'💪',l:'Muscu',k:'muscle'});
    tiles.push({e:'🎓',l:'Formation',k:'parcours'});
  } else {
    tiles.push({e:'💪',l:'Muscu',k:'muscle'});
    tiles.push({e:'💊',l:'Compléments',k:'lpev'});
    tiles.push({e:'🛒',l:'Courses',k:'courses'});
  }
  g.innerHTML=tiles.map(function(t){
    return '<button type="button" class="kpq-tile" data-testid="kpq-'+t.k+'" onclick="kpQuickGo(\\''+t.k+'\\')"><span class="kpq-tile-ico">'+t.e+'</span><span class="kpq-tile-lab">'+t.l+'</span></button>';
  }).join('');
  document.body.classList.add('kp-quick-open');
};
window.kpQuickClose=function(){ document.body.classList.remove('kp-quick-open'); };
window.kpQuickGo=function(k){
  kpQuickClose();
  setTimeout(function(){
    try{
      if(k==='diab'){ if(typeof kpDiabEntryOpen==='function') kpDiabEntryOpen(); return; }
      if(k==='courses'){ if(typeof kpOpenShoppingCourses==='function') kpOpenShoppingCourses(); return; }
      switchTab(k);
    }catch(e){}
  },130);
};
(function(){
  var sy=null, sheet=$id('kpQuickSheet'); if(!sheet) return;
  sheet.addEventListener('touchstart',function(e){ sy=e.touches[0].clientY; },{passive:true});
  sheet.addEventListener('touchmove',function(e){ if(sy!=null && e.touches[0].clientY-sy>70){ sy=null; kpQuickClose(); } },{passive:true});
})();

/* ── Badge statut header ── */
window.kpSyncHomeStatus=function(){
  var t=$id('planStatusMobileTxt'), s=$id('kpHomeStatus'); if(!t||!s) return;
  var txt=(t.textContent||'').trim()||'Version Gratuite';
  var isP=/premium/i.test(txt);
  s.innerHTML=(isP?'👑 ':'🎁 ')+txt.replace(/version\\s*/i,'').toUpperCase();
  s.classList.toggle('is-premium',isP);
};

/* ── Dashboard « Résumé / Objectif / Repas du jour » ── */
function mealCard(r,badge){
  var key=r.cat+'-'+r.id;
  var ph=(typeof KP_RECIPE_PHOTOS!=='undefined'&&KP_RECIPE_PHOTOS.has(key))
    ? '<img class="kpd-meal-photo" src="'+KP_RECIPE_PHOTO_BASE+'/'+key+'.jpg" alt="" loading="lazy" onerror="this.outerHTML=\\'<div class=&quot;kpd-meal-photo&quot;>'+(r.emoji||'🥑')+'</div>\\'">'
    : '<div class="kpd-meal-photo">'+(r.emoji||'🥑')+'</div>';
  return '<div class="kpd-meal" onclick="openRecipe('+r.id+')" data-testid="kpd-meal-'+r.id+'">'+ph
    +'<div class="kpd-meal-body"><div class="kpd-meal-name">'+r.name+'</div>'
    +'<span class="kpd-meal-badge">'+badge+'</span>'
    +'<div class="kpd-meal-meta"><span>🌿 '+(r.carb!=null?r.carb:'–')+'g net</span><span>🔥 '+(r.kcal!=null?r.kcal:'–')+' kcal</span></div>'
    +'</div></div>';
}
window.kpRenderDashboard=function(){
  var host=$id('kpDashHost'); if(!host) return;
  try{ kpSyncHomeStatus(); }catch(e){}
  var fn=(typeof profile!=='undefined'&&profile&&profile.firstname)?' '+profile.firstname:'';
  var greet='<div class="kpd-greet"><div class="kpd-greet-txt"><h2>Bonjour'+fn+' ! 👋</h2><p>Prêt à atteindre vos objectifs en pleine santé ?</p></div><img class="kpd-avo" src="'+KPD_AVO+'" alt="" draggable="false"></div>';
  if(typeof menu==='undefined'||!menu||!menu.length){
    host.innerHTML=greet;
    return;
  }
  var di=(typeof TODAY_IDX!=='undefined')?TODAY_IDX:0;
  var d=menu[di]||menu[0];
  var meals=(typeof profile!=='undefined'&&profile&&profile.meals)||{breakfast:true,lunch:true,dinner:true};
  var m={fat:0,prot:0,carb:0};
  try{
    if(meals.breakfast&&d.bfast!=null) addRecipeMacros(BFAST_RECIPES[d.bfast],m);
    if(meals.lunch){ addRecipeMacros(recipeAtSlot(d,'lunchStarter'),m); addRecipeMacros(recipeAtSlot(d,'lunch'),m); addRecipeMacros(recipeAtSlot(d,'lunchDessert'),m); }
    if(meals.dinner){ addRecipeMacros(recipeAtSlot(d,'dinnerStarter'),m); addRecipeMacros(recipeAtSlot(d,'dinner'),m); addRecipeMacros(recipeAtSlot(d,'dinnerDessert'),m); }
  }catch(e){}
  var fatK=m.fat*9, protK=m.prot*4, carbK=m.carb*4, total=Math.round(fatK+protK+carbK);
  var fp=total>0?Math.round(fatK/total*100):0;
  var carbT=(typeof targets!=='undefined'&&targets&&targets.carb)?targets.carb:20;
  var kcalT=(typeof targets!=='undefined'&&targets)?Math.round((targets.fat||0)*9+(targets.prot||0)*4+(targets.carb||0)*4):1800;
  var carbG=Math.round(m.carb);
  var pctBudget=Math.min(100,Math.round(carbG/Math.max(carbT,1)*100));
  var carbScore=carbG<=carbT?100:Math.max(0,Math.round(carbT/carbG*100));
  var fatScore=Math.max(0,100-Math.abs(fp-72)*3);
  var kcalScore=Math.max(0,100-Math.round(Math.abs(total-kcalT)/Math.max(kcalT,1)*100));
  var obj=Math.round(carbScore*.5+fatScore*.25+kcalScore*.25);
  var resume='<div class="kpd-card" data-testid="kpd-resume"><div class="kpd-card-title">Résumé du jour</div><div class="kpd-stats">'
    +'<div class="kpd-stat"><div class="kpd-stat-ico">🌿</div><div class="kpd-stat-val"><small>Net</small>'+carbG+'g</div><div class="kpd-stat-lab">Glucides nets</div></div>'
    +'<div class="kpd-stat"><div class="kpd-stat-ico">💧</div><div class="kpd-stat-val">'+fp+'%</div><div class="kpd-stat-lab">Lipides</div></div>'
    +'<div class="kpd-stat"><div class="kpd-stat-ico">🔥</div><div class="kpd-stat-val">'+total+'<small>kcal</small></div><div class="kpd-stat-lab">Énergie</div></div>'
    +'<div class="kpd-stat"><div class="kpd-stat-ico">🎯</div><div class="kpd-stat-val">'+obj+'%</div><div class="kpd-stat-lab">Objectif</div></div>'
    +'</div></div>';
  var goal='<div class="kpd-card kpd-goal" data-testid="kpd-goal"><div><div class="kpd-card-title">Objectif du jour</div>'
    +'<p>Rester en dessous de '+carbT+'g de glucides nets</p></div>'
    +'<div class="kpd-ring" style="--pct:'+pctBudget+'"><span>'+pctBudget+'%</span></div></div>';
  var cards=[];
  try{
    if(meals.breakfast&&d.bfast!=null&&BFAST_RECIPES[d.bfast]) cards.push(mealCard(BFAST_RECIPES[d.bfast],'Petit-déj'));
    if(meals.lunch){ var lr=recipeAtSlot(d,'lunch'); if(lr) cards.push(mealCard(lr,'Déjeuner')); }
    if(meals.dinner){ var dr=recipeAtSlot(d,'dinner'); if(dr) cards.push(mealCard(dr,'Dîner')); }
  }catch(e){}
  var dots=cards.length>1?'<div class="kpd-dots" id="kpdDots">'+cards.map(function(_,i){return '<span class="kpd-dot'+(i===0?' on':'')+'"></span>';}).join('')+'</div>':'';
  var mealsCard=cards.length?('<div class="kpd-card" data-testid="kpd-meals"><div class="kpd-meals-head"><span class="kpd-card-title">Repas du jour</span>'
    +'<button type="button" class="kpd-seeall" onclick="setDayView(\\'day\\')" data-testid="kpd-seeall">Voir tout ›</button></div>'
    +'<div class="kpd-meals-scroll" id="kpdScroll">'+cards.join('')+'</div>'+dots+'</div>'):'';
  host.innerHTML=greet+resume+goal+mealsCard;
  var sc=$id('kpdScroll'), dt=$id('kpdDots');
  if(sc&&dt){
    sc.addEventListener('scroll',function(){
      var i=Math.round(sc.scrollLeft/Math.max(sc.firstChild?sc.firstChild.offsetWidth+12:1,1));
      var ds=dt.children;
      for(var j=0;j<ds.length;j++) ds[j].classList.toggle('on',j===i);
    },{passive:true});
  }
};

/* ── Hooks ── */
var _sw=window.switchTab;
window.switchTab=function(t){
  _sw(t);
  if(t==='plan'){ try{ kpRenderDashboard(); }catch(e){} }
};
if(typeof window.generateMenu==='function'){
  var _gm=window.generateMenu;
  window.generateMenu=function(){
    var r=_gm.apply(this,arguments);
    try{ kpRenderDashboard(); }catch(e){}
    return r;
  };
}
function boot(){ try{ kpRenderDashboard(); }catch(e){} }
if(document.readyState==='complete'||document.readyState==='interactive'){ setTimeout(boot,900); }
else document.addEventListener('DOMContentLoaded',function(){ setTimeout(boot,900); });
setInterval(function(){ try{ kpSyncHomeStatus(); }catch(e){} },12000);
})();
</script>

<script id="kpParcoursModule">'''
rep('<script id="kpParcoursModule">', MODULE.replace('__AVO__', AVO), 'P7 module home')

io.open(PATH, 'w', encoding='utf-8').write(src)
print('DONE', len(src))
