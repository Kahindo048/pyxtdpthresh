"""Texts of the diagnostic report in English and French: each alert and what to do about it."""

from __future__ import annotations

#: code -> language -> (message, recommendation); ``str.format`` fields are filled at run time.
TEXTS: dict[str, dict[str, tuple[str, str]]] = {
    "iv_more_than_units": {
        "en": (
            "{n_iv} instruments for {n_units} units: with more instruments than units the Hansen "
            "test loses its power and the weight matrix is poorly estimated.",
            "Reduce the instruments: {levers}.",
        ),
        "fr": (
            "{n_iv} instruments pour {n_units} unités : avec plus d'instruments que d'unités, le "
            "test de Hansen perd sa puissance et la matrice de poids est mal estimée.",
            "Réduire les instruments : {levers}.",
        ),
    },
    "iv_high_ratio": {
        "en": (
            "{n_iv} instruments for {n_units} units (ratio {ratio:.2f}): the instrument count is "
            "high compared with the number of units.",
            "Check that the Hansen p-value is not driven by the count ({levers}).",
        ),
        "fr": (
            "{n_iv} instruments pour {n_units} unités (ratio {ratio:.2f}) : le nombre "
            "d'instruments est élevé au regard du nombre d'unités.",
            "Vérifier que la p-value de Hansen ne tient pas au nombre d'instruments ({levers}).",
        ),
    },
    "hansen_near_one": {
        "en": (
            "The Hansen p-value is {p:.3f}, very close to 1: the test is probably too weak to "
            "detect invalid instruments.",
            "Try fewer instruments ({levers}) and see whether the p-value falls.",
        ),
        "fr": (
            "La p-value de Hansen vaut {p:.3f}, très proche de 1 : le test est probablement trop "
            "faible pour détecter des instruments invalides.",
            "Essayer moins d'instruments ({levers}) et voir si la p-value baisse.",
        ),
    },
    "hansen_rejected": {
        "en": (
            "The Hansen test rejects the over-identifying restrictions (p = {p:.3f}): some "
            "instruments may be invalid or the model misspecified.",
            "Restrict the instrument lags (maxlag) or treat suspect variables as exogenous or "
            "predetermined only if the economics allows it.",
        ),
        "fr": (
            "Le test de Hansen rejette les restrictions de sur-identification (p = {p:.3f}) : "
            "certains instruments peuvent être invalides ou le modèle mal spécifié.",
            "Restreindre les retards des instruments (maxlag), ou ne traiter des variables "
            "suspectes comme exogènes ou prédéterminées que si l'économie le justifie.",
        ),
    },
    "ar2_rejected": {
        "en": (
            "The AR(2) test rejects the absence of second-order serial correlation in the "
            "differenced residuals (p = {p:.3f}): lagged levels may not be valid instruments.",
            "Start the instruments one lag deeper (for example maxlag=(3, 8)) or add dynamics.",
        ),
        "fr": (
            "Le test AR(2) rejette l'absence d'autocorrélation d'ordre 2 des résidus en différence "
            "(p = {p:.3f}) : les niveaux retardés peuvent ne pas être des instruments valides.",
            "Commencer les instruments un retard plus loin (par exemple maxlag=(3, 8)) ou ajouter "
            "de la dynamique.",
        ),
    },
    "gamma_at_edge": {
        "en": (
            "The estimated threshold {gamma:.4f} sits at the {side} edge of the search grid "
            "[{low:.4f}, {high:.4f}]: the true minimum may lie beyond it.",
            "Widen the search by lowering trim, or check the distribution of {q}.",
        ),
        "fr": (
            "Le seuil estimé {gamma:.4f} est au bord {side} de la grille de recherche "
            "[{low:.4f}, {high:.4f}] : le vrai minimum peut se trouver au-delà.",
            "Élargir la recherche en réduisant trim, ou examiner la distribution de {q}.",
        ),
    },
    "ci_boundary": {
        "en": (
            "The confidence set of the threshold reaches the {side} edge of the candidates: it is "
            "cut by the grid, not by the data.",
            "Widen the grid (lower trim) before reading the interval.",
        ),
        "fr": (
            "L'ensemble de confiance du seuil atteint le bord {side} des candidats : il est borné "
            "par la grille, non par les données.",
            "Élargir la grille (réduire trim) avant de lire l'intervalle.",
        ),
    },
    "ci_empty": {
        "en": (
            "No candidate threshold is accepted: the confidence set is empty.",
            "Increase grid_ci and n_boot, and check the specification.",
        ),
        "fr": (
            "Aucun seuil candidat n'est accepté : l'ensemble de confiance est vide.",
            "Augmenter grid_ci et n_boot, et vérifier la spécification.",
        ),
    },
    "ci_incomplete": {
        "en": (
            "{n} candidate thresholds could not be tested, so the confidence set is incomplete "
            "and its bounds are withheld.",
            "Increase n_boot or reduce the instruments ({levers}) so that every candidate can be "
            "solved.",
        ),
        "fr": (
            "{n} seuils candidats n'ont pas pu être testés : l'ensemble de confiance est "
            "incomplet et ses bornes ne sont pas données.",
            "Augmenter n_boot ou réduire les instruments ({levers}) pour que tous les candidats "
            "se résolvent.",
        ),
    },
    "ci_multiple": {
        "en": (
            "The confidence set of the threshold has {n} separate intervals: the data support "
            "several distant thresholds.",
            "Report the segments, not only their hull, and look at plot(fit, 'ci').",
        ),
        "fr": (
            "L'ensemble de confiance du seuil compte {n} intervalles séparés : les données "
            "soutiennent plusieurs seuils éloignés.",
            "Donner les segments et pas seulement leur enveloppe, et regarder plot(fit, 'ci').",
        ),
    },
    "ci_wide": {
        "en": (
            "The confidence set covers {share:.0f} % of the search grid: the threshold is weakly "
            "identified.",
            "Treat the threshold with caution; more units, a longer panel or a more variable {q} "
            "would help.",
        ),
        "fr": (
            "L'ensemble de confiance couvre {share:.0f} % de la grille de recherche : le seuil "
            "est faiblement identifié.",
            "Prendre le seuil avec prudence ; plus d'unités, un panel plus long ou un {q} plus "
            "variable aideraient.",
        ),
    },
    "ci_grid_coarse": {
        "en": (
            "The confidence set of the threshold is {width:.3g} wide, {steps:.1f} steps of its "
            "grid of {n_grid} points: the grid is too coarse for an interval this narrow.",
            "Increase grid_ci (for example to {suggested}); a coarse grid can leave the true "
            "threshold between two points and the interval under-covers.",
        ),
        "fr": (
            "L'ensemble de confiance du seuil a une largeur de {width:.3g}, soit {steps:.1f} pas "
            "de sa grille de {n_grid} points : la grille est trop grossière pour un intervalle "
            "aussi étroit.",
            "Augmenter grid_ci (par exemple à {suggested}) ; une grille grossière peut laisser "
            "le vrai seuil entre deux points et l'intervalle sous-couvre.",
        ),
    },
    "profile_flat": {
        "en": (
            "The criterion profile is flat: {share:.0f} % of the thresholds are within {gap:.1f} "
            "of the minimum.",
            "The estimated threshold is not sharply determined; compare it with the confidence "
            "set and plot(fit, 'profile').",
        ),
        "fr": (
            "Le profil du critère est plat : {share:.0f} % des seuils sont à moins de {gap:.1f} "
            "du minimum.",
            "Le seuil estimé n'est pas nettement déterminé ; le comparer à l'ensemble de "
            "confiance et à plot(fit, 'profile').",
        ),
    },
    "grid_sensitive": {
        "en": (
            "Another threshold, {other:.4f}, fits almost as well as {gamma:.4f} (criterion "
            "within {gap:.1f}): the estimate can jump from one to the other with the grid.",
            "Refine the grid (grid=, refine=) and check that the conclusions hold at both.",
        ),
        "fr": (
            "Un autre seuil, {other:.4f}, ajuste presque aussi bien que {gamma:.4f} (critère à "
            "moins de {gap:.1f}) : l'estimation peut passer de l'un à l'autre selon la grille.",
            "Raffiner la grille (grid=, refine=) et vérifier que les conclusions tiennent aux "
            "deux.",
        ),
    },
    "regime_small": {
        "en": (
            "The {regime} regime has only {n_obs} equations ({share:.1f} %) from {n_units} units.",
            "Raise minregime or move the threshold range (trim) so that each regime keeps enough "
            "observations.",
        ),
        "fr": (
            "Le régime {regime} ne compte que {n_obs} équations ({share:.1f} %) issues de "
            "{n_units} unités.",
            "Relever minregime ou déplacer la plage du seuil (trim) pour que chaque régime garde "
            "assez d'observations.",
        ),
    },
    "q_few_values": {
        "en": (
            "The threshold variable {q} takes only {n} distinct values: the grid and the "
            "bandwidth of the variance are poorly defined.",
            "Use a threshold variable with more variation, or interpret the threshold as one of "
            "a few categories.",
        ),
        "fr": (
            "La variable de seuil {q} ne prend que {n} valeurs distinctes : la grille et la "
            "fenêtre de la variance sont mal définies.",
            "Utiliser une variable de seuil plus variable, ou lire le seuil comme une séparation "
            "entre quelques catégories.",
        ),
    },
    "fd_unbalanced": {
        "en": (
            "The panel is unbalanced and the first-difference transformation loses an equation "
            "at every gap.",
            "Use method='fod' (forward orthogonal deviations), which keeps more observations.",
        ),
        "fr": (
            "Le panel n'est pas cylindré et la transformation en différences premières perd une "
            "équation à chaque trou.",
            "Utiliser method='fod' (écarts orthogonaux), qui garde plus d'observations.",
        ),
    },
    "one_step": {
        "en": (
            "The estimate stays at one step: the second-step weight could not be used.",
            "Reduce the instruments ({levers}); the Hansen test is not available at one step.",
        ),
        "fr": (
            "L'estimation reste à un pas : la matrice de poids du second pas n'a pas pu être "
            "utilisée.",
            "Réduire les instruments ({levers}) ; le test de Hansen n'existe pas à un pas.",
        ),
    },
    "weight_fallback": {
        "en": (
            "The first-step weight fell back to {fallback}: the moments are close to collinear.",
            "Reduce the instruments ({levers}) so that the usual weight can be built.",
        ),
        "fr": (
            "La matrice de poids du premier pas est retombée sur {fallback} : les moments sont "
            "presque colinéaires.",
            "Réduire les instruments ({levers}) pour pouvoir construire la matrice habituelle.",
        ),
    },
    "continuity_kink": {
        "en": (
            "The continuity test does not reject a kink against the jump (p = {p:.3f}).",
            "A continuous threshold effect (kink=True) is a more parsimonious description.",
        ),
        "fr": (
            "Le test de continuité ne rejette pas un kink contre le saut (p = {p:.3f}).",
            "Un effet de seuil continu (kink=True) est une description plus parcimonieuse.",
        ),
    },
    "continuity_jump": {
        "en": (
            "The continuity test rejects a kink in favour of the jump (p = {p:.3f}).",
            "Keep the jump model.",
        ),
        "fr": (
            "Le test de continuité rejette le kink au profit du saut (p = {p:.3f}).",
            "Garder le modèle à saut.",
        ),
    },
    "levers_collapse": {"en": ("collapse=True", ""), "fr": ("collapse=True", "")},
    "levers_maxlag": {
        "en": ("limit the lags with maxlag=(2, 4)", ""),
        "fr": ("limiter les retards avec maxlag=(2, 4)", ""),
    },
    "levers_fewer": {
        "en": ("use fewer endogenous or predetermined variables", ""),
        "fr": ("réduire le nombre de variables endogènes ou prédéterminées", ""),
    },
    "side_lower": {"en": ("lower", ""), "fr": ("inférieur", "")},
    "side_upper": {"en": ("upper", ""), "fr": ("supérieur", "")},
    "side_both": {"en": ("lower and upper", ""), "fr": ("inférieur et supérieur", "")},
    "fallback_1": {"en": ("(Z'Z)^-1", ""), "fr": ("(Z'Z)^-1", "")},
    "fallback_2": {"en": ("the identity matrix", ""), "fr": ("la matrice identité", "")},
    "regime_lower": {"en": ("lower", ""), "fr": ("bas", "")},
    "regime_upper": {"en": ("upper", ""), "fr": ("haut", "")},
    "none": {
        "en": ("No alert: nothing in the diagnostics calls for action.", ""),
        "fr": ("Aucune alerte : rien dans les diagnostics n'appelle d'action.", ""),
    },
    "header": {
        "en": ("Diagnostic report: {warnings} warning(s), {notices} notice(s)", ""),
        "fr": ("Rapport de diagnostic : {warnings} alerte(s), {notices} remarque(s)", ""),
    },
    "recommendation": {"en": ("Recommendation:", ""), "fr": ("Recommandation :", "")},
    "warning": {"en": ("warning", ""), "fr": ("alerte", "")},
    "notice": {"en": ("notice", ""), "fr": ("remarque", "")},
}
