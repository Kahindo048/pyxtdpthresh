"""``ThresholdStargazer``: models side by side, with the options of R's ``stargazer`` (layer 6).

The slopes are laid out by regime (lower, change at the threshold, upper) instead of one row per
variable, and the lines under them are those of a threshold model: observations, units,
instruments, Hansen, serial correlation, linearity, threshold and its interval, transformation
and form of the effect.  The object builds a :class:`~.table_spec.TableSpec` once; every output
format reads that.
"""

from __future__ import annotations

import logging
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scipy.stats import norm

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.reporting.extract import BLOCKS, Estimate, ModelColumn, extract
from pyxtdpthresh.extras.reporting.formats import (
    DEFAULT_LEVELS,
    MISSING,
    integer,
    interval,
    number,
    star_count,
    star_note,
)
from pyxtdpthresh.extras.reporting.labels import label
from pyxtdpthresh.extras.reporting.table_spec import Cell, CoefRow, StatRow, TableSpec

logger = logging.getLogger(__name__)

STATISTICS = ("se", "t", "p", "ci")
#: Diagnostic lines in the order they are shown, and the ones that are whole numbers.
STAT_ORDER = (
    "n_obs", "n_units", "n_instruments", "hansen_p", "ar1_p", "ar2_p", "linearity_p", "gamma",
    "gamma_ci", "method", "shape", "estimator",
)  # fmt: skip
_COUNTS = ("n_obs", "n_units", "n_instruments")
_WORDS = ("shape", "estimator")


@dataclass(frozen=True)
class TableOptions:
    """Options of the table (see :class:`ThresholdStargazer`)."""

    statistic: str = "se"
    star_levels: tuple[float, ...] = DEFAULT_LEVELS
    digits: int = 3
    keep: tuple[str, ...] = ()
    omit: tuple[str, ...] = ()
    order: tuple[str, ...] = ()
    covariate_labels: Mapping[str, str] | None = None
    omit_stat: tuple[str, ...] = ()
    single_row: bool = False
    level: float = 95.0
    lang: Lang = "en"

    @property
    def decimal(self) -> str:
        """Decimal sign of the language."""
        return "," if self.lang == "fr" else "."


def _patterns(value: str | Sequence[str] | None) -> tuple[str, ...]:
    """Return ``value`` as a tuple of patterns (one string is one pattern)."""
    if value is None:
        return ()
    return (value,) if isinstance(value, str) else tuple(value)


def _matches(block: str, variable: str, patterns: tuple[str, ...]) -> bool:
    """Whether a pattern matches the variable name or ``block:variable``."""
    return any(re.search(p, variable) or re.search(p, f"{block}:{variable}") for p in patterns)


def row_keys(columns: Sequence[ModelColumn], options: TableOptions) -> list[tuple[str, str]]:
    """Return the ``(block, variable)`` rows of the table: the union of the models, filtered.

    Blocks come in the order lower, change, upper; inside a block the variables keep the order
    in which the models introduce them, then ``order`` brings the listed ones to the front.
    """
    seen: dict[tuple[str, str], None] = {}
    for block in BLOCKS:
        for column in columns:
            for key in column.coefs:
                if key[0] == block:
                    seen.setdefault(key)
    keys = list(seen)
    if options.keep:
        keys = [k for k in keys if _matches(k[0], k[1], options.keep)]
    if options.omit:
        keys = [k for k in keys if not _matches(k[0], k[1], options.omit)]
    if options.order:

        def rank(key: tuple[str, str]) -> int:
            hits = [i for i, p in enumerate(options.order) if _matches(key[0], key[1], (p,))]
            return hits[0] if hits else len(options.order)

        keys.sort(key=lambda k: (BLOCKS.index(k[0]), rank(k)))
    return keys


def _p_value(estimate: Estimate) -> float:
    """Two-sided normal p-value of ``b / se``."""
    if not math.isfinite(estimate.b) or not math.isfinite(estimate.se) or estimate.se <= 0:
        return math.nan
    return float(2.0 * norm.sf(abs(estimate.b / estimate.se)))


