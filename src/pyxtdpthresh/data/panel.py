"""Panel stored as contiguous arrays, one block of rows per unit.

Rows are sorted by (unit, time) and the units are delimited by ``offsets`` (CSR style), so a
Numba kernel can loop ``for i in range(n_units): for r in range(offsets[i], offsets[i+1])``
without any Python object.  The layout replaces the array of per-unit structures of the Mata
code (``xdpt2_unit``) and keeps the same information: times, values and, once the model
layer adds it, the equation flag.
"""

from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import DataError, PyxdpthreshWarning
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.data.checks import (
    Balance,
    BalanceSummary,
    as_period_numbers,
    balance_summary,
    check_unique_pairs,
    unknown_variable,
)
from pyxtdpthresh.data.sampling import resolve_where


@dataclass(frozen=True)
class Panel:
    """Rows sorted by (unit, time), the units delimited by ``offsets``.

    Attributes
    ----------
    unit_labels
        Original identifier of each unit, in sorted order (length ``n_units``).
    offsets
        Unit ``i`` owns rows ``offsets[i]:offsets[i + 1]`` (length ``n_units + 1``).
    time
        Integer period of each row.
    source_row
        Position of each row in the frame the panel was built from (to map results back).
    names
        Name of each column of ``values``.
    values
        ``(n_rows, n_columns)`` float array; missing values are NaN.
    balance
        Balance of the whole input as ``xtset`` reports it, before ``where`` is applied.
    id_name, time_name
        Names of the identifier and time variables.
    balance_summary
        Counts behind ``balance``.
    """

    unit_labels: np.ndarray
    offsets: IntArray
    time: IntArray
    source_row: IntArray
    names: tuple[str, ...]
    values: FloatArray
    balance: Balance
    id_name: str = "id"
    time_name: str = "time"
    balance_summary: BalanceSummary | None = None

    def __post_init__(self) -> None:
        for arr in (self.offsets, self.time, self.source_row, self.values):
            arr.flags.writeable = False

    @property
    def n_units(self) -> int:
        """Number of units."""
        return int(self.offsets.size - 1)

    @property
    def n_rows(self) -> int:
        """Number of rows."""
        return int(self.time.size)

    @property
    def unit_of_row(self) -> IntArray:
        """Index (0-based) of the unit that owns each row."""
        return np.repeat(np.arange(self.n_units, dtype=np.int64), np.diff(self.offsets))

    def column(self, name: str) -> FloatArray:
        """Values of one column (a view)."""
        if name not in self.names:
            raise unknown_variable(name, self.names)
        column: FloatArray = self.values[:, self.names.index(name)]
        return column

    def columns(self, names: Sequence[str]) -> FloatArray:
        """Values of several columns as an ``(n_rows, len(names))`` array."""
        return (
            np.column_stack([self.column(n) for n in names])
            if names
            else np.empty((self.n_rows, 0))
        )

    def lag(self, x: FloatArray, k: int = 1) -> FloatArray:
        """Value of ``x`` ``k`` periods earlier in the same unit, NaN when that row is absent.

        This is Stata's ``L{k}.x`` with a time step of 1: it looks up the *period*
        ``t - k`` in the unit, so a gap in the calendar gives a missing value rather than
        the previous observation.  A negative ``k`` gives the lead ``F{-k}.x``.
        """
        x = np.asarray(x, dtype=np.float64)
        if self.n_rows == 0:
            return np.zeros(0, dtype=np.float64)
        unit = self.unit_of_row
        t0 = int(np.min(self.time))
        span = int(np.max(self.time)) - t0 + 1 + abs(k)
        key = unit * span + (self.time - t0)
        target = key - k
        pos = np.searchsorted(key, target)
        pos_clipped = np.minimum(pos, key.size - 1)
        found = (pos < key.size) & (key[pos_clipped] == target)
        return np.asarray(np.where(found, x[pos_clipped], np.nan), dtype=np.float64)

    def with_columns(self, extra: Mapping[str, FloatArray]) -> Panel:
        """Panel with extra (derived) columns appended."""
        new = np.column_stack([self.values, *(np.asarray(v, float) for v in extra.values())])
        return replace(self, names=(*self.names, *extra), values=new)

    def select(self, mask: BoolArray) -> Panel:
        """Panel restricted to the rows where ``mask`` holds; units left empty disappear."""
        keep = np.asarray(mask, dtype=np.bool_)
        counts = (
            np.add.reduceat(keep.astype(np.int64), self.offsets[:-1])
            if self.n_rows
            else (np.zeros(self.n_units, dtype=np.int64))
        )
        present = counts > 0
        offsets = np.concatenate([[0], np.cumsum(counts[present])]).astype(np.int64)
        return replace(
            self,
            unit_labels=self.unit_labels[present],
            offsets=offsets,
            time=self.time[keep],
            source_row=self.source_row[keep],
            values=self.values[keep],
        )


