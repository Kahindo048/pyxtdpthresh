# Coût du premier appel (J.2.4)

`tools/first_call.py`, processus neuf, ajustement de 60 firmes de Hansen (n_boot = 29, grid_ci = 30), mesure du
séjour d'`import`, du premier et du second ajustement. Les noyaux sont compilés avec `cache=True`
(déjà en place avant ce point).

| Situation | `import pyxtdpthresh` | 1er ajustement | 2e ajustement |
|---|---:|---:|---:|
| Cache disque Numba vide (première utilisation sur la machine) | 0,03 s | 5,8 s | 0,76 s |
| Cache disque rempli (cas courant) | 0,03 s | 2,6 s | 0,73 s |

Décomposition du premier ajustement à cache rempli (imports faits à la demande) : `numpy` + `pandas`
0,7 s, `scipy` 1,1 s, `numba` 0,4 s, chargement du cache des noyaux environ 0,4 s. Ces
dépendances sont incompressibles ; `import pyxtdpthresh` ne charge rien tant qu'on n'appelle pas une
fonction (noms à chargement différé).

## Ce qui a été fait

* `pyxtdpthresh.warmup()` est public : il compile, ou charge depuis le cache disque, tous les noyaux de
  l'estimation. Vérifié : après `warmup()` sur un cache vide, le premier ajustement dure 0,88 s contre
  0,76 s pour le second (la compilation, environ 3,2 s, est payée dans `warmup()`).
* À conseiller après l'installation : `python -c "import pyxtdpthresh; pyxtdpthresh.warmup()"`.

## Limites

* Le cache est écrit à côté des modules (`__pycache__`) ; sur une installation en lecture seule, Numba
  utilise `NUMBA_CACHE_DIR`.
* Les 2,6 s à cache rempli sont surtout des importations : on ne peut les réduire sans retirer des
  dépendances.
