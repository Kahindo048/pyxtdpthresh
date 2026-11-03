"""Weight matrices of the two GMM steps of ``xthenreg``."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.gmm import moment_covariance
from pyxtdpthresh.core.linalg import invsym, syminv


def ma1_weight(blocks: Sequence[FloatArray]) -> FloatArray:
    """First-step weight matrix for first-differenced errors, ``(2 W2 - W1 - W1')^{-1}``.

    The errors of consecutive equations of a unit overlap in one term (MA(1)).  With
    ``Z_p`` the ``(N, m_p)`` instruments of equation ``p``, the matrix is block tridiagonal:
    ``(1/N) Z_p' Z_p`` on the diagonal, ``-(1/N) Z_{p-1}' Z_p`` above it (and its transpose
    below), and the diagonal blocks are counted twice.  The result is
    ``invsym(W1 + W1' + 2 W2)``.

    Parameters
    ----------
    blocks
        Instruments of each equation, in time order, each ``(N, m_p)``.
    """
    # Stata: GMM_W_n_con (xthenreg.ado:1110) and GMM_W_n_static (1349)
    sizes = [b.shape[1] for b in blocks]
    n_units = blocks[0].shape[0]
    starts = np.concatenate([[0], np.cumsum(sizes)])
    total = int(starts[-1])
    off_diag = np.zeros((total, total))
    diag = np.zeros((total, total))
    for p, block in enumerate(blocks):
        here = slice(starts[p], starts[p + 1])
        diag[here, here] = block.T @ block / n_units
        if p > 0:
            before = slice(starts[p - 1], starts[p])
            off_diag[before, here] = -(blocks[p - 1].T @ block) / n_units
    return invsym(off_diag + off_diag.T + 2.0 * diag)


def second_step_weight(g: FloatArray) -> FloatArray:
    """Second-step weight matrix, the inverse of the centred covariance of the unit moments.

    Parameters
    ----------
    g
        Moments of each unit ``(N, L)`` evaluated at the first-step estimate.
    """
    # Stata: GMM_W_n_2_con (xthenreg.ado:1293)
    return invsym(moment_covariance(g, center=True))


class FirstStepWeight(NamedTuple):
    """First-step weight of the stacked first-difference system.

    Attributes
    ----------
    weight
        ``(L, L)`` matrix.
    fallback
        0: the MA(1) weight; 1: ``(Z'Z)^{-1}`` was substituted; 2: the identity was substituted
        (``e(W1_fallback)``).
    """

    weight: FloatArray
    fallback: int


def stacked_ma1_weight(second_moment: FloatArray, lag_cross: FloatArray) -> FirstStepWeight:
    """MA(1) first-step weight with the fallbacks ``(Z'Z)^{-1}`` then the identity.

    Parameters
    ----------
    second_moment
        ``W2 = Z'Z / n_u`` where ``n_u`` is the number of units.
    lag_cross
        ``W1 = (1/n_u) sum z_{t-1}' z_t`` over consecutive equations of the same unit.
    """
    # Stata: xdpt2_build_W_ma1 (xtdpthresh.ado:3808)
    ma1 = syminv(2.0 * second_moment - lag_cross - lag_cross.T)
    if ma1.ok:
        return FirstStepWeight(ma1.inv, 0)
    plain = syminv(second_moment)
    if plain.ok:
        return FirstStepWeight(plain.inv, 1)
    return FirstStepWeight(np.eye(second_moment.shape[0]), 2)
