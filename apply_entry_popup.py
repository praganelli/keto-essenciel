#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du jour → bouton + popup contenant le carrousel/sliders, reset après enregistrement."""
src = open('/app/keto.html', encoding='utf-8').read()

# ── 1. Markup : bouton + historique dans la carte ; wizard déplacé dans un popup ──
sec_start = '<div class="sec-label" style="margin-top:20px">✍️ Saisie du jour</div>\n      <div class="card"><div class="card-body">'
assert src.count(sec_start) == 1
wiz_start = src.index('<div class="diab-wiz-tabs" id="diabWizTabs">')
save_btn = '<button class="btn btn-primary" onclick="kpDiabSave()" data-testid="diab-save" style="width:100%;margin-top:10px">+ Enregistrer ma journée</button>'
assert src.count(save_btn) == 1
wiz_end = src.index(save_btn) + len(save_btn)
wizard_html = src[wiz_start:wiz_end]

hist_block = '<div id="diabHistory" style="margin-top:14px"></div>\n      </div></div>'
assert src.count(hist_block) == 1

new_section = sec_start.replace('<div class="card"><div class="card-body">', '') + """
      <div class="card"><div class="card-body">
        <button class="btn btn-primary" onclick="kpDiabEntryOpen()" data-testid="diab-entry-open" style="width:100%;font-size:14px">✍️ Saisie du jour</button>
        <div id="diabHistory" style="margin-top:14px"></div>
      </div></div>
      <!-- ═══ Popup Saisie du jour (carrousel 3 étapes + curseurs) ═══ -->
      <div id="diabEntryOverlay" onclick="if(event.target===this)kpDiabEntryClose()" style="display:none;position:fixed;inset:0;z-index:100000;background:rgba(20,26,20,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);align-items:center;justify-content:center;padding:16px">
        <div style="background:var(--card,#fff);border-radius:20px;max-width:470px;width:100%;max-height:88vh;overflow-y:auto;padding:22px 18px 18px;position:relative;box-shadow:0 24px 60px -20px rgba(0,0,0,.4)">
          <button onclick="kpDiabEntryClose()" data-testid="diab-entry-close" aria-label="Fermer" style="position:absolute;top:10px;right:12px;background:transparent;border:none;font-size:24px;line-height:1;color:var(--muted);cursor:pointer;padding:4px 8px">×</button>
          <div style="font-family:'Fraunces',Georgia,serif;font-size:19px;font-weight:600;color:var(--text,#1e2a1e);margin-bottom:14px">✍️ Saisie du jour</div>
          """ + wizard_html + """
        </div>
      </div>"""

# Remplace du début de section jusqu'à la fin du bouton save, puis supprime l'ancien bloc historique isolé
sec_idx = src.index(sec_start)
src = src[:sec_idx] + new_section + src[wiz_end:]
# l'ancien "diabHistory + fermeture carte" qui suivait le bouton save doit disparaître (il reste orphelin)
old_tail = '\n        <div id="diabHistory" style="margin-top:14px"></div>\n      </div></div>'
assert src.count(old_tail) == 1
src = src.replace(old_tail, '', 1)

# ── 2. JS : open / close / reset ──
js_anchor = "window.kpDiabWizGo = kpDiabWizGo;"
assert src.count(js_anchor) == 1
js_new = js_anchor + """
/* ─── Popup Saisie du jour : ouverture, fermeture, remise à zéro ─── */
function kpDiabEntryReset(){
  try{
    ['diabMeds','diabMedsMatin','diabMedsMidi','diabMedsSoir','diabInsMatin','diabInsMidi','diabInsSoir','diabSideFx','diabSteps','diabWater','diabSleep'].forEach(function(id){
      var e=document.getElementById(id); if(e) e.value='';
    });
    KP_GLY_FIELDS.forEach(function(f){
      var n=document.getElementById('diabGly_'+f[0]); if(n) n.value='';
      var s=document.getElementById('diabGlyS_'+f[0]); if(s) s.value=110;
    });
    var sd={diabStepsS:6000, diabWaterS:1.5, diabSleepS:7};
    Object.keys(sd).forEach(function(id){ var s=document.getElementById(id); if(s) s.value=sd[id]; });
    kpDiabTgl('med', false); kpDiabTgl('ins', false);
    var mi=document.getElementById('diabMissed'); if(mi) mi.checked=false;
    var co=document.getElementById('diabCarbsOk'); if(co) co.checked=false;
    try{ if(typeof _diabMood!=='undefined' && _diabMood) kpDiabSetMood(_diabMood); }catch(e){}
  }catch(e){}
}
function kpDiabEntryOpen(){
  var ov=document.getElementById('diabEntryOverlay');
  if(!ov) return;
  if(ov.parentNode!==document.body) document.body.appendChild(ov);
  kpDiabEntryReset();
  try{ kpDiabPrefillFromQuiz(); }catch(e){}
  kpDiabWizGo(0);
  ov.style.display='flex';
}
function kpDiabEntryClose(){
  var ov=document.getElementById('diabEntryOverlay');
  if(ov) ov.style.display='none';
}
window.kpDiabEntryReset=kpDiabEntryReset; window.kpDiabEntryOpen=kpDiabEntryOpen; window.kpDiabEntryClose=kpDiabEntryClose;"""
src = src.replace(js_anchor, js_new)

open('/app/keto.html', 'w', encoding='utf-8').write(src)
print('OK')
