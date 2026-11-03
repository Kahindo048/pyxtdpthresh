"""Lag, lead and difference terms, as Stata's time-series operators.

A term such as ``"L2.x"``, ``"LD.x"`` or ``"S12.x"`` names a variable and a chain of operators:
``L`` lag, ``F`` lead, ``D`` difference, ``S`` seasonal difference, each with an optional number
(``L2`` is the second lag, ``D2`` the second difference, ``S12`` the 12-period difference) or
a list in parentheses (``"L(1/2).x"`` is ``"L.x"`` and ``"L2.x"``).  The operators commute, so a
chain reduces to a net shift, a difference order and the seasonal periods; the canonical
spelling is the one Stata writes (``"ll.x"`` and ``"l2.x"`` are ``"L2.x"``, ``"dl.x"`` is
``"LD.x"``, ``"lf.x"`` is ``"x"``), which is what makes ``"x"`` and ``"L0.x"`` the same term.

Values are computed on the calendar, as Stata does: ``L.x`` is the value of the *period* before,
so a gap in a unit's dates gives a missing value.  Terms can also be built without strings with
:func:`lag`, :func:`lead`, :func:`diff` and :func:`seasonal`.
"""

from __future__ import annotations

import itertools
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.data.panel import Panel

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TOKEN = re.compile(r"([lfdsLFDS])(\([^)]*\)|\d*)")


@dataclass(frozen=True)
class Term:
    """A variable with time-series operators, in canonical form.

    Attributes
    ----------
    base
        Name of the variable.
    shift
        Net lag (``L`` minus ``F``); negative for a lead.
    diff
        Order of differencing (``D``).
    seasonal
        Periods of the seasonal differences (``S``).
    raw
        The text the term was written as (kept for messages and checks; not compared).
    """

    base: str
    shift: int = 0
    diff: int = 0
    seasonal: tuple[int, ...] = ()
    raw: str = field(default="", compare=False)

    @property
    def is_operated(self) -> bool:
        """Whether any operator remains after reduction."""
        return bool(self.shift or self.diff or self.seasonal)

    @property
    def netlag(self) -> int:
        """Net lag of the term (negative for a lead)."""
        return self.shift

    @property
    def has_dsf(self) -> bool:
        """Whether the term has a ``D``, ``S`` or ``F`` operator (a current or future value)."""
        return self.diff > 0 or bool(self.seasonal) or self.shift < 0

    @property
    def name(self) -> str:
        """Canonical spelling, e.g. ``"L2D.x"``."""
        if not self.is_operated:
            return self.base
        ops = ""
        if self.shift:
            ops += ("L" if self.shift > 0 else "F") + (
                str(abs(self.shift)) if abs(self.shift) > 1 else ""
            )
        if self.diff:
            ops += "D" + (str(self.diff) if self.diff > 1 else "")
        ops += "".join("S" + (str(p) if p > 1 else "") for p in self.seasonal)
        return f"{ops}.{self.base}"

    def __str__(self) -> str:
        return self.name


def lag(name: str, k: int = 1) -> Term:
    """Return the ``k``-th lag of ``name`` (``"L{k}.name"``)."""
    return Term(name, shift=int(k), raw=f"L{k}.{name}")


def lead(name: str, k: int = 1) -> Term:
    """Return the ``k``-th lead of ``name`` (``"F{k}.name"``)."""
    return Term(name, shift=-int(k), raw=f"F{k}.{name}")


def diff(name: str, order: int = 1) -> Term:
    """Return the ``order``-th difference of ``name`` (``"D{order}.name"``)."""
    return Term(name, diff=int(order), raw=f"D{order}.{name}")


def seasonal(name: str, period: int) -> Term:
    """Return the seasonal difference of ``name`` over ``period`` periods."""
    return Term(name, seasonal=(int(period),), raw=f"S{period}.{name}")


def _numbers(text: str, term: str) -> list[int]:
    """Numbers of an operator suffix: ``""``, ``"2"``, ``"(1/3)"``, ``"(1 3)"``, ``"(1(2)5)"``."""
    if not text:
        return [1]
    if not text.startswith("("):
        return [int(text)]
    body = text[1:-1].strip()
    values: list[int] = []
    for part in re.split(r"[\s,]+", body):
        if m := re.fullmatch(r"(\d+)/(\d+)", part):
            values += range(int(m.group(1)), int(m.group(2)) + 1)
        elif m := re.fullmatch(r"(\d+)\((\d+)\)(\d+)", part):
            values += range(int(m.group(1)), int(m.group(3)) + 1, max(int(m.group(2)), 1))
        elif part.isdigit():
            values.append(int(part))
        else:
            raise SpecificationError(message("term_invalid", term=term), stata_code=198,
                                     key="term_invalid")  # fmt: skip
    if not values:
        raise SpecificationError(message("term_invalid", term=term), stata_code=198,
                                 key="term_invalid")  # fmt: skip
    return values


def _reduce(base: str, tokens: list[tuple[str, int]], raw: str) -> Term:
    shift = diff_order = 0
    periods: list[int] = []
    for letter, n in tokens:
        if letter == "l":
            shift += n
        elif letter == "f":
            shift -= n
        elif letter == "d":
            diff_order += n
        elif n > 0:
            periods.append(n)
    return Term(base, shift, diff_order, tuple(periods), raw)


def parse_term(item: str | Term) -> list[Term]:
    """Parse a term; a range such as ``"L(1/2).x"`` gives several terms.

    Raises
    ------
    SpecificationError
        If the text is not a variable name with valid operators.
    """
    # Stata: syntax varlist(ts) canonical spelling; _xdpt_tsterm (xtdpthresh.ado:2391)
    if isinstance(item, Term):
        return [item]
    text = str(item).strip()
    invalid = SpecificationError(
        message("term_invalid", term=text), stata_code=198, key="term_invalid"
    )
    *prefixes, base = text.split(".")
    if not _NAME.match(base):
        raise invalid
    ops = "".join(prefixes)
    if not prefixes:
        return [Term(base, raw=text)]
    pos, groups = 0, []
    while pos < len(ops):
        match = _TOKEN.match(ops, pos)
        if match is None or match.end() == pos:
            raise invalid
        groups.append((match.group(1).lower(), _numbers(match.group(2), text)))
        pos = match.end()
    if not groups:
        raise invalid
    return [
        _reduce(base, list(zip((g[0] for g in groups), combo, strict=True)), text)
        for combo in itertools.product(*(g[1] for g in groups))
    ]


def parse_terms(items: Iterable[str | Term]) -> list[Term]:
    """Parse several terms, expanding ranges, in order."""
    return [term for item in items for term in parse_term(item)]


def evaluate(panel: Panel, term: Term) -> FloatArray:
    """Values of ``term`` on the rows of ``panel`` (NaN where a needed period is absent)."""
    # The operators commute on a complete calendar but not when periods are missing: Stata
    # applies them from the variable outwards (seasonal differences, then differences, then
    # the shift), which is the order of the canonical spelling read from the right.
    values: FloatArray = panel.column(term.base)
    for period in term.seasonal:
        values = values - panel.lag(values, period)
    for _ in range(term.diff):
        values = values - panel.lag(values, 1)
    if term.shift:
        values = panel.lag(values, term.shift)
    return values


def names(terms: Sequence[Term]) -> list[str]:
    """Canonical spelling of each term."""
    return [t.name for t in terms]
