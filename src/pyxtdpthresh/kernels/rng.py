"""Mersenne Twister 64 (MT19937-64) of Matsumoto and Nishimura, as used by Stata's ``mt64``.

The state is an array of 313 ``uint64``: the 312 words of the generator followed by the index
of the next word.  Stata's ``set seed s`` initialises it with ``init_genrand64(s)``.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import UIntArray
from pyxtdpthresh.kernels._jit import njit

N_WORDS = 312
STATE_SIZE = N_WORDS + 1


@njit
def _init(seed: int, state: UIntArray) -> None:
    """``init_genrand64``: fill the 312 words from a 64-bit seed and reset the index."""
    mult = np.uint64(6364136223846793005)
    state[0] = np.uint64(seed)
    for i in range(1, 312):
        prev = state[i - 1]
        state[i] = mult * (prev ^ (prev >> np.uint64(62))) + np.uint64(i)
    state[312] = np.uint64(312)


@njit
def _twist(state: UIntArray) -> None:
    """Regenerate the 312 words (the "generate N words at one time" step of the reference)."""
    matrix_a = np.uint64(0xB5026F5AA96619E9)
    upper = np.uint64(0xFFFFFFFF80000000)
    lower = np.uint64(0x7FFFFFFF)
    one = np.uint64(1)
    zero = np.uint64(0)
    for i in range(312 - 156):
        x = (state[i] & upper) | (state[i + 1] & lower)
        state[i] = state[i + 156] ^ (x >> one) ^ (matrix_a if (x & one) != zero else zero)
    for i in range(312 - 156, 311):
        x = (state[i] & upper) | (state[i + 1] & lower)
        state[i] = state[i + 156 - 312] ^ (x >> one) ^ (matrix_a if (x & one) != zero else zero)
    x = (state[311] & upper) | (state[0] & lower)
    state[311] = state[155] ^ (x >> one) ^ (matrix_a if (x & one) != zero else zero)
    state[312] = zero


@njit
def _fill(state: UIntArray, out: UIntArray) -> None:
    """``genrand64_int64`` repeated: write ``out.size`` tempered 64-bit outputs."""
    for k in range(out.shape[0]):
        if state[312] >= np.uint64(312):
            _twist(state)
        x = state[int(state[312])]
        state[312] += np.uint64(1)
        x ^= (x >> np.uint64(29)) & np.uint64(0x5555555555555555)
        x ^= (x << np.uint64(17)) & np.uint64(0x71D67FFFEDA60000)
        x ^= (x << np.uint64(37)) & np.uint64(0xFFF7EEE000000000)
        x ^= x >> np.uint64(43)
        out[k] = x


def seed_state(seed: int) -> UIntArray:
    """State after Stata's ``set seed seed`` (``init_genrand64``)."""
    if not 0 <= seed < 2**64:
        raise ValueError("seed must be an unsigned 64-bit integer")
    state = np.zeros(STATE_SIZE, dtype=np.uint64)
    _init(seed, state)
    return state


def next_uint64(state: UIntArray, n: int) -> UIntArray:
    """Next ``n`` 64-bit outputs; ``state`` is advanced in place."""
    out = np.empty(n, dtype=np.uint64)
    _fill(state, out)
    return out
