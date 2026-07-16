#!/usr/bin/env python3
"""Injecte (ou remplace) le module Parcours (Formation Diabète) dans keto.html.
Idempotent : remplace le bloc entre KP-PARCOURS-START/END s'il existe déjà."""
import sys

KETO = '/app/keto.html'
FRAG = '/app/parcours_module.html'
ANCHOR = '<script id="kpRecipeDetailsData">'
START = '<!-- KP-PARCOURS-START -->'
END = '<!-- KP-PARCOURS-END -->'

src = open(KETO, encoding='utf-8').read()
frag = open(FRAG, encoding='utf-8').read().strip()

if START in src and END in src:
    i = src.index(START)
    j = src.index(END) + len(END)
    src = src[:i] + frag + src[j:]
    print('Bloc Parcours REMPLACÉ')
else:
    if ANCHOR not in src:
        print('ERREUR: ancre kpRecipeDetailsData introuvable'); sys.exit(1)
    i = src.index(ANCHOR)
    src = src[:i] + frag + '\n\n' + src[i:]
    print('Bloc Parcours INSÉRÉ avant le payload recettes')

open(KETO, 'w', encoding='utf-8').write(src)
print('OK — keto.html mis à jour (%d octets)' % len(src))
