"""Console summary of one fit: header, the three blocks of slopes, then the diagnostics."""

from __future__ import annotations

import sys

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.reporting.extract import BLOCKS, ModelColumn, extract
from pyxtdpthresh.extras.reporting.formats import DEFAULT_LEVELS, MISSING, number, star_count
from pyxtdpthresh.extras.reporting.frames import to_dataframe
from pyxtdpthresh.extras.reporting.labels import label
from pyxtdpthresh.extras.reporting.stargazer import TableOptions, stat_label, stat_text

#: Diagnostics of the footer, in order.
_FOOTER = ("hansen_p", "ar1_p", "ar2_p", "linearity_p")
#: Characters a console may not encode, and their ASCII stand-in.
_ASCII = (("γ̂", "gamma-hat"), ("γ", "gamma"))


def _header(column: ModelColumn, options: TableOptions) -> list[str]:
    """Title and facts of the sample and the threshold."""
    lang = options.lang
    facts = [
        f"{label('dep_var', lang)}: {column.dep_var}",
        f"{label('n_units', lang)}: {stat_text('n_units', column, options)}",
        f"{label('n_obs', lang)}: {stat_text('n_obs', column, options)}",
    ]
    threshold = [
        f"{label('threshold_var', lang)}: {column.q or MISSING}",
        f"{label('gamma', lang)} = {stat_text('gamma', column, options)}",
        f"{stat_label('gamma_ci', options)}: {stat_text('gamma_ci', column, options)}",
    ]
    form = [
        f"{label('shape', lang)}: {stat_text('shape', column, options)}",
        f"{label('method', lang)}: {stat_text('method', column, options)}",
        f"{label('estimator', lang)}: {stat_text('estimator', column, options)}",
    ]
    return [label("title", lang), "   ".join(facts), "   ".join(threshold), "   ".join(form)]


def _printable(text: str) -> str:
    """Replace the characters the standard output cannot encode (a Windows console)."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        for char, name in _ASCII:
            text = text.replace(char, name)
    return text


def summary(
    model: object, *, level: float = 95.0, lang: Lang | None = None, digits: int = 4
) -> str:
    """Return a readable summary of a fit.

    The three blocks (lower regime, change at the threshold, upper regime) list each slope with
    its standard error, ``z``, p-value, stars and normal interval at ``level``; the header gives
    the sample and the threshold with its interval, and the footer the Hansen, AR(1), AR(2) and
    linearity p-values (``-`` where the model has none).
    """
    # Stata: _xdpt_coeftab (xtdpthresh.ado:2319-2367): lower, upper and change blocks
    from pyxtdpthresh.extras.plotting.style import resolve_lang

    options = TableOptions(digits=digits, level=level, lang=resolve_lang(lang))
    column = extract(model)
    frame = to_dataframe(model, level)
    lang = options.lang
    widths = (12, 11, 9, 9)
    head = (
        f"{'':<28}{label('coef', lang):>{widths[0]}}{label('std_err', lang):>{widths[1]}}"
        f"{label('z', lang):>{widths[2]}}{label('p_z', lang):>{widths[3]}}"
        f"  {label('conf_int', lang, level=level)}"
    )
    rule = "-" * len(head)
    lines = [*_header(column, options), rule, head, rule]
    for block in BLOCKS:
        if block not in frame.index.get_level_values("block"):
            continue
        lines.append(label(block, lang))
        for variable, row in frame.loc[block].iterrows():
            stars = "*" * star_count(row["p"], DEFAULT_LEVELS)
            numbers = [
                number(row[c], digits, options.decimal) for c in ("estimate", "se", "z", "p")
            ]
            low = number(row["ci_low"], digits, options.decimal)
            high = number(row["ci_high"], digits, options.decimal)
            lines.append(
                f"  {str(variable):<26}{numbers[0]:>{widths[0]}}{numbers[1]:>{widths[1]}}"
                f"{numbers[2]:>{widths[2]}}{numbers[3]:>{widths[3]}}"
                f"  [{low}, {high}] {stars}".rstrip()
            )
    lines.append(rule)
    footer = [f"{stat_label(k, options)}: {stat_text(k, column, options)}" for k in _FOOTER]
    lines += ["   ".join(footer[:2]), "   ".join(footer[2:])]
    return _printable("\n".join(lines) + "\n")
