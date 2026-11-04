"""Global options of the package (layer 0).

The only module holding global state.  Options are read when a function runs, never at
import time.  Numba-specific effects (thread count, jit switch) are applied by the
``kernels`` layer from these values.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import Any

from ._types import Lang


@dataclass(frozen=True)
class Options:
    """Immutable set of global options.

    Attributes
    ----------
    lang : {"en", "fr"}
        Language of messages and diagnostic reports.
    threads : int or None
        Threads of the matrix products (BLAS); ``None`` uses half of the logical cores.  The
        Numba kernels run on one thread, which is faster than letting them compete with BLAS.
    progress : bool
        Show a progress indicator during long bootstraps.
    """

    lang: Lang = "en"
    threads: int | None = None
    progress: bool = False


_options = Options()


def get_options() -> Options:
    """Return the current global options."""
    return _options


def set_options(**changes: Any) -> Options:
    """Change global options and return the previous ones.

    Raises
    ------
    ValueError
        If an option name or value is invalid.
    """
    global _options
    previous = _options
    unknown = set(changes) - set(Options.__dataclass_fields__)
    if unknown:
        raise ValueError(f"Unknown option(s): {sorted(unknown)}")
    candidate = replace(previous, **changes)
    if candidate.lang not in ("en", "fr"):
        raise ValueError("lang must be 'en' or 'fr'")
    if candidate.threads is not None and candidate.threads < 1:
        raise ValueError("threads must be a positive integer or None")
    _options = candidate
    return previous


@contextmanager
def option_context(**changes: Any) -> Iterator[Options]:
    """Temporarily change options inside a ``with`` block."""
    previous = set_options(**changes)
    try:
        yield get_options()
    finally:
        set_options(**{name: getattr(previous, name) for name in Options.__dataclass_fields__})
