"""GMM estimation of ``xtdpthresh`` at a given threshold.

Two steps, as in the Stata command:

1. the first step uses the weight ``W1`` of the stack (Arellano-Bond MA(1) weight for first
   differences, with fallbacks);
2. the residuals of the first step give the cluster covariance ``Omega`` of the moments, whose
   inverse ``W2`` is the second-step weight.  When ``Omega`` cannot be inverted the estimator
   stays at one step and says so (``twostep=False``).

The variance reported is the robust sandwich of the weight that was actually used, so it is
valid also for a one-step estimator.  ``W2`` is built once from the first-step threshold and then
held fixed while the second-step criterion is evaluated at other thresholds (block E.5).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.gmm import FixedWeightFit, cluster_omega, sandwich, solve_fixed_weight
from pyxtdpthresh.core.linalg import syminv
from pyxtdpthresh.kernels.units import unit_moments_arrays
from pyxtdpthresh.models.xtdpthresh.stack import Stack


@dataclass(frozen=True)
class ThresholdFit:
    """Estimates at one threshold.

    Attributes
    ----------
    gamma
        Threshold.
    theta
        Coefficients ``[X, regime change, X x regime]`` (jump) or ``[X, slope change]`` (kink).
    obj
        Criterion of the step that produced ``theta``.
    cov
        Cluster-robust variance of ``theta`` conditional on the threshold.
    weight
        Weight matrix used.
    twostep
        True when ``weight`` is the second-step weight.
    first_theta, first_obj
        Estimates and criterion of the first step.
    """

    gamma: float
    theta: FloatArray
    obj: float
    cov: FloatArray
    weight: FloatArray
    twostep: bool
    first_theta: FloatArray
    first_obj: float


@dataclass(frozen=True)
class StepProblem:
    """Cross products of the stack at one threshold."""

    gamma: float
    regressors: FloatArray
    zw: FloatArray

    def residual(self, stack: Stack, theta: FloatArray) -> FloatArray:
        """Residuals of the transformed equations."""
        return np.asarray(stack.dy - self.regressors @ theta)


def problem_at(stack: Stack, gamma: float) -> StepProblem:
    """Regressors and ``Z'X / n`` of the stack at threshold ``gamma``."""
    regressors = stack.regressors(gamma)
    return StepProblem(gamma, regressors, stack.z.rmatmul(regressors) / stack.n_rows)


def moments_by_unit(stack: Stack, resid: FloatArray) -> FloatArray:
    """Moment contribution ``g_i = sum_e z_e resid_e`` of each unit, ``(n_units, L)``."""
    # Stata: xdpt2_gsum_by_unit (xtdpthresh.ado:3957-4000)
    csr = stack.z.csr
    indptr, indices = stack.z.csr64
    return unit_moments_arrays(indptr, indices, csr.data, csr.shape, resid, stack.unit_ptr)


def contributing_moments(stack: Stack, resid: FloatArray) -> FloatArray:
    """Return the unit moments of the units that have a stacked equation, ``(n_units, L)``.

    The bootstrap weights are drawn for these units only (a unit without equation takes no draw),
    so the rows line up with the weight matrix.
    """
    # Stata: xdpt2_dense_uid (xtdpthresh.ado:4740-4759): draws are indexed by contributing units
    moments = moments_by_unit(stack, resid)
    return moments if stack.n_units == moments.shape[0] else moments[np.diff(stack.unit_ptr) > 0]


def omega_of(stack: Stack, resid: FloatArray, *, center: bool) -> FloatArray:
    """Cluster covariance of the moments for the residuals ``resid``."""
    # Stata: xdpt2_build_cluster_omega (xtdpthresh.ado:4001-4011)
    return cluster_omega(moments_by_unit(stack, resid), stack.n_rows, stack.n_units, center)


def second_step_weight(
    stack: Stack, step: StepProblem, theta: FloatArray, *, center: bool
) -> tuple[FloatArray, FloatArray | None]:
    """Cluster covariance ``Omega`` of the moments at ``theta`` and its inverse.

    Returns
    -------
    omega, weight
        ``weight`` is None when ``Omega`` cannot be inverted (the estimator stays at one step).
    """
    # Stata: xdpt2_grid_search, "W2 is constructed exactly once" (xtdpthresh.ado:5834)
    omega = omega_of(stack, step.residual(stack, theta), center=center)
    inverse = syminv(omega)
    return omega, (inverse.inv if inverse.ok else None)


def first_step(stack: Stack, step: StepProblem) -> FixedWeightFit:
    """One-step estimate with the first-step weight of the stack."""
    return solve_fixed_weight(step.zw, stack.zy, stack.first_weight.weight, stack.n_rows)


def second_step(stack: Stack, step: StepProblem, weight: FloatArray) -> FixedWeightFit:
    """Estimate with a given (second-step) weight."""
    return solve_fixed_weight(step.zw, stack.zy, weight, stack.n_rows)


def estimate_at(stack: Stack, gamma: float, *, center: bool = True) -> ThresholdFit | None:
    """Two-step estimate when the threshold is the same in both steps.

    The first-step residuals at ``gamma`` give ``W2``; the second step is solved at the same
    ``gamma``.  Without an invertible ``Omega`` the one-step estimate and its sandwich are
    returned.  ``None`` when the first step is rejected.
    """
    step = problem_at(stack, gamma)
    one = first_step(stack, step)
    if not one.ok:
        return None
    omega, weight = second_step_weight(stack, step, one.theta, center=center)
    if weight is None:
        cov = sandwich(step.zw, stack.first_weight.weight, omega, stack.n_rows)
        if cov is None:
            return None
        return ThresholdFit(
            gamma, one.theta, one.obj, cov, stack.first_weight.weight, False, one.theta, one.obj
        )
    two = second_step(stack, step, weight)
    if not two.ok:
        return None
    omega_2 = omega_of(stack, step.residual(stack, two.theta), center=center)
    cov = sandwich(step.zw, weight, omega_2, stack.n_rows)
    if cov is None:
        return None
    return ThresholdFit(gamma, two.theta, two.obj, cov, weight, True, one.theta, one.obj)
