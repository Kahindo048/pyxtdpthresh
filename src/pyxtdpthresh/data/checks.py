"""Panel checks that Stata performs through ``xtset``.

Stata's ``xtset`` refuses repeated (unit, time) pairs and classifies the panel as strongly
balanced, weakly balanced or unbalanced; ``xthenreg`` requires the first, ``xtdpthresh``
accepts any of them provided the time step is 1.
"""

from __future__ import annotations

import difflib
from collections.abc import Iterable
from typing import Literal, NamedTuple

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import IntArray

Balance = Literal["strongly balanced", "weakly balanced", "unbalanced"]


#: Columns listed, and close names suggested, when a variable is not found.
MAX_LISTED, MAX_SUGGESTED = 10, 3


def unknown_variable(name: str, available: Iterable[object]) -> DataError:
    """Return the error for a variable that is not in the data, with what could have been meant.

    The message names the variable, suggests the columns whose name is close to it (ignoring the
    case) and lists the columns available, so that a typo is found without opening the data.
    """
    columns = [str(column) for column in available]
    lowered = {column.lower(): column for column in columns}
    close = difflib.get_close_matches(str(name).lower(), list(lowered), n=MAX_SUGGESTED, cutoff=0.6)
    text = message("variable_not_found", name=name)
    if close:
        suggestions = ", ".join(f"'{lowered[c]}'" for c in close)
        text += " " + message("variable_suggest", suggestions=suggestions)
    if columns:
        listed = ", ".join(columns[:MAX_LISTED]) + (" ..." if len(columns) > MAX_LISTED else "")
        text += " " + message("variable_available", columns=listed)
    return DataError(text, key="variable_not_found")


def as_period_numbers(
    values: np.ndarray, name: str, units: np.ndarray | None = None, unit_name: str = ""
) -> IntArray:
    """Convert a time column to integer period numbers (``xtset`` with delta 1).

    ``units`` (the identifier of each row, named ``unit_name``) lets the error say whose value
    it is.

    Raises
    ------
    DataError
        If a value is missing, infinite or not a whole number; the message gives the row.
    """
    arr = np.asarray(values)
    if arr.dtype.kind in "iu":
        return arr.astype(np.int64)

    def fail(row: int, example: object) -> DataError:
        unit = f" ({unit_name} {units[row]})" if units is not None and row < len(units) else ""
        return DataError(
            message("time_not_integer", name=name, example=example, row=row, unit=unit),
            key="time_not_integer",
        )

    if arr.dtype.kind != "f":
        raise fail(0, repr(arr.flat[0]) if arr.size else "nothing")
    bad = ~np.isfinite(arr) | (arr != np.floor(arr))
    if bad.any():
        row = int(np.flatnonzero(bad)[0])
        raise fail(row, arr[row])
    return arr.astype(np.int64)


def check_unique_pairs(
    unit: IntArray,
    time: IntArray,
    id_name: str,
    time_name: str,
    labels: np.ndarray | None = None,
) -> None:
    """Raise if a (unit, time) pair is repeated (Stata ``xtset`` error 451).

    ``unit`` and ``time`` are integer codes of equal length; ``labels`` (the identifier of each
    unit code) lets the message give the identifiers as they are in the data.
    """
    first = int(np.min(time)) if time.size else 0
    span = int(np.max(time)) - first + 1 if time.size else 1
    key = unit.astype(np.int64) * span + (time - first)
    order = np.argsort(key, kind="stable")
    sorted_key = key[order]
    repeated = np.flatnonzero(sorted_key[1:] == sorted_key[:-1])
    if repeated.size:
        rows = order[repeated[:3] + 1]

        def show(i: int) -> str:
            who = unit[i] if labels is None else labels[unit[i]]
            return f"({id_name}={who}, {time_name}={time[i]})"

        examples = ", ".join(show(int(i)) for i in rows)
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
    example: str = ""


#: Periods listed in the example of an incomplete unit.
MAX_PERIODS_LISTED = 5


def _example(
    unit: IntArray,
    time: IntArray,
    counts: IntArray,
    labels: np.ndarray | None,
    names: tuple[str, str],
) -> str:
    """Return the sentence naming the first incomplete unit and the periods it lacks."""
    periods = np.unique(time)
    first = int(np.flatnonzero(counts != periods.size)[0])
    missing = np.setdiff1d(periods, time[unit == first])
    shown = ", ".join(str(int(p)) for p in missing[:MAX_PERIODS_LISTED])
    if missing.size > MAX_PERIODS_LISTED:
        shown += ", ..."
    who = first if labels is None else labels[first]
    return message("balance_example", id=names[0], unit=who, time=names[1], periods=f"({shown})")


def balance_summary(
    unit: IntArray,
    time: IntArray,
    labels: np.ndarray | None = None,
    names: tuple[str, str] = ("unit", "time"),
) -> BalanceSummary:
    """Classify a panel like ``xtset`` does in ``r(balanced)``.

    ``unit`` holds integer unit codes (0 to n - 1) and ``time`` integer periods, with no repeated
    pair.  ``labels`` (the identifier of each code) and ``names`` (identifier and time variable)
    are used to name the first incomplete unit in the summary.
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
    example = _example(unit, time, np.bincount(unit), labels, names) if incomplete else ""
    return BalanceSummary(kind, int(counts.size), n_times, incomplete, example)


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
        + (" " + summary.example if summary.example else "")
    )


def require_strongly_balanced(unit: IntArray, time: IntArray) -> None:
    """Raise unless every unit is observed in every period (requirement of ``xthenreg``)."""
    raise_unless_strongly_balanced(balance_summary(unit, time))