def coefficient_cell(estimate: Estimate | None, options: TableOptions) -> Cell:
    """Return the cell of one estimate: value, stars and the statistic chosen."""
    if estimate is None:
        return Cell()
    digits, decimal = options.digits, options.decimal
    p = _p_value(estimate)
    if options.statistic == "se":
        below = f"({number(estimate.se, digits, decimal)})"
    elif options.statistic == "t":
        t = estimate.b / estimate.se if estimate.se > 0 else math.nan
        below = f"({number(t, digits, decimal)})"
    elif options.statistic == "p":
        below = f"({number(p, digits, decimal)})"
    else:
        z = float(norm.ppf(0.5 + options.level / 200.0))
        below = interval(
            estimate.b - z * estimate.se, estimate.b + z * estimate.se, digits, decimal
        )
    return Cell(number(estimate.b, digits, decimal), star_count(p, options.star_levels), below)


def stat_text(key: str, column: ModelColumn, options: TableOptions) -> str:
    """Return the text of one diagnostic of one model (``-`` when the model has none)."""
    value = column.stats.get(key)
    lang, digits, decimal = options.lang, options.digits, options.decimal
    if value is None:
        return MISSING
    if key in _COUNTS and isinstance(value, float):
        return integer(value)
    if key in _WORDS and isinstance(value, str):
        return label(value, lang)
    if isinstance(value, tuple):
        return interval(value[0], value[1], digits, decimal)
    if isinstance(value, float):
        return number(value, digits, decimal)
    return str(value)


def stat_label(key: str, options: TableOptions) -> str:
    """Return the row label of the diagnostic ``key``."""
    return label(key, options.lang, level=options.level)


def stat_rows(columns: Sequence[ModelColumn], options: TableOptions) -> list[StatRow]:
    """Diagnostic rows shown by at least one model, in :data:`STAT_ORDER`."""
    rows = []
    for key in STAT_ORDER:
        if key in options.omit_stat or all(c.stats.get(key) is None for c in columns):
            continue
        rows.append(
            StatRow(stat_label(key, options), tuple(stat_text(key, c, options) for c in columns))
        )
    return rows


def _notes(
    columns: Sequence[ModelColumn], options: TableOptions, extra: Sequence[str]
) -> list[str]:
    """Return the notes: the stars, the statistic, the interval kinds, then the user's."""
    lang = options.lang
    notes = [
        star_note(options.star_levels, options.decimal),
        label(options.statistic, lang, level=options.level),
    ]
    kinds = {c.gamma_ci_kind for c in columns if c.stats.get("gamma_ci") is not None}
    if len(kinds) > 1 and "gamma_ci" not in options.omit_stat:
        notes.append(label("gamma_ci_kinds", lang))
    return [*notes, *extra]


