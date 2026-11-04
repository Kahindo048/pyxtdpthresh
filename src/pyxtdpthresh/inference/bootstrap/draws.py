"""Mammen weights and the random streams of the bootstrap components.

The wild bootstrap multiplies the residuals of each unit by a two-point weight with mean 0 and
variance 1 (Mammen 1993): ``-phi`` with probability ``(sqrt5 + 1) / (2 sqrt5)`` and ``1 / phi``
otherwise, ``phi = (sqrt5 - 1) / 2``.  One uniform draw per unit and replication is consumed, the
replications one after the other, exactly as the Stata command does, so that a given seed gives
the same weights in both programs.

With a seed, every component of the command (confidence set, linearity test, continuity test,
coefficient bootstrap, ``citest``) restarts the generator at ``seed + offset``: the components
are decoupled, and asking for one test does not change another result.  Without a seed they
share one stream, in that order.
"""

from __future__ import annotations

import math

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.inference.bootstrap.rng import MAX_SEED, StataRNG, component_seed

#: Offsets added to ``rseed`` for each component of the command.
OFFSETS: dict[str, int] = {
    "threshold": 0,
    "linearity": 104729,
    "continuity": 224737,
    "coefficient": 350377,
    "citest": 477377,
}

_SQRT5 = math.sqrt(5.0)
_PHI = (_SQRT5 - 1.0) / 2.0
#: Probability of the negative point ``-phi``.
_P_LOW = (_SQRT5 + 1.0) / (2.0 * _SQRT5)


def mammen_weights(rng: StataRNG, n_units: int, n_draws: int) -> FloatArray:
    """Weights ``(n_units, n_draws)``; column ``b`` is drawn after column ``b - 1``."""
    # Stata: xdpt2_mammen_draw (xtdpthresh.ado:4783), filled column by column
    uniform = rng.uniform((n_draws, n_units))
    low = (uniform < _P_LOW).astype(np.float64)
    return np.asarray((-_PHI * low + (1.0 / _PHI) * (1.0 - low)).T)


class BootstrapStreams:
    """Generators of the bootstrap components.

    Parameters
    ----------
    seed
        ``rseed``: each component restarts at ``seed + offset``.  ``None`` draws one random seed
        and shares a single stream between the components, in the order they run.
    """

    def __init__(self, seed: int | None = None) -> None:
        self.seed = None if seed is None else int(seed)
        self._shared: StataRNG | None = None
        self._streams: dict[str, StataRNG] = {}
        if self.seed is None:
            self._shared = StataRNG(int(np.random.default_rng().integers(0, MAX_SEED + 1)))

    def stream(self, component: str) -> StataRNG:
        """Return the generator of ``component`` (``"threshold"``, ``"linearity"``, ...).

        With a seed the generator starts at ``seed + offset`` the first time it is requested and
        goes on from there, so successive candidates of a component take new draws.
        """
        # Stata: xdpt2_component_seed (xtdpthresh.ado:4796)
        if component not in OFFSETS:
            raise KeyError(f"unknown bootstrap component {component!r}")
        if self._shared is not None:
            return self._shared
        assert self.seed is not None
        if component not in self._streams:  # created once: later requests continue the stream
            self._streams[component] = StataRNG(component_seed(self.seed, OFFSETS[component]))
        return self._streams[component]

    def component_seed(self, component: str) -> int | None:
        """Seed the component starts from (``None`` without ``rseed``)."""
        if self.seed is None:
            return None
        return component_seed(self.seed, OFFSETS[component])
