"""Panel checks that Stata performs through ``xtset``.

Stata's ``xtset`` refuses repeated (unit, time) pairs and classifies the panel as strongly
balanced, weakly balanced or unbalanced; ``xthenreg`` requires the first, ``xtdpthresh``
accepts any of them provided the time step is 1.
"""

from __future__ import annotations

from typing import Literal, NamedTuple

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import IntArray

Balance = Literal["strongly balanced", "weakly balanced", "unbalanced"]


def as_period_numbers(values: np.ndarray, name: str) -> IntArray:
    """Convert a time column to integer period numbers (``xtset`` with delta 1).

    Raises
    ------
    DataError
        If a value is missing, infinite or not a whole number.
    """
    arr = np.asarray(values)
    if arr.dtype.kind in "iu":
        return arr.astype(np.int64)
    if arr.dtype.kind != "f":
        raise DataError(message("time_not_integer", name=name, example=repr(arr.flat[0])))
    bad = ~np.isfinite(arr) | (arr != np.floor(arr))
    if bad.any():
        raise DataError(message("time_not_integer", name=name, example=arr[bad][0]))
    return arr.astype(np.int64)


def check_unique_pairs(unit: IntArray, time: IntArray, id_name: str, time_name: str) -> None:
    """Raise if a (unit, time) pair is repeated (Stata ``xtset`` error 451).

    ``unit`` and ``time`` are integer codes of equal length.
    """
    first = int(np.min(time)) if time.size else 0
    span = int(np.max(time)) - first + 1 if time.size else 1
    key = unit.astype(np.int64) * span + (time - first)
    order = np.argsort(key, kind="stable")
    sorted_key = key[order]
    repeated = np.flatnonzero(sorted_key[1:] == sorted_key[:-1])
    if repeated.size:
        rows = order[repeated[:3] + 1]
        examples = ", ".join(f"({unit[i]}, {time[i]})" for i in rows)
        raise DataError(
            message(
                "panel_duplicates",
                n=int(repeated.size),
                id=id_name,
                time=time_name,
                examples=examples,
            ),
            stata_code=451,
        )


class BalanceSummary(NamedTuple):
    """Balance of a panel as ``xtset`` reports it, with the counts behind the verdict."""

    kind: Balance
    n_units: int
    n_times: int
    n_incomplete: int


def balance_summary(unit: IntArray, time: IntArray) -> BalanceSummary:
    """Classify a panel like ``xtset`` does in ``r(balanced)``.

    ``unit`` holds integer unit codes and ``time`` integer periods, with no repeated pair.
    """
    if unit.size == 0:
        return BalanceSummary("strongly balanced", 0, 0, 0)
    n_times = int(np.unique(time).size)
    counts = np.bincount(unit)
    counts = counts[counts > 0]
    incomplete = int(np.sum(counts != n_times))
    if incomplete == 0:
        kind: Balance = "strongly balanced"
    elif np.all(counts == counts[0]):
        kind = "weakly balanced"
    else:
        kind = "unbalanced"
    return BalanceSummary(kind, int(counts.size), n_times, incomplete)


def classify_balance(unit: IntArray, time: IntArray) -> Balance:
    """Balance of a panel as reported by ``xtset`` in ``r(balanced)``."""
    return balance_summary(unit, time).kind


def raise_unless_strongly_balanced(summary: BalanceSummary) -> None:
    """Raise if the panel is not strongly balanced (requirement of ``xthenreg``)."""
    if summary.kind == "strongly balanced":
        return
    raise DataError(
        message("not_balanced")
        + " "
        + message(
            "balance_detail",
            kind=summary.kind,
            n_incomplete=summary.n_incomplete,
            n_units=summary.n_units,
            n_times=summary.n_times,
        )
    )


def require_strongly_balanced(unit: IntArray, time: IntArray) -> None:
    """Raise unless every unit is observed in every period (requirement of ``xthenreg``)."""
    raise_unless_strongly_balanced(balance_summary(unit, time))
