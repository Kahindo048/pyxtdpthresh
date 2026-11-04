"""pyxtdpthresh : dynamic panel threshold models in Python.

Ports of Stata's ``xthenreg`` (Seo, Kim and Kim 2019) and ``xtdpthresh``
(Nguyen and Lai 2026), validated against Stata to four decimals.

The public API is what ``__all__`` lists; everything else is private.  The names are loaded
when first used, so that ``import pyxtdpthresh`` does not import Numba, pandas or matplotlib.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from pyxtdpthresh._version import __version__

#: Public name -> module that defines it.
_PUBLIC = {
    "xtdpthresh": "pyxtdpthresh.api.xtdpthresh",
    "xthenreg": "pyxtdpthresh.api.xthenreg",
    "XtdpthreshResult": "pyxtdpthresh.results.public",
    "XthenregResult": "pyxtdpthresh.results.public",
    "compare": "pyxtdpthresh.extras.reporting",
    "ThresholdStargazer": "pyxtdpthresh.extras.reporting",
    "robustness": "pyxtdpthresh.extras.robustness",
    "plot": "pyxtdpthresh.extras.plotting",
    "from_stata": "pyxtdpthresh.data.io",
    "load_dataset": "pyxtdpthresh.extras.datasets",
    "list_datasets": "pyxtdpthresh.extras.datasets",
    "monte_carlo": "pyxtdpthresh.extras.simulation",
    "simulate_panel": "pyxtdpthresh.extras.simulation",
    "warmup": "pyxtdpthresh.kernels.warmup",
    "set_options": "pyxtdpthresh._config",
    "option_context": "pyxtdpthresh._config",
    "PyxdpthreshError": "pyxtdpthresh._errors",
    "SpecificationError": "pyxtdpthresh._errors",
    "DataError": "pyxtdpthresh._errors",
    "NumericalError": "pyxtdpthresh._errors",
    "PyxdpthreshWarning": "pyxtdpthresh._errors",
}

__all__ = ["__version__", *_PUBLIC]

if TYPE_CHECKING:  # for type checkers only: the names are loaded on first use
    from pyxtdpthresh._config import option_context, set_options  # noqa: F401
    from pyxtdpthresh._errors import (  # noqa: F401
        DataError,
        NumericalError,
        PyxdpthreshError,
        PyxdpthreshWarning,
        SpecificationError,
    )
    from pyxtdpthresh.api.xtdpthresh import xtdpthresh  # noqa: F401
    from pyxtdpthresh.api.xthenreg import xthenreg  # noqa: F401
    from pyxtdpthresh.data.io import from_stata  # noqa: F401
    from pyxtdpthresh.extras.datasets import list_datasets, load_dataset  # noqa: F401
    from pyxtdpthresh.extras.plotting import plot  # noqa: F401
    from pyxtdpthresh.extras.reporting import ThresholdStargazer, compare  # noqa: F401
    from pyxtdpthresh.extras.robustness import robustness  # noqa: F401
    from pyxtdpthresh.extras.simulation import monte_carlo, simulate_panel  # noqa: F401
    from pyxtdpthresh.kernels.warmup import warmup  # noqa: F401
    from pyxtdpthresh.results.public import XtdpthreshResult, XthenregResult  # noqa: F401


def __getattr__(name: str) -> Any:
    """Load a public name on first use (PEP 562)."""
    if name not in _PUBLIC:
        raise AttributeError(f"module 'pyxtdpthresh' has no attribute {name!r}")
    value = getattr(importlib.import_module(_PUBLIC[name]), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted([*globals(), *_PUBLIC])
