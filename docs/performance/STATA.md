# Python contre Stata 17 MP (J.3.1) — mesures appariées

`tools/paired_bench.ps1` : une exécution Stata, puis une exécution Python, en alternance (3 tours), pour
que les deux voient le même état de la machine. Même modèle des deux côtés : y sur son retard, seuil q,
différences premières, bootstrap wild B = 299, grid_ci = 100, une graine. Python : processus neuf,
échauffement sur 40 unités, puis **un** ajustement de taille réelle chronométré (le cas d'un utilisateur
qui lance l'estimation une fois).

| Taille | Stata (s) | Python (s) | Rapport (médiane) | Plage des rapports |
|---|---:|---:|---:|---:|
| Hansen 565 × 15 (117 instruments) | 37,1 | 3,26 | **×11,6** | 11,3 – 13,4 |
| N = 2 000, T = 8 (27 instruments) | 18,8 | 1,03 | **×18,2** | 17,4 – 18,4 |
| N = 10 000, T = 8 (27 instruments) | 80,2 | 2,74 | **×29,3** | 28,0 – 35,0 |

Politique de fils : un fil pour les noyaux Numba, la moitié des cœurs logiques (4 sur 8) pour BLAS.

## Pourquoi ces chiffres sont plus bas que ceux d'une première série (×21 / ×30 / ×54)

La première série comparait un Python **déjà chaud** (médiane de répétitions dans le même processus) à un
Stata mesuré **à un autre moment**, quand la machine était dans un état plus lent : le même do-file Stata
a pris 80 s puis 36 s sur Hansen, à quelques heures d'intervalle. Les temps absolus ne se comparent donc
qu'à l'intérieur d'un même tour ; ce document ne retient que le rapport apparié.

## Lecture

* Les cibles du PLAN (×10 sur la recherche de seuil, ×20 sur les bootstraps) : le total avec bootstrap,
  où le bootstrap pèse plus de 80 %, donne ×11,6 à Hansen, ×18,2 à N = 2 000 et ×29,3 à N = 10 000. La
  cible ×20 sur le bootstrap n'est donc **atteinte qu'à grand N** ; à Hansen elle ne l'est pas.
* À Hansen (117 instruments), le temps est dans le produit matriciel du critère non restreint
  (≈ 90 Gflops mesurés, près du pic) ; aucun gain exact n'est connu (`GOULOTS.md`).
* La recherche de seuil seule n'est pas mesurable séparément côté Stata : la cible ×10 s'apprécie sur le
  total hors bootstrap, mesuré dans la première série (×18 à ×34, non appariée).
