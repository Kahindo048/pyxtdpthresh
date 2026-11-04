"""Moment matrices of ``xthenreg`` as a function of the threshold, with two engines.

The model in first differences is ``dy_t = dx_t' beta + [regime terms] + de_t``.  With a jump
the regime terms are ``delta_0 (1(q_t > g) - 1(q_{t-1} > g)) + sum_k delta_k (x_tk 1(q_t > g) -
x_{t-1,k} 1(q_{t-1} > g))``; with a kink they are
``kappa ((q_t - g) 1(q_t > g) - (q_{t-1} - g) 1(q_{t-1} > g))``.  The matrix ``A(g)`` has the
instruments' moments with these terms as columns: ``[beta | delta_0 | delta]`` for a jump,
``[beta | kappa]`` for a kink.

* ``engine="fast"`` computes ``A(g)`` for the whole grid in one pass with the cumulative-sum
  kernel (:mod:`pyxtdpthresh.kernels.moments`).
* ``engine="literal"`` evaluates the formulas of the Mata code grid point by grid point on the
  ``(L, N)`` matrices, for audit and for the equivalence tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy import sparse

from pyxtdpthresh._types import FloatArray, IntArray
from pyxtdpthresh.kernels.moments import regime_moments
from pyxtdpthresh.kernels.units import unit_moments
from pyxtdpthresh.models.xthenreg.design import InstrumentSet, XthenregData

Engine = Literal["fast", "literal"]


@dataclass(frozen=True)
class XthenregProblem:
    """Everything the estimator needs, in equation-row form (row ``i * n_eq + p``).

    Attributes
    ----------
    static, kink
        Model variants.
    n_units, n_periods
        ``N`` and ``T``.
    dy, dx
        First differences of the dependent variable ``(n_rows,)`` and of the ``k`` regressors
        ``(n_rows, k)``; the first regressor is the lag of ``y`` unless ``static``.
    level_x, level_q
        Regressors ``(N * T, k)`` and threshold variable ``(N * T,)`` at the level observations
        (index ``i * T + t``).
    pair_ptr, pair_lev, pair_w
        Each equation row differences the levels at ``t`` (weight 1) and ``t - 1`` (weight -1).
    inst
        Instruments (:class:`InstrumentSet`).
    zy, zdx
        ``Z' dy / N`` and ``Z' dx / N``: the moments that do not depend on the threshold.
    """

    static: bool
    kink: bool
    n_units: int
    n_periods: int
    dy: FloatArray
    dx: FloatArray
    level_x: FloatArray
    level_q: FloatArray
    pair_ptr: IntArray
    pair_lev: IntArray
    pair_w: FloatArray
    inst: InstrumentSet
    zy: FloatArray
    zdx: FloatArray

    @property
    def k(self) -> int:
        """Number of regressors that enter linearly."""
        return int(self.dx.shape[1])

    @property
    def n_moments(self) -> int:
        """Number of moment conditions ``L``."""
        return self.inst.n_moments

    @property
    def n_params(self) -> int:
        """Coefficients other than the threshold: ``2k + 1`` for a jump, ``k + 1`` for a kink."""
        return self.k + 1 if self.kink else 2 * self.k + 1

    @property
    def regime_levels(self) -> FloatArray:
        """Level observations whose regime moments the kernel sums: ``[1, x]`` or ``[q, 1]``."""
        ones = np.ones((self.level_q.size, 1))
        if self.kink:
            return np.hstack([self.level_q[:, None], ones])
        return np.hstack([ones, self.level_x])


def make_problem(
    data: XthenregData, inst: InstrumentSet, *, static: bool = False, kink: bool = False
) -> XthenregProblem:
    """Arrange the sample and the instruments in equation-row form."""
    # Stata: GMM_var_con (xthenreg.ado:1014)
    # Stata: FD_con (xthenreg.ado:885): the first differences of y and x
    n, t_all = data.n_units, data.n_periods
    first = 1 if static else 0  # the lag-of-y block is not a regressor of the static model
    x = data.x[first:]
    k = x.shape[0]
    eq = inst.equation_index
    n_eq = eq.size
    unit_of_row = np.repeat(np.arange(n), n_eq)
    t_of_row = np.tile(eq, n)

    dy = data.y[unit_of_row, t_of_row] - data.y[unit_of_row, t_of_row - 1]
    dx = np.column_stack(
        [x[b][unit_of_row, t_of_row] - x[b][unit_of_row, t_of_row - 1] for b in range(k)]
    )
    level_x = np.nan_to_num(x.transpose(1, 2, 0).reshape(n * t_all, k))
    level_q = data.q.reshape(n * t_all)
    rows = n * n_eq
    pair_lev = np.empty(2 * rows, dtype=np.int64)
    pair_lev[0::2] = unit_of_row * t_all + t_of_row
    pair_lev[1::2] = unit_of_row * t_all + t_of_row - 1
    pair_w = np.tile([1.0, -1.0], rows)
    z = inst.z
    return XthenregProblem(
        static=static,
        kink=kink,
        n_units=n,
        n_periods=t_all,
        dy=dy,
        dx=dx,
        level_x=level_x,
        level_q=level_q,
        pair_ptr=np.arange(0, 2 * rows + 1, 2, dtype=np.int64),
        pair_lev=pair_lev,
        pair_w=pair_w,
        inst=inst,
        zy=np.asarray(z.T @ dy) / n,
        zdx=np.asarray(z.T @ dx) / n,
    )


# --------------------------------------------------------------------- A(g), two engines
def _fast_a(problem: XthenregProblem, grid: FloatArray) -> FloatArray:
    s = (
        regime_moments(
            problem.inst.z,
            problem.pair_ptr,
            problem.pair_lev,
            problem.pair_w,
            problem.regime_levels,
            problem.level_q,
            grid,
        )
        / problem.n_units
    )
    regime = (s[:, :, 0] - grid[:, None] * s[:, :, 1])[:, :, None] if problem.kink else s
    base = np.broadcast_to(problem.zdx, (grid.size, *problem.zdx.shape))
    return np.concatenate([base, regime], axis=2)


@dataclass(frozen=True)
class _Literal:
    """The ``(L, N)`` matrices of the Mata code (``x_temp1`` ... ``q_temp2``)."""

    z: FloatArray
    y: FloatArray
    x1: FloatArray
    x2: FloatArray
    x3: FloatArray
    q1: FloatArray
    q2: FloatArray


def literal_tensors(problem: XthenregProblem) -> _Literal:
    """Stack the data row by row of the moment conditions, as ``GMM_var_con`` does."""
    inst = problem.inst
    n, t_all, k = problem.n_units, problem.n_periods, problem.k
    eq = inst.equation_index
    level_x = problem.level_x.reshape(n, t_all, k)
    level_q = problem.level_q.reshape(n, t_all)
    dx = problem.dx.reshape(n, eq.size, k)
    n_mom = inst.n_moments
    y = np.empty((n_mom, n))
    x1, x2, x3 = (np.empty((n_mom, k, n)) for _ in range(3))
    q1, q2 = np.empty((n_mom, n)), np.empty((n_mom, n))
    dy = problem.dy.reshape(n, eq.size)
    for p, (start, size) in enumerate(zip(inst.block_starts, inst.block_sizes, strict=True)):
        rows = slice(start, start + size)
        t = int(eq[p])
        y[rows] = dy[:, p]
        x1[rows] = dx[:, p, :].T
        x2[rows] = level_x[:, t, :].T
        x3[rows] = level_x[:, t - 1, :].T
        q1[rows] = level_q[:, t]
        q2[rows] = level_q[:, t - 1]
    return _Literal(inst.literal(), y, x1, x2, x3, q1, q2)


def _literal_a(problem: XthenregProblem, grid: FloatArray) -> FloatArray:
    # Stata: GMM_cal (xthenreg.ado:1175) and GMM_cal_kink (1415)
    lit = literal_tensors(problem)
    n, k = problem.n_units, problem.k
    out = np.empty((grid.size, problem.n_moments, problem.n_params))
    base = np.stack([(lit.z * lit.x1[:, b, :]).sum(axis=1) / n for b in range(k)], axis=1)
    for g, gamma in enumerate(grid):
        ind2 = (lit.q1 > gamma).astype(float)
        ind3 = (lit.q2 > gamma).astype(float)
        out[g, :, :k] = base
        if problem.kink:
            kink_var = (lit.q1 - gamma) * ind2 - (lit.q2 - gamma) * ind3
            out[g, :, k] = (lit.z * kink_var).sum(axis=1) / n
        else:
            out[g, :, k] = (lit.z * (ind2 - ind3)).sum(axis=1) / n
            for b in range(k):
                shifted = lit.x2[:, b, :] * ind2 - lit.x3[:, b, :] * ind3
                out[g, :, k + 1 + b] = (lit.z * shifted).sum(axis=1) / n
    return out


def moment_matrices(
    problem: XthenregProblem, grid: FloatArray, engine: Engine = "fast"
) -> FloatArray:
    """``A(gamma)`` for every grid point, shape ``(G, L, n_params)``."""
    grid = np.ascontiguousarray(grid, dtype=np.float64)
    if engine == "fast":
        return _fast_a(problem, grid)
    if engine == "literal":
        return _literal_a(problem, grid)
    raise ValueError("engine must be 'fast' or 'literal'")


# ------------------------------------------------------------- residuals and unit moments
def regime_regressors(problem: XthenregProblem, gamma: float) -> FloatArray:
    """Regime columns of the first-differenced regressors at one threshold, ``(n_rows, r)``."""
    above = (problem.level_q > gamma).astype(float)
    levels = (problem.regime_levels * above[:, None])[problem.pair_lev] * problem.pair_w[:, None]
    summed = np.add.reduceat(levels, problem.pair_ptr[:-1], axis=0)
    if problem.kink:
        # (q - g) 1(q > g) = q 1(q > g) - g 1(q > g): columns [q, 1]
        return np.asarray(summed[:, :1] - gamma * summed[:, 1:], dtype=np.float64)
    return np.asarray(summed, dtype=np.float64)


def residual_rows(problem: XthenregProblem, theta: FloatArray, gamma: float) -> FloatArray:
    """First-difference residuals of every equation row at ``(theta, gamma)``."""
    # Stata: ep_cal (xthenreg.ado:1208) and ep_cal_kink (1250)
    design = np.hstack([problem.dx, regime_regressors(problem, gamma)])
    return np.asarray(problem.dy - design @ theta, dtype=np.float64)


def moments_by_unit(problem: XthenregProblem, resid: FloatArray) -> FloatArray:
    """Moment contributions ``g_i = sum_rows Z * resid`` of every unit, ``(N, L)``."""
    z: sparse.csr_matrix = problem.inst.z
    return unit_moments(z, resid, problem.inst.unit_ptr)
