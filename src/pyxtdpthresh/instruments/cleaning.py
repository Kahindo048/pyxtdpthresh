"""Removal of instrument columns that carry no information, in the order of the Stata command.

1. columns that are multiples of the period constants (a variable common to all units in a
   period: a macro series, a trend) are zeroed (:func:`drop_cell_constant`);
2. columns that are exactly zero are dropped (a lag depth no unit reaches);
3. exact duplicate columns are dropped, the first one is kept (:func:`duplicate_columns`);
4. columns that are linear combinations of the columns before them are dropped
   (:func:`dependent_columns`).

The instruments do not depend on the threshold, so the cleaning is done once.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.kernels.cleaning import independent_columns

#: Smallest squared relative residual for a column to be kept as independent.
INDEPENDENCE_TOL = 1e-13
#: Relative residual above which a dropped column is not a linear combination of the others.
NEAR_DEPENDENCE_TOL = 1e-10
#: Relative tolerance on the equality of the values of a trend-like column across periods.
ACROSS_CELLS_RTOL = 1e-10


@dataclass(frozen=True)
class CleanedInstruments:
    """Instruments after cleaning and what was removed.

    Attributes
    ----------
    z
        Cleaned ``(n, k)`` matrix.
    rows
        Index, in the input, of each kept row (all rows unless a partialling dropped some).
    columns
        Index, in the raw matrix, of each kept column.
    n_common
        Columns removed as multiples of the period constants (``e(N_iv_common)``).
    n_zero, n_duplicate
        Columns removed for being exactly zero or a duplicate.
    n_dependent
        Columns removed as linear combinations of earlier ones (``e(N_iv_dep)``).
    dep_res
        Largest relative residual of a dependent column on the kept ones, NaN when none
        was removed (``e(iv_dep_res)``).
    dep_near
        Dependent columns whose relative residual exceeds ``1e-10``: they are not linear
        combinations of the kept columns (``e(N_iv_dep_near)``).
    """

    z: FloatArray
    rows: IntArray
    columns: IntArray
    n_common: int
    n_zero: int
    n_duplicate: int
    n_dependent: int
    dep_res: float
    dep_near: int


def _cells(times: IntArray) -> tuple[IntArray, list[IntArray]]:
    """Cell (distinct period) of each row and the rows of each cell, in period order."""
    _, cell_of_row = np.unique(times, return_inverse=True)
    order = np.argsort(cell_of_row, kind="stable")
    bounds = np.flatnonzero(np.diff(cell_of_row[order])) + 1
    return cell_of_row.astype(np.int64) + 1, np.split(order, bounds)


class _CellScan(NamedTuple):
    """Per column: constant in every cell, nonzero cells, first such cell and value, one value."""

    constant: BoolArray
    nonzero_cells: IntArray
    first_cell: IntArray
    first_value: FloatArray
    same_value: BoolArray


def _scan_cells(z: FloatArray, groups: list[IntArray]) -> _CellScan:
    """Scan the columns cell by cell (``xdpt2_drop_cellconst``, first loop)."""
    k = z.shape[1]
    constant = np.ones(k, dtype=bool)
    nonzero_cells = np.zeros(k, dtype=np.int64)
    first_cell = np.zeros(k, dtype=np.int64)
    first_value = np.zeros(k)
    same_value = np.ones(k, dtype=bool)
    for c, rows in enumerate(groups, start=1):
        sub = z[rows]
        if rows.size == 1:
            constant &= sub[0] == 0
            continue
        high, low = sub.max(axis=0), sub.min(axis=0)
        constant &= high == low
        nonzero = constant & (high != 0)
        new = nonzero & (first_cell == 0)
        first_cell = first_cell + new * c
        first_value = first_value + new * high
        same_value &= ~nonzero | (
            np.abs(high - first_value) <= ACROSS_CELLS_RTOL * np.abs(first_value)
        )
        nonzero_cells += nonzero
    return _CellScan(constant, nonzero_cells, first_cell, first_value, same_value)


def drop_cell_constant(z: FloatArray, times: IntArray) -> tuple[FloatArray, int]:
    """Zero the columns that are linear combinations of the period constants kept before them.

    A variable that takes one value for every unit in a period gives, in the per-period layout,
    a column equal to that value times the constant of the period (or, collapsed, a multiple
    of the all-ones column).  Such a column adds no moment.  Only columns that are constant
    within every period are candidates; a period with a single row cannot show constancy, so a
    column that is nonzero there is never one.

    Returns
    -------
    z, n_dropped
        A copy of ``z`` with the dropped columns set to zero, and their number.
    """
    # Stata: xdpt2_drop_cellconst (xtdpthresh.ado:3304)
    n, k = z.shape
    if k < 2 or n < 2:
        return z, 0
    cell_of_row, groups = _cells(times)
    n_cells = len(groups)
    scan = _scan_cells(z, groups)
    constant, nonzero_cells = scan.constant, scan.nonzero_cells
    first_cell, same_value = scan.first_cell, scan.same_value
    if not np.any(constant & (nonzero_cells > 0)):
        return z, 0

    out = z.copy()
    spanned = np.zeros(n_cells + 1, dtype=bool)  # cells whose indicator is already kept
    free = n_cells
    all_ones = False
    dropped = 0
    for j in np.flatnonzero(constant & (nonzero_cells > 0)):
        if nonzero_cells[j] == 1:
            c = int(first_cell[j])
            drop = bool(spanned[c]) or (all_ones and free == 1)
            if not drop:
                spanned[c] = True
                free -= 1
        elif nonzero_cells[j] == n_cells and same_value[j]:
            drop = free == 0 or all_ones
            if not drop:
                all_ones = True
        elif free == 0:
            drop = True
        else:
            drop = _spanned_by_cells(out[:, j], cell_of_row, spanned, n_cells, all_ones, free)
        if drop:
            out[:, j] = 0.0
            dropped += 1
    return out, dropped


def _spanned_by_cells(
    column: FloatArray,
    cell_of_row: IntArray,
    spanned: BoolArray,
    n_cells: int,
    all_ones: bool,
    free: int,
) -> bool:
    """One value per cell: spanned if it vanishes off the kept cells or is one common value."""
    nonzero_rows = np.flatnonzero(column != 0)
    value_by_cell = np.zeros(n_cells + 1)
    value_by_cell[cell_of_row[nonzero_rows]] = column[nonzero_rows]
    open_cells = np.flatnonzero((value_by_cell != 0) & ~spanned)
    if open_cells.size == 0:
        return True
    if all_ones and open_cells.size == free:
        values = value_by_cell[open_cells]
        return bool(
            np.all(np.abs(values - values[0]) <= ACROSS_CELLS_RTOL * np.max(np.abs(values)))
        )
    return False


def duplicate_columns(z: FloatArray) -> BoolArray:
    """Mask of the columns to keep when exact duplicates are dropped (the first is kept)."""
    # Stata: xdpt2_nodup_cols (xtdpthresh.ado:3244)
    n, k = z.shape
    keep = np.ones(k, dtype=bool)
    if k < 2 or n == 0:
        return keep
    total = z.sum(axis=0)
    weighted = _row_weighted_sums(z)
    order = np.lexsort((np.arange(k), weighted, total))
    same = (total[order][1:] == total[order][:-1]) & (weighted[order][1:] == weighted[order][:-1])
    starts = np.concatenate([[0], np.flatnonzero(~same) + 1, [k]])
    for lo, hi in zip(starts[:-1], starts[1:], strict=True):
        group = order[lo:hi]
        for pos in range(1, group.size):
            for earlier in group[:pos]:
                if keep[earlier] and np.array_equal(z[:, earlier], z[:, group[pos]]):
                    keep[group[pos]] = False
                    break
    return keep


def _row_weighted_sums(z: FloatArray, chunk: int = 256) -> FloatArray:
    """``sum_r r * z[r, j]`` with the same order of additions for every column.

    A matrix product would sum identical columns in different orders depending on their
    position, and two equal columns must get equal signatures.
    """
    weights = np.arange(1, z.shape[0] + 1, dtype=np.float64)[:, None]
    out = np.empty(z.shape[1])
    for start in range(0, z.shape[1], chunk):
        out[start : start + chunk] = (z[:, start : start + chunk] * weights).sum(axis=0)
    return out


def dependent_columns(z: FloatArray) -> BoolArray:
    """Mask of the columns kept when linear combinations of earlier columns are dropped.

    Cholesky in column order on the Gram matrix scaled to a unit diagonal: a column is kept
    when its squared relative residual after the kept earlier columns is at least ``1e-13``.
    A matrix whose Cholesky factor has no such small pivot keeps every column, which is
    checked first with one LAPACK factorisation.
    """
    # Stata: xdpt2_indep_cols (xtdpthresh.ado:3177)
    n, k = z.shape
    keep = np.ones(k, dtype=bool)
    if k < 2 or n == 0:
        return keep
    gram = z.T @ z
    scale = np.sqrt(np.diag(gram))
    if not np.all(np.isfinite(scale)) or np.any(scale <= 0):
        return keep
    gram = gram / np.outer(scale, scale)
    try:
        factor = np.linalg.cholesky(gram)
    except np.linalg.LinAlgError:
        return np.asarray(independent_columns(gram, INDEPENDENCE_TOL))
    if np.all(np.diag(factor) ** 2 >= INDEPENDENCE_TOL):
        return keep
    return np.asarray(independent_columns(gram, INDEPENDENCE_TOL))


def dependence_residuals(z: FloatArray, kept: BoolArray) -> FloatArray:
    """Relative residual of each dropped column on the span of the kept ones (QR on ``z``)."""
    # Stata: xdpt2_indep_cols, diagnostics block (xtdpthresh.ado:3216-3231)
    dropped = z[:, ~kept]
    basis = z[:, kept]
    if basis.shape[1] >= z.shape[0]:
        return np.zeros(dropped.shape[1])
    basis = basis / np.sqrt(np.sum(basis**2, axis=0))
    unit = dropped / np.sqrt(np.sum(dropped**2, axis=0))
    q, _ = np.linalg.qr(basis)
    return np.asarray(np.sqrt(np.sum((unit - q @ (q.T @ unit)) ** 2, axis=0)))


def clean_instruments(
    z: FloatArray,
    times: IntArray,
    partial: Callable[[FloatArray], tuple[FloatArray, IntArray]] | None = None,
) -> CleanedInstruments:
    """Remove the columns that carry no information, in the order of the Stata command.

    Parameters
    ----------
    z
        ``(n, k)`` raw instruments of the stacked equations.
    times
        Period of each row.
    partial
        Time-effect partialling applied after the period-constant step, as the Stata command
        does: it receives the matrix and returns the projected matrix restricted to the rows it
        keeps, with the indices of those rows.
    """
    # Stata: xdpt2_stack_at_gamma (xtdpthresh.ado:3543-3797)
    n_raw = z.shape[1]
    columns = np.arange(n_raw, dtype=np.int64)
    work = z
    n_common = n_zero = n_duplicate = n_dependent = 0
    dep_res, dep_near = float("nan"), 0
    if work.shape[0] > 1 and n_raw > 1:
        work, n_common = drop_cell_constant(work, times)
    rows = np.arange(work.shape[0], dtype=np.int64)
    if partial is not None:
        work, rows = partial(work)
    if work.shape[0] > 0:
        nonzero = np.sum(np.abs(work), axis=0) > 0
        if 0 < int(nonzero.sum()) < work.shape[1]:
            n_zero = int((~nonzero).sum())
            work, columns = work[:, nonzero], columns[nonzero]
    if work.shape[0] > 0 and work.shape[1] > 1:
        unique = duplicate_columns(work)
        n_duplicate = int((~unique).sum())
        work, columns = work[:, unique], columns[unique]
    if work.shape[0] > 0 and work.shape[1] > 1:
        independent = dependent_columns(work)
        n_dependent = int((~independent).sum())
        if n_dependent:
            residuals = dependence_residuals(work, independent)
            dep_res = float(np.max(residuals))
            dep_near = int(np.sum(residuals > NEAR_DEPENDENCE_TOL))
            work, columns = work[:, independent], columns[independent]
    return CleanedInstruments(
        np.ascontiguousarray(work),
        rows,
        columns,
        n_common,
        n_zero,
        n_duplicate,
        n_dependent,
        dep_res,
        dep_near,
    )