class ThresholdStargazer:
    r"""Table of threshold models side by side, in the manner of R's ``stargazer``.

    Parameters
    ----------
    models
        Fitted models (``xtdpthresh`` results; ``xthenreg`` results); mixed types are allowed.
    model_names
        Name of each column, instead of ``(1)``, ``(2)``...
    statistic : {"se", "t", "p", "ci"}
        What goes under each estimate: standard error, t statistic, p-value or confidence
        interval at ``level``.
    star_levels
        Significance levels, loosest first (default 0.1, 0.05, 0.01 give ``*``, ``**``, ``***``).
    digits
        Decimals of the numbers.
    column_labels
        Group label above each column (for example ``"FD"``, ``"FOD"``).
    covariate_labels
        New names of the variables, ``{"cashflow": "Cash flow"}`` (``"block:variable"`` keys
        name one regime only).
    dep_var_label
        Name of the dependent variable to show instead of the models' own.
    keep, omit, order
        Regular expressions that select, drop and order the rows, matched against the variable
        name or ``block:variable`` (``"lower:cashflow"``).
    add_lines
        Extra lines under the coefficients: ``[("Firm effects", ["Yes", "Yes"])]``.
    notes
        Extra notes under the table.
    title, label
        Caption and anchor (LaTeX ``\\caption`` and ``\\label``).
    font_size
        LaTeX size command (``"footnotesize"``).
    single_row
        Put each statistic on the line of its estimate.
    omit_stat
        Diagnostic lines to drop (``"n_obs"``, ``"hansen_p"``...).
    level
        Level of the intervals (``statistic="ci"``).
    lang : {"en", "fr"}, optional
        Language of the labels and decimal sign (default: the global ``lang`` option).

    Examples
    --------
    >>> table = ThresholdStargazer([fit_fd, fit_fod], ["FD", "FOD"])  # doctest: +SKIP
    >>> table.to_latex("table1.tex")  # doctest: +SKIP
    """

    def __init__(
        self,
        models: Sequence[object],
        model_names: Sequence[str] | None = None,
        *,
        statistic: str = "se",
        star_levels: Sequence[float] = DEFAULT_LEVELS,
        digits: int = 3,
        column_labels: Sequence[str] | None = None,
        covariate_labels: Mapping[str, str] | None = None,
        dep_var_label: str | None = None,
        keep: str | Sequence[str] | None = None,
        omit: str | Sequence[str] | None = None,
        order: str | Sequence[str] | None = None,
        add_lines: Sequence[tuple[str, Sequence[str]]] = (),
        notes: Sequence[str] = (),
        title: str = "",
        label: str = "",  # noqa: A002
        font_size: str | None = None,
        single_row: bool = False,
        omit_stat: Sequence[str] = (),
        level: float = 95.0,
        lang: Lang | None = None,
    ) -> None:
        from pyxtdpthresh.extras.plotting.style import resolve_lang

        if not models:
            raise SpecificationError(message("table_no_models"), key="table_no_models")
        if statistic not in STATISTICS:
            raise SpecificationError(
                message("table_statistic", options=", ".join(STATISTICS), value=statistic),
                key="table_statistic",
            )
        n = len(models)
        for what, given in (
            ("model_names", model_names),
            ("column_labels", column_labels),
        ):
            if given is not None and len(given) != n:
                raise SpecificationError(
                    message("table_names_length", what=what, got=len(given), expected=n),
                    key="table_names_length",
                )
        for text, values in add_lines:
            if len(values) != n:
                raise SpecificationError(
                    message(
                        "table_names_length",
                        what=f"add_lines {text!r}",
                        got=len(values),
                        expected=n,
                    ),
                    key="table_names_length",
                )
        self.options = TableOptions(
            statistic=statistic,
            star_levels=tuple(star_levels),
            digits=digits,
            keep=_patterns(keep),
            omit=_patterns(omit),
            order=_patterns(order),
            covariate_labels=covariate_labels,
            omit_stat=tuple(omit_stat),
            single_row=single_row,
            level=level,
            lang=resolve_lang(lang),
        )
        self.columns = [extract(m) for m in models]
        names = (
            tuple(model_names) if model_names is not None else tuple(f"({i + 1})" for i in range(n))
        )
        dep_vars = (dep_var_label,) * n if dep_var_label else tuple(c.dep_var for c in self.columns)
        self.spec = TableSpec(
            dep_var_label=_dep_var_label(self.options.lang),
            dep_vars=tuple(dep_vars),
            columns=names,
            column_labels=tuple(column_labels) if column_labels is not None else (),
            rows=tuple(self._coefficient_rows()),
            stats=tuple(
                [StatRow(t, tuple(v)) for t, v in add_lines] + stat_rows(self.columns, self.options)
            ),
            notes=tuple(_notes(self.columns, self.options, notes)),
            title=title,
            label=label,
            font_size=font_size or "",
            single_row=single_row,
        )

    def _coefficient_rows(self) -> list[CoefRow]:
        """One row per ``(block, variable)`` with the cell of each model."""
        options = self.options
        names = options.covariate_labels or {}
        rows = []
        for block, variable in row_keys(self.columns, options):
            shown = names.get(f"{block}:{variable}", names.get(variable, variable))
            cells = tuple(
                coefficient_cell(c.coefs.get((block, variable)), options) for c in self.columns
            )
            rows.append(CoefRow(shown, cells, label(block, options.lang)))
        return rows

    # ------------------------------------------------------------------------------ outputs
    def to_latex(self, path: str | Path | None = None) -> str:
        """Return the table as LaTeX (``booktabs``); also write it to ``path`` when given.

        Parameters
        ----------
        path
            File to write (UTF-8), in addition to returning the text.

        Returns
        -------
        str
            The table as LaTeX.
        """
        from pyxtdpthresh.extras.reporting.renderers import latex

        return _emit(latex.render(self.spec), path)

    def to_html(self, path: str | Path | None = None) -> str:
        """Return the table as an HTML fragment; also write it to ``path`` when given.

        Parameters
        ----------
        path
            File to write (UTF-8), in addition to returning the text.

        Returns
        -------
        str
            The table as an HTML fragment.
        """
        from pyxtdpthresh.extras.reporting.renderers import html

        return _emit(html.render(self.spec), path)

    def to_markdown(self, path: str | Path | None = None) -> str:
        """Return the table as a Markdown pipe table; also write it to ``path`` when given.

        Parameters
        ----------
        path
            File to write (UTF-8), in addition to returning the text.

        Returns
        -------
        str
            The table as a Markdown pipe table.
        """
        from pyxtdpthresh.extras.reporting.renderers import markdown

        return _emit(markdown.render(self.spec), path)

    def to_text(self, path: str | Path | None = None) -> str:
        """Return the table as aligned plain text; also write it to ``path`` when given.

        Parameters
        ----------
        path
            File to write (UTF-8), in addition to returning the text.

        Returns
        -------
        str
            The table as aligned plain text.
        """
        from pyxtdpthresh.extras.reporting.renderers import text

        return _emit(text.render(self.spec), path)

    def to_csv(self, path: str | Path | None = None) -> str:
        """Return the table as CSV text; also write it to ``path`` when given.

        Parameters
        ----------
        path
            File to write (UTF-8), in addition to returning the text.

        Returns
        -------
        str
            The table as CSV text.
        """
        from pyxtdpthresh.extras.reporting.renderers import csv

        return _emit(csv.render(self.spec), path)

    def to_word(self, path: str | Path) -> Path:
        """Write the table to a Word file (needs ``python-docx``) and return its path.

        Parameters
        ----------
        path
            File to write.

        Returns
        -------
        pathlib.Path
            The file that was written.

        Raises
        ------
        PyxdpthreshError
            ``python-docx`` is not installed.
        """
        from pyxtdpthresh.extras.reporting.renderers import word

        return _written(word.write(self.spec, Path(path)))

    def to_excel(self, path: str | Path) -> Path:
        """Write the table to an Excel file (needs ``openpyxl``) and return its path.

        Parameters
        ----------
        path
            File to write.

        Returns
        -------
        pathlib.Path
            The file that was written.

        Raises
        ------
        PyxdpthreshError
            ``openpyxl`` is not installed.
        """
        from pyxtdpthresh.extras.reporting.renderers import excel

        return _written(excel.write(self.spec, Path(path)))

    def __str__(self) -> str:
        return self.to_text()

    def _repr_html_(self) -> str:
        """Display in Jupyter."""
        return self.to_html()

    def _repr_latex_(self) -> str:
        """Display in LaTeX output (``nbconvert`` to PDF)."""
        return self.to_latex()


