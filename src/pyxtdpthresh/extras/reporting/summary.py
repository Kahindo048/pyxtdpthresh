"""Console summary of one fit, laid out like the reports of ``pyxtabond2`` and ``pyxthreg``.

Six blocks, 80 columns wide: the title and a two-column header (``pyxtabond2``), the threshold
with its interval, the threshold-effect test with its bootstrap critical values (``pyxthreg``),
the slopes of the three regimes, and the diagnostic tests.  Only the layout is new: every number
is one the fit already holds.
"""

from __future__ import annotations

import sys
from datetime import datetime

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.reporting.extract import BLOCKS, ModelColumn, Statistic, extract
from pyxtdpthresh.extras.reporting.formats import DEFAULT_LEVELS, MISSING, number, star_count
from pyxtdpthresh.extras.reporting.frames import to_dataframe
from pyxtdpthresh.extras.reporting.labels import label

#: Narrowest report; a table with long variable names widens every rule.
WIDTH = 80
#: Spaces between the two columns of the header.
_GAP = 4
_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _printable(text: str) -> str:
    """Replace the characters the standard output cannot encode (a legacy Windows console)."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        text = text.encode(encoding, errors="replace").decode(encoding)
    return text


def _text(column: ModelColumn, key: str) -> str | None:
    """Return a statistic that is text, ``None`` when the model has none."""
    value = column.stats.get(key)
    return value if isinstance(value, str) else None


def _value(column: ModelColumn, key: str) -> float | None:
    """Return a statistic that is a number, ``None`` when the model has none."""
    value: Statistic = column.stats.get(key)
    return float(value) if isinstance(value, int | float) and not isinstance(value, bool) else None


def _flag(column: ModelColumn, key: str, lang: Lang) -> str:
    """``Yes``/``No`` for a model option, ``-`` for a model without it."""
    value = column.stats.get(key)
    if not isinstance(value, bool):
        return MISSING
    return label("v_yes" if value else "v_no", lang)


def _whole(value: float | None) -> str:
    """Write a count without decimals."""
    return MISSING if value is None else str(round(value))


def _stamp(when: datetime) -> tuple[str, str]:
    """Date and time of the report, in English whatever the locale."""
    date = f"{_DAYS[when.weekday()]}, {when.day:02d} {_MONTHS[when.month - 1]} {when.year}"
    return date, when.strftime("%H:%M:%S")


# ------------------------------------------------------------------------------------- header
def _header_rows(
    column: ModelColumn, lang: Lang, when: datetime
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return the two columns of the header as ``(label, value)`` pairs."""
    henreg = column.kind == "xthenreg"
    n_obs, n_units = _value(column, "n_obs"), _value(column, "n_units")
    periods = _value(column, "n_periods")
    per_group = periods if henreg else (n_obs / n_units if n_obs and n_units else None)
    estimator = _text(column, "estimator")
    method = label("v_one_step" if estimator == "one_step" else "v_two_step", lang)
    static = column.stats.get("static") is True
    if henreg:
        covariance = label("v_kernel", lang)
    else:
        joint = column.stats.get("joint") is True
        covariance = label("v_robust_joint" if joint else "v_robust_cond", lang)
    boot, seed = _value(column, "n_boot"), _value(column, "seed")
    bootstrap = MISSING if boot is None else f"{_whole(boot)} / {_whole(seed)}"
    transform = _text(column, "method") or MISSING
    date, clock = _stamp(when)
    left = [
        (label("h_dep", lang), column.dep_var or MISSING),
        (label("h_model", lang), label("v_static" if static else "v_dynamic", lang)),
        (label("h_method", lang), method),
        (label("h_date", lang), date),
        (label("h_time", lang), clock),
        (label("h_nobs", lang), _whole(n_obs)),
        (label("h_groups", lang), _whole(n_units)),
        (label("h_obspg", lang), MISSING if per_group is None else f"{per_group:.2f}"),
        (label("h_ninst", lang), _whole(_value(column, "n_instruments"))),
        (label("h_cov", lang), covariance),
    ]
    right = [
        (label("h_qvar", lang), column.q or MISSING),
        (label("h_effect", lang), label(_text(column, "shape") or "jump", lang)),
        (label("h_transf", lang), transform),
        (label("h_gvar", lang), _text(column, "id") or MISSING),
        (label("h_tvar", lang), _text(column, "time") or MISSING),
        (label("h_lags", lang), _text(column, "maxlag") or MISSING),
        (label("h_collapse", lang), _flag(column, "collapse", lang)),
        (label("h_teff", lang), _flag(column, "time_effects", lang)),
        (label("h_boot", lang), bootstrap),
        (label("h_grid", lang), _whole(_value(column, "grid"))),
    ]
    return left, right


