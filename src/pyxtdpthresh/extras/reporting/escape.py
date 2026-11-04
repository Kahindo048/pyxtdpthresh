"""Escaping of text for each output format (layer 6)."""

from __future__ import annotations

import html
import re

#: Greek letters the labels use, and how LaTeX writes them.
_GREEK = re.compile("(γ̂|γ|δ)")
_LATEX_GREEK = {"γ̂": r"$\hat{\gamma}$", "γ": r"$\gamma$", "δ": r"$\delta$"}
_LATEX_SPECIAL = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
}
_LATEX_PATTERN = re.compile("|".join(re.escape(c) for c in _LATEX_SPECIAL))
_MARKDOWN = re.compile(r"([\\`*_\[\]|~])")
#: A minus sign that belongs to a number.
_MINUS = re.compile(r"-(?=\d)")


def latex(text: str) -> str:
    """Escape the characters LaTeX treats specially and write Greek letters as math."""
    parts = _GREEK.split(text)
    return "".join(
        _LATEX_GREEK[part] if index % 2 else _LATEX_PATTERN.sub(_latex_char, part)
        for index, part in enumerate(parts)
    )


def _latex_char(match: re.Match[str]) -> str:
    return _LATEX_SPECIAL[match.group(0)]


def latex_number(text: str) -> str:
    """Escape a formatted number or interval: its minus signs become math minus signs."""
    return _MINUS.sub("$-$", latex(text))


def markdown(text: str) -> str:
    """Escape the characters Markdown reads as markup."""
    return _MARKDOWN.sub(r"\\\1", text)


def web(text: str) -> str:
    """Escape text for HTML; the minus signs of numbers become true minus signs."""
    return _MINUS.sub("−", html.escape(text, quote=False))
