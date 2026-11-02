"""Frozen result containers (layer 0): data only, no computation or formatting."""

from __future__ import annotations

from dataclasses import dataclass, fields

import numpy as np

from pyxtdpthresh._types import FloatArray


def _frozen(value: FloatArray) -> FloatArray:
    """Read-only copy, so a result cannot be changed by accident."""
    out = np.array(value, dtype=np.float64, copy=True)
    out.flags.writeable = False
    return out


@dataclass(frozen=True)
class XthenregFit:
    """Everything ``xthenreg`` stores in ``e()``, plus the grid and the test details.

    Attributes
    ----------
    coef
        ``e(b)``: linear coefficients, regime coefficients, then the threshold (last).
    cov
        ``e(V)``: covariance of ``coef``.
    ci
        ``e(CI)``: ``(p, 2)`` lower and upper 95 % limits.
    n_units
        ``e(N)``: units retained in the sample.
    n_periods
        ``e(T)``: periods of the panel.
    boots_p
        ``e(boots_p)``: bootstrap p-value of the linearity test, ``-1`` without bootstrap.
    grid_num, trim_rate, boot_reps
        ``e(grid)``, ``e(trim)`` and ``e(bs)``.
    gamma
        Threshold estimate (``coef[-1]``).
    grid, criterion
        Candidate thresholds and the step-2 GMM criterion at each of them.
    n_moments
        Number of moment conditions ``L``.
    sup_wald
        Sample sup-Wald statistic (NaN without bootstrap).
    boot_sup
        Supremum of each bootstrap replication, ``(B,)``.
    bandwidth
        Kernel bandwidth of the covariance (NaN for a kink).
    static, kink
        Model variants.
    """

    coef: FloatArray
    cov: FloatArray
    ci: FloatArray
    n_units: int
    n_periods: int
    boots_p: float
    grid_num: int
    trim_rate: float
    boot_reps: int
    gamma: float
    grid: FloatArray
    criterion: FloatArray
    n_moments: int
    sup_wald: float
    boot_sup: FloatArray
    bandwidth: float
    static: bool
    kink: bool

    def __post_init__(self) -> None:
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, np.ndarray):
                object.__setattr__(self, f.name, _frozen(value))
