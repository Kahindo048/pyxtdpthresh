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

    Parameters
    ----------
    **changes
        Any of the fields of :class:`Options`: ``lang`` (``"en"`` or ``"fr"``), ``threads`` (a
        positive integer, or ``None`` for half of the logical cores) and ``progress``.

    Returns
    -------
    Options
        The options before the change, to restore them later.

    Raises
    ------
    ValueError
        If an option name or value is invalid.

    Examples
    --------
    >>> import pyxtdpthresh as pyx
    >>> previous = pyx.set_options(lang="fr")
    >>> previous.lang
    'en'
    >>> _ = pyx.set_options(lang=previous.lang)
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
    """Temporarily change options inside a ``with`` block.

    Parameters
    ----------
    **changes
        Options to set, as in :func:`set_options`; the previous ones are restored on exit, even
        after an exception.

    Yields
    ------
    Options
        The options in force inside the block.

    Examples
    --------
    >>> import pyxtdpthresh as pyx
    >>> with pyx.option_context(lang="fr") as options:
    ...     options.lang
    'fr'
    """
    previous = set_options(**changes)
    try:
        yield get_options()
    finally:
        set_options(**{name: getattr(previous, name) for name in Options.__dataclass_fields__})
