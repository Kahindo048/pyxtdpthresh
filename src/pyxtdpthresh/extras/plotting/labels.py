"""Texts of the figures in English and French (layer 6)."""

from __future__ import annotations

from pyxtdpthresh._types import Lang

LABELS: dict[str, dict[str, str]] = {
    "threshold": {"en": "Threshold ({q})", "fr": "Seuil ({q})"},
    "criterion": {"en": "GMM criterion J", "fr": "Critère GMM J"},
    "profile_flat": {
        "en": "Flat profile: {share:.0f} % of the thresholds are within {gap:.1f} of the minimum",
        "fr": "Profil plat : {share:.0f} % des seuils sont à moins de {gap:.1f} du minimum",
    },
    "distance": {"en": "Bootstrap distance D", "fr": "Distance bootstrap D"},
    "ci_sample": {"en": "D (sample)", "fr": "D (échantillon)"},
    "ci_critical": {"en": "critical value", "fr": "valeur critique"},
    "ci_set": {
        "en": "{level:g} % confidence set",
        "fr": "ensemble de confiance à {level:g} %",
    },
    "unresolved": {"en": "not resolved", "fr": "non résolu"},
    "lin_x": {"en": "Bootstrap distance D*", "fr": "Distance bootstrap D*"},
    "lin_y": {"en": "Draws", "fr": "Tirages"},
    "lin_obs": {"en": "observed D = {d:.3g}", "fr": "D observée = {d:.3g}"},
    "lin_p": {"en": "p = {p:.3f}", "fr": "p = {p:.3f}"},
    "lin_p_missing": {
        "en": "p undefined (invalid draws)",
        "fr": "p non défini (tirages invalides)",
    },
    "coef_x": {
        "en": "Coefficient ({level:g} % confidence interval)",
        "fr": "Coefficient (intervalle de confiance à {level:g} %)",
    },
    "lower": {"en": "Lower regime", "fr": "Régime bas"},
    "change": {"en": "Change", "fr": "Changement"},
    "upper": {"en": "Upper regime", "fr": "Régime haut"},
    "observations": {"en": "Observations", "fr": "Observations"},
    "regime_lower": {
        "en": "lower regime\n{n} obs. ({share:.0f} %)",
        "fr": "régime bas\n{n} obs. ({share:.0f} %)",
    },
    "regime_upper": {
        "en": "upper regime\n{n} obs. ({share:.0f} %)",
        "fr": "régime haut\n{n} obs. ({share:.0f} %)",
    },
    "reference": {"en": "reference", "fr": "référence"},
    "robust_failed": {"en": "not estimated", "fr": "non estimé"},
    "robust_stability": {
        "en": "stability index {value:.2f}",
        "fr": "indice de stabilité {value:.2f}",
    },
    "outside": {
        "en": "{n} observations outside the window",
        "fr": "{n} observations hors de la fenêtre",
    },
    "gamma_set": {"en": "confidence set of the threshold", "fr": "ensemble de confiance du seuil"},
    "effect": {"en": "Effect of {var}", "fr": "Effet de {var}"},
    "contribution": {
        "en": "Contribution of {var}\n(relative to the threshold)",
        "fr": "Contribution de {var}\n(relative au seuil)",
    },
    "period": {"en": "Period", "fr": "Période"},
    "switch_share": {"en": "Share in the upper regime (%)", "fr": "Part du régime haut (%)"},
    "units": {"en": "Units", "fr": "Unités"},
    "always_lower": {"en": "always lower", "fr": "toujours bas"},
    "always_upper": {"en": "always upper", "fr": "toujours haut"},
    "switching": {"en": "change regime", "fr": "changent de régime"},
    "instruments": {"en": "Instruments", "fr": "Instruments"},
    "instruments_n": {"en": "N = {n} units", "fr": "N = {n} unités"},
    "residuals": {"en": "Transformed residuals", "fr": "Résidus transformés"},
    "residual_band": {"en": "median and quartiles", "fr": "médiane et quartiles"},
    "ar_stat": {"en": "AR test statistic", "fr": "Statistique du test AR"},
    "ar_p": {"en": "p = {p:.3f}", "fr": "p = {p:.3f}"},
    "mc_name": {
        "en": "n = {n}, T = {t}, jump = {jump}",
        "fr": "n = {n}, T = {t}, saut = {jump}",
    },
    "mc_name_linear": {"en": "n = {n}, T = {t}, linear", "fr": "n = {n}, T = {t}, linéaire"},
    "mc_coverage_x": {
        "en": "Coverage of the true value ({level:g} % intervals)",
        "fr": "Couverture de la vraie valeur (intervalles à {level:g} %)",
    },
    "mc_threshold": {"en": "Threshold", "fr": "Seuil"},
    "mc_slopes": {"en": "Slopes", "fr": "Pentes"},
    "mc_segments": {"en": "segments", "fr": "segments"},
    "mc_hull": {"en": "hull", "fr": "enveloppe"},
    "mc_slope_mean": {"en": "mean", "fr": "moyenne"},
    "mc_nominal": {"en": "nominal {level:g} %", "fr": "nominal {level:g} %"},
    "mc_no_threshold": {"en": "no threshold", "fr": "pas de seuil"},
    "mc_no_coverage": {"en": "no complete set", "fr": "aucun ensemble complet"},
    "mc_shift_x": {
        "en": "Shift c of the tested threshold (true threshold + c)",
        "fr": "Décalage c du seuil testé (vrai seuil + c)",
    },
    "mc_rejection_y": {"en": "Rejection rate", "fr": "Taux de rejet"},
    "mc_level": {"en": "level {alpha:g}", "fr": "niveau {alpha:g}"},
    "mc_estimate_x": {"en": "Estimated threshold", "fr": "Seuil estimé"},
    "mc_range": {
        "en": "median, quartiles and 5-95 % range",
        "fr": "médiane, quartiles et étendue 5-95 %",
    },
    "mc_truth": {"en": "true value", "fr": "vraie valeur"},
}


def label(key: str, lang: Lang, **fields: object) -> str:
    """Text ``key`` in ``lang`` with ``fields`` substituted."""
    return LABELS[key][lang].format(**fields)