def _dep_var_label(lang: Lang) -> str:
    return label("dep_var", lang)


def _emit(content: str, path: str | Path | None) -> str:
    """Write ``content`` to ``path`` when given, and return it."""
    if path is not None:
        target = Path(path)
        target.write_text(content, encoding="utf-8")
        logger.info("table written to %s", target)
    return content


def _written(path: Path) -> Path:
    logger.info("table written to %s", path)
    return path


def compare(models: Sequence[object], **options: Any) -> ThresholdStargazer:
    """Put fitted models side by side (xthenreg against xtdpthresh, FD against FOD, jump, kink).

    A shortcut for :class:`ThresholdStargazer`: ``compare([a, b], model_names=["FD", "FOD"])``.

    Parameters
    ----------
    models
        Results of :func:`pyxtdpthresh.xtdpthresh` and :func:`pyxtdpthresh.xthenreg`, in the
        order of the columns.
    **options
        Options of :class:`ThresholdStargazer` (``model_names``, ``statistic``, ``star_levels``,
        ``digits``...).

    Returns
    -------
    ThresholdStargazer
        The table, with the ``to_*`` writers.

    Examples
    --------
    >>> import pyxtdpthresh as pyx
    >>> df = pyx.load_dataset("invest")
    >>> df = df[~df["firm"].isin([137, 391, 407, 488, 538])]
    >>> res = pyx.xtdpthresh(df, "invest", q="debt", endogenous=["cashflow", "tobin_q", "debt"],
    ...                      maxlag=(3, 8), collapse=True, id="firm", time="year", bootstrap=False)
    >>> table = pyx.compare([res], model_names=["FD"])
    >>> table.to_text().splitlines()[1]
    'Dependent variable: invest'
    """
    return ThresholdStargazer(models, **options)
