"""English and French message catalogue (layer 0).

Every user-facing message is registered here under a stable key, so that a message can be
translated or reworded without touching the code that raises it.
"""

from __future__ import annotations

from ._config import get_options
from ._types import Lang

#: key -> {language: template}.  Templates use ``str.format`` placeholders.
_CATALOGUE: dict[str, dict[str, str]] = {
    "not_balanced": {
        "en": "The data are not a strongly balanced panel (required by xthenreg).",
        "fr": "Les données ne forment pas un panel strictement cylindré (exigé par xthenreg).",
    },
    "no_complete_unit": {
        "en": "No unit is observed in every period.",
        "fr": "Aucune unité n'est observée à toutes les périodes.",
    },
    "missing_values": {
        "en": "Missing values in variable(s) {variables}.",
        "fr": "Valeurs manquantes dans la ou les variables {variables}.",
    },
    "unknown_option": {
        "en": "Unknown option(s): {names}.",
        "fr": "Option(s) inconnue(s) : {names}.",
    },
    "variable_not_found": {
        "en": "Variable '{name}' not found in the data.",
        "fr": "Variable « {name} » introuvable dans les données.",
    },
    "quantile_missing": {
        "en": "Missing values are not allowed when computing quantiles.",
        "fr": "Les valeurs manquantes ne sont pas permises pour calculer des quantiles.",
    },
    "q_too_few": {
        "en": "The threshold variable has too few usable values.",
        "fr": "La variable de seuil a trop peu de valeurs utilisables.",
    },
    "q_no_variation": {
        "en": "The threshold variable has insufficient variation on the effective GMM sample.",
        "fr": "La variable de seuil varie trop peu sur l'échantillon effectif du GMM.",
    },
    "minregime_no_split": {
        "en": "minregime({floor}) leaves no admissible threshold split: the effective support "
        "has only {n} observations and each regime needs at least minregime() of them.",
        "fr": "minregime({floor}) ne laisse aucun seuil admissible : le support effectif n'a que "
        "{n} observations et chaque régime en exige au moins minregime().",
    },
    "panel_key_missing": {
        "en": "Missing {what} in {n} row(s), first at row(s) {rows}.",
        "fr": "{what} manquant(e) dans {n} ligne(s), la première en position {rows}.",
    },
    "panel_duplicates": {
        "en": "Repeated time values within a unit ({n} pair(s) of {id}, {time}), for example "
        "{examples}.",
        "fr": "Valeurs de temps répétées au sein d'une unité ({n} couple(s) {id}, {time}), par "
        "exemple {examples}.",
    },
    "time_not_integer": {
        "en": "The time variable '{name}' must hold whole numbers (periods spaced by 1, e.g. "
        "years); found {example}. Convert dates to period numbers first.",
        "fr": "La variable de temps « {name} » doit contenir des entiers (périodes espacées de "
        "1, par exemple des années) ; trouvé {example}. Convertissez d'abord les dates en "
        "numéros de période.",
    },
    "column_not_numeric": {
        "en": "Variable '{name}' is not numeric (type {dtype}).",
        "fr": "La variable « {name} » n'est pas numérique (type {dtype}).",
    },
    "balance_detail": {
        "en": "The panel is {kind}: {n_incomplete} of {n_units} unit(s) are not observed in all "
        "{n_times} period(s).",
        "fr": "Le panel est {kind} : {n_incomplete} unité(s) sur {n_units} ne sont pas observées "
        "aux {n_times} période(s).",
    },
    "where_not_boolean": {
        "en": "where must be a boolean mask of length {n} or an expression that evaluates to "
        "one; got {got}.",
        "fr": "where doit être un masque booléen de longueur {n} ou une expression qui en "
        "donne un ; reçu {got}.",
    },
    "no_usable_obs": {
        "en": "No usable complete-case observations in the requested sample.",
        "fr": "Aucune observation complète utilisable dans l'échantillon demandé.",
    },
    "keys_not_found": {
        "en": "Panel identifier and time variable were not given and the index does not hold "
        "two levels; pass id= and time=.",
        "fr": "L'identifiant du panel et la variable de temps ne sont pas fournis et l'index n'a "
        "pas deux niveaux ; passez id= et time=.",
    },
    "unsupported_file": {
        "en": "Unsupported file type '{suffix}' (use .dta, .csv or .parquet).",
        "fr": "Type de fichier non géré « {suffix} » (utilisez .dta, .csv ou .parquet).",
    },
}


def message(key: str, lang: Lang | None = None, **fields: object) -> str:
    """Return the message registered under ``key`` in the requested language.

    Parameters
    ----------
    key : str
        Message identifier.
    lang : {"en", "fr"}, optional
        Language; defaults to the global ``lang`` option.
    **fields
        Values substituted in the template.

    Raises
    ------
    KeyError
        If the key is not registered.
    """
    language: Lang = lang if lang is not None else get_options().lang
    template = _CATALOGUE[key].get(language) or _CATALOGUE[key]["en"]
    return template.format(**fields)


def keys() -> list[str]:
    """Return all registered message keys (used by the catalogue completeness test)."""
    return sorted(_CATALOGUE)


def has_language(key: str, lang: Lang) -> bool:
    """Whether ``key`` is translated into ``lang``."""
    return lang in _CATALOGUE[key]
