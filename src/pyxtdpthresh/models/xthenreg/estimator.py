"""Two-step GMM estimation of the threshold model (``xthenreg``, Seo and Shin 2016).

Step 1 uses the MA(1) weight matrix of first-differenced errors and searches the threshold
over the grid (first minimum of the criterion).  Step 2 re-weights with the inverse of the
centred covariance of the unit moments evaluated at the step-1 estimate and searches again.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.gmm import GridSolution, solve_grid
from pyxtdpthresh.core.weights import ma1_weight, second_step_weight
from pyxtdpthresh.models.xthenreg.moments import (
    Engine,
    XthenregProblem,
    moment_matrices,
    moments_by_unit,
    residual_rows,
)


@dataclass(frozen=True)
class StepResult:
    """Result of one GMM step.

    Attributes
    ----------
    weight
        Weight matrix used, ``(L, L)``.
    solution
        GMM solution at every grid point.
    index
        Position of the first minimum of the criterion on the grid.
    gamma
        Threshold estimate (``grid[index]``).
    theta
        Coefficients at the estimated threshold, without the threshold itself.
    """

    weight: FloatArray
    solution: GridSolution
    index: int
    gamma: float
    theta: FloatArray

    @property
    def criterion(self) -> FloatArray:
        """Criterion at every grid point."""
        return self.solution.crit


@dataclass(frozen=True)
class TwoStepFit:
    """Both GMM steps and the matrices the covariance needs.

    Attributes
    ----------
    grid
        Candidate thresholds.
    a
        Moment matrices ``A(gamma)`` for every grid point, ``(G, L, n_params)``.
    first, second
        Step results.
    omega_inv
        Inverse of the centred covariance of the step-2 unit moments (called ``omega_hat``
        in the Stata code, although it estimates the inverse of the moment covariance).
    resid
        Step-2 residuals of the equation rows.
    """

    grid: FloatArray
    a: FloatArray
    first: StepResult
    second: StepResult
    omega_inv: FloatArray
    resid: FloatArray

    @property
    def estimates(self) -> FloatArray:
        """Coefficients followed by the threshold, as returned in ``e(b)``."""
        return np.append(self.second.theta, self.second.gamma)


def first_minimum(criterion: FloatArray) -> int:
    """Index of the first smallest value; missing values never win (Mata ``minindex``)."""
    return int(np.argmin(np.where(np.isnan(criterion), np.inf, criterion)))


def _step(a: FloatArray, y: FloatArray, weight: FloatArray, grid: FloatArray) -> StepResult:
    solution = solve_grid(a, y, weight)
    index = first_minimum(solution.crit)
    return StepResult(weight, solution, index, float(grid[index]), solution.theta[index])


def fit(problem: XthenregProblem, grid: FloatArray, engine: Engine = "fast") -> TwoStepFit:
    """Estimate the model in two steps over a grid of thresholds.

    Parameters
    ----------
    problem
        Data and instruments in equation-row form.
    grid
        Candidate thresholds in increasing order.
    engine
        ``"fast"`` (cumulative sums over the grid) or ``"literal"`` (formulas of the Mata
        code, point by point).
    """
    # Stata: maincode_0719, steps 2 and 3 (xthenreg.ado:454-791)
    grid = np.ascontiguousarray(grid, dtype=np.float64)
    a = moment_matrices(problem, grid, engine)
    first = _step(a, problem.zy, ma1_weight(problem.inst.blocks()), grid)

    resid1 = residual_rows(problem, first.theta, first.gamma)
    weight2 = second_step_weight(moments_by_unit(problem, resid1))
    second = _step(a, problem.zy, weight2, grid)

    resid2 = residual_rows(problem, second.theta, second.gamma)
    omega_inv = second_step_weight(moments_by_unit(problem, resid2))
    return TwoStepFit(grid, a, first, second, omega_inv, resid2)
