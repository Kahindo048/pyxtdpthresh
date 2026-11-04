# Optimisations de la séance J (J.2.3, J.2.4, bootstrap par unités)

Toutes les mesures ci-dessous sont **comparatives dans une même séance** : le temps absolu d'un même
code varie avec l'état de la machine (Hansen : 3,8 s puis 5,2 s à quelques heures d'intervalle).
Aucun changement ne modifie les résultats : les tests golden contre Stata (bootstrap : 307 + 339
cas) passent.

## 1. Copies supprimées dans la boucle des candidats (J.2.3) — fait

| Changement | Où |
|---|---|
| Valeurs ajustées `X(γ)θ` transformées en **une** colonne au lieu de `p` (la transformation est linéaire) | `Stack.fitted` |
| `Z'F/n` lu dans le cache des moments des candidats (`(Z'X(γ)/n) θ`) au lieu d'un produit `Z'a` | `_Inversion.distances` |
| Index `int64` du CSR de `Z` construits une fois et non à chaque appel de `unit_moments` | `InstrumentMatrix.csr64`, `unit_moments_arrays` |

Mesure (A/B, 5 répétitions, bootstrap wild B = 299, grid_ci = 100) : Hansen 5,2–5,3 s → 5,0–5,1 s (−4 %) ;
N = 10 000 : 4,0 s → 2,87 s (**−28 %**). Équivalence : `tests/unit/test_fitted_equivalence.py` (24 tests,
FD, FOD, effets temporels, kink, collapse).

## 2. Premier appel (J.2.4) — fait

`pyxtdpthresh.warmup()` public ; voir `PREMIER_APPEL.md` (5,8 s à cache vide, 2,6 s à cache rempli, dont
1,6 s d'imports incompressibles).

## 3. Bootstrap par unités (algorithme 1 de Gong-Seo) — deux noyaux Numba

Cas : 150 firmes de Hansen, collapse, B = 99, grid_ci = 40. **Stata : 71 s** (3 répétitions, 70,5 à 74,4 s).

| Étape | Python (s) |
|---|---:|
| Avant | 11,3 |
| + noyau `profile_rows` (minimum du profil, boucle Python) | 10,6 |
| + noyau `syminv_many` (matrices p×p, 780 000 par exécution : 6,4 s → 1,5 s) | 8,6 |
| + un seul fil Numba (voir 4) | 5,3 |

* Le profil cProfile surestimait la boucle Python `profile_min` (764 000 appels de `objtol`) : le gain réel
  du noyau est de 6 %, pas de 27 %. **Mesurer sans profileur avant de choisir.**
* `kernels/profile.py`, `kernels/syminv.py` et leurs références NumPy (`kernels/reference/`) ; tests
  `test_profile_kernel.py` (16) et `test_syminv_kernel.py` (11) : décisions d'admission identiques à la
  référence sur des milliers de matrices (y compris près de la limite de conditionnement 1e12), inverses
  à moins de 0,4 · cond · eps, accord avec `NUMBA_DISABLE_JIT=1`.

## 4. Politique de fils — **appliquée** (J.2.2)

`blas_threads()` donnait à BLAS la moitié des fils Numba (4 sur 8) ; les fils Numba restent actifs
(attente active) et se disputent les cœurs avec BLAS. Nouvelle politique : **un fil** pour les noyaux
Numba (`KERNEL_THREADS`), et l'option `threads` borne les fils BLAS, **la moitié des cœurs logiques par
défaut**. Mesure (bootstrap wild complet, médiane de 3 répétitions dans un même processus) :

| Taille | ancien défaut | Numba 1, BLAS 1 | Numba 1, BLAS 4 | Numba 1, BLAS 8 |
|---|---:|---:|---:|---:|
| Hansen | 5,41 | 4,39 | 3,16 | 2,90 |
| N = 2 000 | 1,49 | 0,96 | 0,85 | 1,13 |
| N = 10 000 | 3,00 | 2,29 | 1,94 | 2,00 |
| Unités, 150 firmes | 7,94 | 5,35 | 5,25 | 5,35 |
| Wild, 150 firmes | 0,55 | 0,20 | 0,21 | 0,22 |

Mais en **processus neuf** (premier ajustement de taille réelle), 8 fils BLAS pénalisent le premier appel
(N = 2 000 : 1,7–1,9 s contre 0,9 s au second), alors que 4 fils donnent le même temps au premier et au
second (≈ 1,0 s) : d'où le défaut « moitié des cœurs logiques » plutôt que « tous les cœurs ». Hansen en
processus neuf : 4,4–4,9 s (1 fil), 3,7 (2), 3,2 (4), 3,0–4,0 (8). Sans changer un résultat (l'ordre de
sommation de BLAS bouge à 1e-16 près).

Leçon : mesurer en processus neuf, pas seulement en répétant dans un processus chaud.

## 5. Mémoire (J.2.1, J.2.5) et garde de vitesse (J.3.3)

* Pic mesuré (tracemalloc), T = 8, 27 instruments conservés : 17 Mo à N = 2 000, 83 Mo à N = 10 000,
  415 Mo à N = 50 000 ; le pic est atteint à la construction de la pile, pas au bootstrap. Il vaut
  environ 3 copies de la matrice d'instruments **brute** (avant nettoyage). Estimation et mesure :
  0,97 à 1,03 sur quatre configurations (jusqu'à 621 Mo à N = 20 000, T = 12), mais 2,3 fois trop avec
  `collapse` (estimation prudente).
* Aucun découpage par blocs n'est nécessaire à N = 50 000 ; à N = 1 000 000 le pic serait d'environ
  8 Go : l'avertissement `warn_memory_high` (au-dessus de 8 Go) le signale avant le calcul.
* `tests/benchmarks/` : voir `test_speed.py`. Exemple d'utilisation : `pytest -m bench`.
* Le noyau `syminv_many`, sur un seul fil, n'est plus que ×1,3 à ×1,9 plus rapide que NumPy (×7 avec huit
  fils) ; il ramène néanmoins le bootstrap par unités de 150 firmes de ≈ 6,8 s à ≈ 5,6 s. Un calcul du
  conditionnement moins cher (norme 1) irait plus vite, mais élargirait l'écart de décision avec Stata
  près de la limite 1e12 : non fait.
