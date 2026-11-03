"""Time effects (``td``): partialling the period dummies out of the transformed system.

With a common time effect in the model, the transformed time effect is a function of the period
only.  Frisch-Waugh-Lovell then removes it by projecting ``dy``, the regressors and the
instruments off the transformed period dummies:

* first differences: the transformed dummy of period ``t`` is the same for every unit, so the
  projection is **exact demeaning within the period**; a period observed for one unit only is
  demeaned to zero and its row is dropped;
* forward orthogonal deviations: the transformed dummy of an equation depends on the unit's
  future dates, so the dummies receive the same transform as the data
  (``+c`` at ``t``, ``-c / T_f`` at each later equation row) and the system is projected on them
  with a generalised inverse (the transformed dummies sum to zero).  A row the projection
  saturates (leverage 1) carries no moment information and is dropped.

Both projections are symmetric and idempotent, so ``(M Z)' dW = Z' M dW``: the moments of the
regime terms are formed from the projected instruments and the unprojected regressors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from scipy import sparse

from pyxtdpthresh._types import FloatArray, IntArray
from pyxtdpthresh.core.linalg import invsym

#: A row whose residual leverage is below this after the projection is saturated.
SATURATION = 1e-10


class Partialling(Protocol):
    """A projection off the transformed period dummies."""

    @property
    def keep(self) -> IntArray:
        """Rows the projection leaves in the system."""
        ...

    def apply(self, values: FloatArray) -> FloatArray:
        """Project ``values`` (all rows, one or several columns); dropped rows are not removed."""
        ...


@dataclass(frozen=True)
class CellDemean:
    """Demeaning within the period (first differences).

    Attributes
    ----------
    keep
        Rows whose period has at least two equations.
    """

    keep: IntArray
    _indicator: sparse.csr_matrix
    _counts: FloatArray

    def apply(self, values: FloatArray) -> FloatArray:
        """Subtract the period mean of every column."""
        means = (self._indicator.T @ values) / (
            self._counts if values.ndim == 1 else self._counts[:, None]
        )
        return np.asarray(values - self._indicator @ means)


def fd_time_effects(times: IntArray) -> CellDemean:
    """Period demeaning of the stacked first-difference equations."""
    # Stata: xdpt2_demean_bytime (xtdpthresh.ado:3142) and the singleton-cell drop (3637-3656)
    _, cell = np.unique(times, return_inverse=True)
    n = cell.size
    indicator = sparse.csr_matrix((np.ones(n), (np.arange(n), cell)))
    counts = np.asarray(indicator.sum(axis=0)).ravel()
    keep = np.flatnonzero(counts[cell] >= 2).astype(np.int64)
    return CellDemean(keep, indicator, counts)


@dataclass(frozen=True)
class TimeProjection:
    """Projection on the transformed period dummies (forward orthogonal deviations).

    Attributes
    ----------
    keep
        Rows that the projection does not saturate.
    """

    keep: IntArray
    _dummies: FloatArray
    _inverse: FloatArray

    def apply(self, values: FloatArray) -> FloatArray:
        """Residual of the projection of every column on the transformed dummies."""
        coefficients = self._inverse @ (self._dummies.T @ values)
        return np.asarray(values - self._dummies @ coefficients)


def fod_time_effects(
    transform: sparse.csr_matrix, level_rank: IntArray, n_periods: int
) -> TimeProjection:
    """Projection on the forward-deviation transform of the period dummies.

    Parameters
    ----------
    transform
        ``(n_equations, n_levels)`` sparse matrix of the triplets.
    level_rank
        Rank of the period of each level observation among the observed equation periods.
    n_periods
        Number of observed equation periods.
    """
    # Stata: xdpt2_stack_at_gamma, FOD branch (xtdpthresh.ado:3658-3743)
    onehot = sparse.csr_matrix(
        (np.ones(level_rank.size), (np.arange(level_rank.size), level_rank)),
        shape=(level_rank.size, n_periods),
    )
    dummies = np.asarray((transform @ onehot).todense())
    dummies = dummies[:, np.sum(np.abs(dummies), axis=0) > 0]
    inverse = invsym(dummies.T @ dummies) if dummies.shape[1] else np.zeros((0, 0))
    leverage = np.sum((dummies @ inverse) * dummies, axis=1)
    keep = np.flatnonzero((1.0 - leverage) > SATURATION).astype(np.int64)
    return TimeProjection(keep, dummies, inverse)
