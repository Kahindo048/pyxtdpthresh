"""Common settings of the Numba kernels.

Every kernel is compiled with the same options: on-disk cache (the compilation cost is paid
once per machine), explicit ``float64`` / ``int64`` types in the callers, no ``fastmath``
(four-decimal agreement with Stata matters more than the last few percent of speed) and
NumPy error semantics, so that a division by zero gives ``inf`` or ``nan`` as in Mata
instead of raising.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numba

from pyxtdpthresh._config import get_options, set_options

#: Decorator for a serial kernel.
njit: Callable[..., Any] = numba.njit(cache=True, nogil=True, fastmath=False, error_model="numpy")
#: Decorator for a kernel that uses ``prange`` over independent iterations.
pjit: Callable[..., Any] = numba.njit(
    cache=True, nogil=True, fastmath=False, error_model="numpy", parallel=True
)
prange = numba.prange


def apply_threads() -> int:
    """Apply the ``threads`` option to Numba and return the number of threads in use.

    ``threads=None`` uses every thread Numba offers; a larger request than Numba allows is capped.
    """
    available: int = numba.config.NUMBA_NUM_THREADS  # type: ignore[attr-defined]
    requested = get_options().threads
    numba.set_num_threads(available if requested is None else min(requested, available))
    return int(numba.get_num_threads())


def set_threads(n: int | None) -> int:
    """Set the number of threads used by the parallel kernels and return it.

    ``None`` restores the Numba default.  The value is stored in the package options, so it
    also applies to kernels called later.
    """
    set_options(threads=n)
    return apply_threads()
