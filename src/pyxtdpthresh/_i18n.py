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
