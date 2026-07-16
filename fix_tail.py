#!/usr/bin/env python3
"""Nettoie la fin corrompue de keto.html (restes d'écritures non tronquées)
et synchronise vers le backend. À exécuter APRÈS CHAQUE édition de keto.html."""
import sys

path = '/app/keto.html'
src = open(path, encoding='utf-8').read()

# Le fichier doit se terminer par: payload KP_RECIPE_DETAILS ... </script>\n</body>\n</html>
marker = 'window.KP_RECIPE_DETAILS='
i = src.rfind(marker)
if i == -1:
    print('ERREUR: payload KP_RECIPE_DETAILS introuvable'); sys.exit(1)
j = src.find('</html>', i)
if j == -1:
    print('ERREUR: </html> introuvable après le payload'); sys.exit(1)
clean = src[:j + len('</html>')] + '\n'
removed = len(src) - len(clean)
if removed > 0:
    open(path, 'w', encoding='utf-8').write(clean)
    print(f'Nettoyé: {removed} octets orphelins supprimés')
else:
    print('OK: aucune corruption détectée')

# Validation rapide du payload (doit finir par }}; avant </script>)
tail = clean[i:i+200]
end = clean[j-40:j]
assert '</script>' in end or '</script>' in clean[j-200:j], 'ATTENTION: structure fin de fichier suspecte'
print('Fin de fichier valide.')
