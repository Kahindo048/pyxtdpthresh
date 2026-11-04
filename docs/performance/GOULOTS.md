# Tableau des goulots (J.1.2) — proposition à valider

Source : `cprofile_*.txt` (profil), `STATA.md` (cibles), et deux micro-mesures (scratchpad, non conservées).
Cibles du PLAN : ×10 sur la recherche de seuil, ×20 sur les bootstraps ; atteintes (×28 à ×67 et ×20 à ×52).

| # | Goulot | Où | Part (Hansen / N = 10 000) | Nature | Choix proposé |
|---|---|---|---|---|---|
| 1 | Critère « non restreint » recalculé pour chacun des 99 candidats | `criterion` ← `_Inversion.distances` | 2,6 s sur 5,3 s / 0,3 s | Flops : G·L²·B par candidat, soit 8·10¹⁰ au total. Le produit `Q·m` tourne déjà à environ 90 Gflops (9,2 ms avec 8 fils pour 8,2·10⁸ opérations), donc près du pic de la machine | **Aucun gain exact connu.** La séparation `m = a_c + v_b` proposée d'abord est **invalide** : le résidu `dy − X(γ_c)θ_c` dépend du candidat, donc `v_b` aussi (le prototype supposait `v_b` commun ; ×10 sans objet). Pistes restantes, toutes à valider : float32 (≈ ×2, perd de la précision), élagage des candidats (non exact sans borne), ou ne rien faire |
| 2 | Moments des tirages `U'η` répétés par candidat | `sample_moments` | 0,13 s / 0,84 s | Algorithme | Mise à jour incrémentale le long des γ triés (seules les lignes qui changent de régime) : gain réel à grand N, plus délicat. À étudier après #1 |
| 3 | Copies et conversions | `astype`, `transform_levels`, `rmatmul`, `unit_moments` | 0,05 s / 1,4 s | Copies | J.2.3 : stockage contigu, pas de conversion répétée ; aucun noyau nouveau |
| 4 | Bootstrap par unités (Gong-Seo) | `unit_bootstrap.py` | environ ×80 le wild | Algorithme + Numba | Profil dédié avant tout choix (ce n'est pas le défaut) |
| 5 | Premier appel (compilation) | kernels | non mesuré | Compilation | J.2.4 : `warmup()` + cache disque ; mesure du premier appel |
| 6 | Pile (instruments, poids) | `build_stack` | 0,13 s / 0,40 s | — | Rien à faire : < 10 % du total |

Correction (même séance) : le point 1 n'a pas de gain algébrique exact connu ; l'ordre de grandeur de
8·10¹⁰ opérations est inhérent à l'algorithme de Stata (minimum sur toute la grille, pour chaque
candidat et chaque tirage). Les cibles du PLAN étant atteintes, rien n'est modifié dans le code.
