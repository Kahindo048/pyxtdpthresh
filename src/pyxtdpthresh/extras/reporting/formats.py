"""Number formats and significance stars of the tables (layer 6)."""

from __future__ import annotations

import math
from collections.abc import Sequence

#: Symbol repeated once per level a p-value is under.
STAR = "*"
#: Default significance levels, loosest first: ``*`` under 0.1, ``**`` under 0.05, ``***`` under
#: 0.01.
DEFAULT_LEVELS = (0.1, 0.05, 0.01)
#: What an empty or undefined cell shows.
MISSING = "-"


def number(value: float | None, digits: int = 3, decimal: str = ".") -> str:
    """Return ``value`` with ``digits`` decimals (``-`` when it is missing); no negative zero."""
    if value is None or not math.isfinite(value):
        return MISSING
    text = f"{value:.{digits}f}"
    if text.startswith("-") and float(text) == 0.0:
        text = text[1:]
    return text.replace(".", decimal)


def integer(value: float | None) -> str:
    """Return a whole number without a decimal part (``-`` when it is missing)."""
    if value is None or not math.isfinite(value):
        return MISSING
    return str(round(value))


def interval(low: float | None, high: float | None, digits: int = 3, decimal: str = ".") -> str:
    """Return ``[low, high]`` with ``digits`` decimals (``-`` when a bound is missing)."""
    if low is None or high is None or not (math.isfinite(low) and math.isfinite(high)):
        return MISSING
    return f"[{number(low, digits, decimal)}, {number(high, digits, decimal)}]"


def star_count(p_value: float | None, levels: Sequence[float] = DEFAULT_LEVELS) -> int:
    """Return how many of the ``levels`` the p-value is strictly under (0 when undefined)."""
    if p_value is None or not math.isfinite(p_value):
        return 0
    return sum(p_value < level for level in levels)


def star_note(levels: Sequence[float] = DEFAULT_LEVELS, decimal: str = ".") -> str:
    """Return the legend of the stars, for example ``*p<0.1; **p<0.05; ***p<0.01``."""
    parts = [
        f"{STAR * (rank + 1)}p<{format(level, 'g').replace('.', decimal)}"
        for rank, level in enumerate(sorted(levels, reverse=True))
    ]
    return "; ".join(parts)
