"""Random numbers that reproduce Stata's ``set seed`` / ``uniform()`` / ``invnormal(uniform())``.

Stata 17 uses the 64-bit Mersenne Twister (``mt64``).  ``set seed s`` initialises it with
``init_genrand64(s)``; each draw takes one 64-bit output ``x`` and returns

    u = ((x >> 11) | 1) * 2**-53

(measured on 10 000 draws from five seeds: 100 % identical; the low bit is forced to 1, so a
draw is never exactly 0).  A matrix is filled row by row, and ``uniform()``, ``runiform()``
and ``invnormal(uniform())`` all consume the same stream.  Reproducing the stream lets a
Python bootstrap use the very draws of the Stata command for the same seed.
"""

from __future__ import annotations

import numpy as np
from scipy.special import ndtri

from pyxtdpthresh._types import FloatArray, UIntArray
from pyxtdpthresh.kernels import rng as mt64

#: Largest seed accepted by Stata's ``set seed``.
MAX_SEED = 2**31 - 1
_ONE = np.uint64(1)
_SHIFT = np.uint64(11)
_SCALE = 2.0**-53


def component_seed(rseed: int, offset: int) -> int:
    """Seed of one component of ``xtdpthresh`` under ``rseed()``: ``(rseed + offset) mod 2**31``."""
    # Stata: xdpt2_component_seed (xtdpthresh.ado:4796)
    return (int(rseed) + int(offset)) % 2**31


class StataRNG:
    """Stata-compatible generator.

    Parameters
    ----------
    seed
        The value given to ``set seed`` (0 to 2**31 - 1).

    Examples
    --------
    >>> rng = StataRNG(123)
    >>> round(float(rng.uniform()), 6)
    0.3132
    """

    def __init__(self, seed: int) -> None:
        self.reseed(seed)

    def reseed(self, seed: int) -> None:
        """Restart the stream as ``set seed seed`` does."""
        if not 0 <= int(seed) <= MAX_SEED:
            raise ValueError(f"seed must be an integer between 0 and {MAX_SEED}")
        self._state: UIntArray = mt64.seed_state(int(seed))

    def copy(self) -> StataRNG:
        """Independent generator at the same point of the stream."""
        clone = StataRNG.__new__(StataRNG)
        clone._state = self._state.copy()
        return clone

    def raw(self, n: int) -> UIntArray:
        """Next ``n`` 64-bit outputs of the generator."""
        return mt64.next_uint64(self._state, int(n))

    def uniform(self, size: int | tuple[int, ...] = ()) -> FloatArray:
        """Draws of Mata's ``uniform(r, c)`` in an array of shape ``size`` (row-major fill)."""
        shape = (size,) if isinstance(size, int) else tuple(size)
        count = int(np.prod(shape, dtype=np.int64)) if shape else 1
        bits = (self.raw(count) >> _SHIFT) | _ONE
        return np.asarray(bits.astype(np.float64) * _SCALE).reshape(shape)

    def normal(self, size: int | tuple[int, ...] = ()) -> FloatArray:
        """Draws of ``invnormal(uniform(r, c))``."""
        return np.asarray(ndtri(self.uniform(size)), dtype=np.float64)