def _numeric(frame: pd.DataFrame, name: str) -> FloatArray:
    if name not in frame.columns:
        raise unknown_variable(name, frame.columns)
    col = frame[name]
    if not (pd.api.types.is_numeric_dtype(col) or pd.api.types.is_bool_dtype(col)):
        raise DataError(message("column_not_numeric", name=name, dtype=str(col.dtype)))
    values = np.array(col.to_numpy(dtype=np.float64, na_value=np.nan), dtype=np.float64)
    infinite = np.isinf(values)
    if infinite.any():
        # Stata has no infinity: a number that overflows is missing (log(0), 1/0)
        warnings.warn(
            message("warn_infinite", n=int(infinite.sum()), name=name),
            PyxdpthreshWarning,
            stacklevel=2,
        )
        values[infinite] = np.nan
    return values


def _key_column(frame: pd.DataFrame, name: str | None, level: int) -> tuple[str, pd.Series]:
    """Return the identifier or time as a Series, from a column or an index level."""
    if name is not None:
        if name in frame.columns:
            return name, frame[name].reset_index(drop=True)
        if name in frame.index.names:
            return name, pd.Series(frame.index.get_level_values(name))
        raise unknown_variable(name, [*frame.columns, *(n for n in frame.index.names if n)])
    if frame.index.nlevels != 2:
        raise DataError(message("keys_not_found"))
    label = frame.index.names[level] or ("id", "time")[level]
    return str(label), pd.Series(frame.index.get_level_values(level))


def build_panel(
    frame: pd.DataFrame,
    columns: Sequence[str],
    *,
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
) -> Panel:
    """Build a :class:`Panel` from a long-form DataFrame.

    Parameters
    ----------
    frame
        Long data, one row per (unit, period).
    columns
        Numeric columns to keep, in the order they appear in ``Panel.values``.
    id, time
        Identifier and time columns (or index level names).  When omitted, the two levels of a
        MultiIndex are used, in that order.
    where
        Row selection, see :func:`pyxtdpthresh.data.sampling.resolve_where`.  The balance and
        the repeated-pair check use all rows with non-missing keys, as ``xtset`` does.

    Raises
    ------
    DataError
        On missing keys, repeated (unit, time) pairs, non-integer time, unknown or non-numeric
        columns, or an empty selection.
    """
    id_name, id_series = _key_column(frame, id, 0)
    time_name, time_series = _key_column(frame, time, 1)

    missing_id = id_series.isna().to_numpy()
    missing_time = time_series.isna().to_numpy()
    for what, bad in ((id_name, missing_id), (time_name, missing_time)):
        if bad.any():
            rows = np.flatnonzero(bad)[:3].tolist()
            raise DataError(
                message("panel_key_missing", what=what, n=int(bad.sum()), rows=rows),
                stata_code=459,
            )

    codes, labels = pd.factorize(id_series, sort=True)
    unit_code = codes.astype(np.int64)
    period = as_period_numbers(time_series.to_numpy(), time_name, id_series.to_numpy(), id_name)
    check_unique_pairs(unit_code, period, id_name, time_name, np.asarray(labels))
    summary = balance_summary(unit_code, period, np.asarray(labels), (id_name, time_name))

    data = (
        np.column_stack([_numeric(frame, c) for c in columns])
        if columns
        else np.empty((len(frame), 0))
    )
    keep = resolve_where(frame, where)
    if not keep.any():
        raise DataError(message("no_usable_obs"), stata_code=2000)

    position = np.flatnonzero(keep)
    order = position[np.lexsort((period[position], unit_code[position]))]
    kept_codes = unit_code[order]
    present, counts = np.unique(kept_codes, return_counts=True)
    offsets = np.concatenate([[0], np.cumsum(counts)]).astype(np.int64)
    return Panel(
        unit_labels=np.asarray(labels)[present],
        offsets=offsets,
        time=period[order],
        source_row=order.astype(np.int64),
        names=tuple(columns),
        values=np.ascontiguousarray(data[order]),
        balance=summary.kind,
        id_name=id_name,
        time_name=time_name,
        balance_summary=summary,
    )
