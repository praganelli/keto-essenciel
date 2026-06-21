SRC="/app/keto.html"
OUT="/app/backend/keto_preview.html"

CSS = """
<style id="kp-desktop-dashboard">
/* ═══════════════ DESKTOP — « Dashboard Naturo » (min-width:1024px) ═══════════════ */
@media (min-width:1024px){
  body{ background:#f1e9d6 !important; }
  body::after{ display:none !important; }
  body::before{ display:none !important; }

  /* ───────────── BARRE LATÉRALE GAUCHE ───────────── */
  .bottom-nav{
    position:fixed !important; left:0 !important; top:0 !important; bottom:0 !important; right:auto !important;
    width:272px !important; height:100vh !important; padding:0 !important; margin:0 !important;
    z-index:300 !important; display:block !important; transform:none !important;
    background:linear-gradient(180deg,#1d3022 0%,#263c27 50%,#324d38 100%) !important;
    box-shadow:16px 0 60px -28px rgba(0,0,0,.55) !important;
  }
  .bottom-nav-inner{
    flex-direction:column !important; align-items:stretch !important; justify-content:flex-start !important;
    height:100% !important; width:100% !important; max-width:none !important;
    background:transparent !important; border:none !important; box-shadow:none !important;
    border-radius:0 !important; gap:5px !important; padding:30px 18px 24px !important;
    backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
  }
  .bottom-nav-inner::before{
    content:"🌿  Le Keto" !important;
    font-family:'Fraunces',serif !important; font-size:27px !important; font-weight:600 !important;
    color:#f5ecd6 !important; letter-spacing:.005em !important;
    padding:4px 14px 20px !important; margin-bottom:8px !important;
    border-bottom:1px solid rgba(255,255,255,.12) !important;
  }
  .bottom-nav-pill{ display:none !important; }

  .bnav-tab{
    flex:0 0 auto !important; flex-direction:row !important; justify-content:flex-start !important;
    align-items:center !important; gap:15px !important; width:100% !important; height:auto !important;
    padding:13px 16px !important; border-radius:14px !important; opacity:1 !important;
    color:rgba(244,236,214,.78) !important;
    transition:background .2s ease,color .2s ease,transform .2s ease !important;
  }
  .bnav-tab .bnav-icon{ font-size:21px !important; width:26px !important; text-align:center !important; transform:none !important; }
  .bnav-tab .bnav-label{ font-size:15.5px !important; font-weight:600 !important; letter-spacing:.01em !important; opacity:1 !important; }
  .bnav-tab:hover{ background:rgba(255,255,255,.08) !important; color:#fdf8ec !important; }
  .bnav-tab.active{
    background:linear-gradient(100deg,rgba(255,255,255,.18),rgba(255,255,255,.08)) !important;
    color:#ffffff !important; box-shadow:inset 0 0 0 1px rgba(255,255,255,.14) !important;
  }
  .bnav-tab.active .bnav-icon{ transform:scale(1.08) !important; }
  /* Réglages + Déconnexion poussés en bas */
  .bnav-settings{ margin-top:auto !important; border-top:1px solid rgba(255,255,255,.1) !important; padding-top:16px !important; margin-bottom:2px !important; }
  .bnav-logout{ color:rgba(255,210,200,.85) !important; }
  .bnav-logout:hover{ background:rgba(255,120,100,.16) !important; color:#fff !important; }

  /* ───────────── ZONE DE CONTENU (pleine largeur) ───────────── */
  .app{
    margin:0 0 0 272px !important; max-width:none !important; width:auto !important;
    padding:38px 60px 84px !important; min-height:100vh !important;
    background:transparent !important; border:none !important; box-shadow:none !important; border-radius:0 !important;
  }
  /* En-tête en barre du haut, aligné à gauche */
  header{ text-align:left !important; align-items:flex-start !important; max-width:1180px !important; margin:0 0 6px !important; padding:4px 0 24px !important; }
  header h1{ font-size:38px !important; line-height:1.05 !important; text-align:left !important; }
  header .tagline, header p{ text-align:left !important; }

  /* Concept C — grilles larges */
  .lib-grid{ grid-template-columns:repeat(4,1fr) !important; gap:20px !important; }
  .week-grid{ gap:12px !important; }
  /* limite de lecture confortable pour les blocs pleine largeur */
  #tab-plan, #tab-library, #tab-suivi, #tab-profile{ max-width:1320px !important; }
}
@media (min-width:1540px){
  .lib-grid{ grid-template-columns:repeat(5,1fr) !important; }
}
</style>
"""

html = open(SRC, encoding="utf-8").read()
assert "</head>" in html
html = html.replace("</head>", CSS + "\n</head>", 1)
open(OUT, "w", encoding="utf-8").write(html)
print("preview built:", OUT, "size", len(html))