def _pair(left: tuple[str, str], right: tuple[str, str], width: int) -> str:
    """One header line: each side is its label, then its value flush right in half the width."""
    half = (width - _GAP) // 2
    sides = []
    for name, value in (left, right):
        sides.append(name + value.rjust(max(half - len(name), len(value) + 1)))
    return (" " * _GAP).join(sides)


# ------------------------------------------------------------------------------------- tables
def _table(
    title: str, head: list[str], widths: list[int], rows: list[list[str]], width: int
) -> list[str]:
    """Build a titled table: centred title, double rule, header, single rule, rows, double rule.

    The first column is left aligned and the others right aligned; ``widths`` gives all columns
    but the first, which takes what is left of ``width``.
    """
    first = width - sum(widths)
    cells = [first, *widths]

    def line(row: list[str]) -> str:
        return row[0].ljust(cells[0]) + "".join(
            c.rjust(w) for c, w in zip(row[1:], widths, strict=True)
        )

    return [
        title.center(width).rstrip(),
        "=" * width,
        line(head),
        "-" * width,
        *(line(row) for row in rows),
        "=" * width,
    ]


def _threshold_table(column: ModelColumn, lang: Lang, digits: int, width: int) -> list[str]:
    """Build the table of the estimate of the threshold and its interval."""
    interval = column.stats.get("gamma_ci")
    low, high = interval if isinstance(interval, tuple) else (None, None)
    level = _value(column, "gamma_level") or 95.0
    rows = [
        [
            "Th-1",
            number(_value(column, "gamma"), digits),
            number(low, digits),
            number(high, digits),
        ]
    ]
    head = [label(k, lang) for k in ("c_model", "c_threshold", "c_lower", "c_upper")]
    widths = [(width - 18) // 3] * 3
    return _table(label("t_threshold", lang, level=level), head, widths, rows, width)


def _effect_table(column: ModelColumn, lang: Lang, digits: int, width: int) -> list[str]:
    """Bootstrap tests of the threshold effect with their critical values (empty without any)."""
    henreg = column.kind == "xthenreg"
    rows = []
    for key, name in (
        ("linearity", "r_linearity_sw" if henreg else "r_linearity"),
        ("continuity", "r_continuity"),
    ):
        statistic, p_value = _value(column, key), _value(column, f"{key}_p")
        if statistic is None and p_value is None:
            continue
        crit = [number(_value(column, f"{key}_crit{s}"), digits) for s in ("10", "5", "1")]
        rows.append([label(name, lang), number(statistic, digits), number(p_value, digits), *crit])
    if not rows:
        return []
    boot = _value(column, "n_boot")
    suffix = "" if boot is None else f", B = {_whole(boot)}"
    head = [
        label("c_test", lang),
        label("c_stat", lang),
        label("c_prob", lang),
        "Crit10",
        "Crit5",
        "Crit1",
    ]
    return _table(label("t_effect", lang, boot=suffix), head, [12, 9, 12, 12, 13], rows, width)


def _coefficients(
    column: ModelColumn, model: object, lang: Lang, digits: int, level: float
) -> tuple[list[tuple[str, list[str], str]], list[str]]:
    """Return the rows ``(kind, cells, stars)`` of the slopes by regime, and the header cells."""
    frame = to_dataframe(model, level)
    low = (100.0 - level) / 200.0
    head = [
        label("c_coef", lang),
        label("c_se", lang),
        label("c_z", lang),
        label("c_p", lang),
        f"[{low:.3f}",
        f"{1.0 - low:.3f}]",
    ]
    fields = {"q": column.q or "q", "gamma": number(_value(column, "gamma"), digits)}
    titles = {
        "lower": label("b_lower", lang, **fields),
        "change": label("b_change", lang),
        "upper": label("b_upper", lang, **fields),
    }
    shown = set(frame.index.get_level_values("block"))
    rows: list[tuple[str, list[str], str]] = []
    for block in (b for b in BLOCKS if b in shown):
        rows.append(("title", [titles[block]], ""))
        for variable, row in frame.loc[block].iterrows():
            cells = [
                str(variable),
                number(row["estimate"], digits),
                number(row["se"], digits),
                number(row["z"], 3),
                number(row["p"], 4),
                number(row["ci_low"], digits),
                number(row["ci_high"], digits),
            ]
            rows.append(("row", cells, "*" * star_count(row["p"], DEFAULT_LEVELS)))
    return rows, head


def _coefficient_table(
    column: ModelColumn, model: object, lang: Lang, digits: int, level: float, width: int
) -> tuple[list[str], int]:
    """Build the slopes by regime; return the lines and the width the table needs."""
    rows, head = _coefficients(column, model, lang, digits, level)
    names = [cells[0] for kind, cells, _ in rows if kind == "row"]
    name_width = max([20, *(len(n) + 2 for n in names)])
    widths = [10, 9, 8, 8, 10, 10]
    for _, cells, _ in rows:
        for position, text in enumerate(cells[1:]):
            widths[position] = max(widths[position], len(text) + 2)
    needed = max(width, name_width + sum(widths) + 4)
    title = label("t_coef_static" if column.stats.get("static") is True else "t_coef_dynamic", lang)
    lines = [
        title.center(needed).rstrip(),
        "=" * needed,
        "".ljust(name_width) + "".join(c.rjust(w) for c, w in zip(head, widths, strict=True)),
        "-" * needed,
    ]
    for kind, cells, stars in rows:
        if kind == "title":
            lines.append(cells[0])
            continue
        body = ("  " + cells[0]).ljust(name_width) + "".join(
            c.rjust(w) for c, w in zip(cells[1:], widths, strict=True)
        )
        lines.append(f"{body} {stars}".rstrip())
    lines += ["=" * needed, label("s_significance", lang)]
    return lines, needed


def _diagnostic_table(column: ModelColumn, lang: Lang, width: int) -> list[str]:
    """Arellano-Bond and Hansen tests, ``-`` where the model has none."""

    def z_test(key: str) -> tuple[str, str]:
        z, p = _value(column, key), _value(column, f"{key}_p")
        return (
            MISSING if z is None else f"z = {z:.2f}",
            MISSING if p is None else f"Pr > z = {p:.3f}",
        )

    hansen, p_hansen, df = (
        _value(column, "hansen"),
        _value(column, "hansen_p"),
        _value(column, "hansen_df"),
    )
    chi2 = (
        MISSING if hansen is None or df is None else f"chi2({_whole(df)}) = {hansen:.2f}",
        MISSING if p_hansen is None else f"Pr > chi2 = {p_hansen:.3f}",
    )
    rows = [
        [label("r_ar1", lang), *z_test("ar1")],
        [label("r_ar2", lang), *z_test("ar2")],
        [label("r_hansen", lang), *chi2],
    ]
    head = [label("c_diag", lang), label("c_stat", lang), label("c_pvalue", lang)]
    return _table(label("t_diag", lang), head, [24, width - 54], rows, width)


def summary(
    model: object,
    *,
    level: float = 95.0,
    lang: Lang | None = None,
    digits: int = 4,
    when: datetime | None = None,
) -> str:
    """Return the report of a fit, ready to print.

    Parameters
    ----------
    model
        A fit or a result of :func:`pyxtdpthresh.xtdpthresh` or :func:`pyxtdpthresh.xthenreg`.
    level
        Confidence level of the normal intervals of the slopes (percent).  The interval of the
        threshold keeps the level of the estimation.
    lang : {"en", "fr"}, optional
        Language of the texts (default: the global ``lang`` option).
    digits
        Decimals of the estimates.
    when
        Date and time printed in the header (default: now).  A result keeps the moment it was
        computed, so printing it twice gives the same report.

    Returns
    -------
    str
        The report: header, threshold, threshold-effect test with its bootstrap critical values,
        the slopes by regime and the diagnostic tests (``-`` where the model has none).
    """
    # Stata: _xdpt_coeftab (xtdpthresh.ado:2319-2367): lower, upper and change blocks
    from pyxtdpthresh.extras.plotting.style import resolve_lang

    lang = resolve_lang(lang)
    column = extract(model)
    when = when or datetime.now()
    coefficients, width = _coefficient_table(column, model, lang, digits, level, WIDTH)
    left, right = _header_rows(column, lang, when)
    title = label("s_title_xthenreg" if column.kind == "xthenreg" else "s_title_xtdpthresh", lang)
    lines = [
        title.center(width).rstrip(),
        "=" * width,
        *(_pair(a, b, width) for a, b in zip(left, right, strict=True)),
        "=" * width,
        "",
        *_threshold_table(column, lang, digits, width),
    ]
    effect = _effect_table(column, lang, digits, width)
    if effect:
        lines += ["", *effect]
    lines += ["", *coefficients, "", *_diagnostic_table(column, lang, width)]
    return _printable("\n".join(lines) + "\n")
