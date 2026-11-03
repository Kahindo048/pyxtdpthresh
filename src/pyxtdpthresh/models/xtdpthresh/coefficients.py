"""Coefficient names and the slopes of the upper regime.

``e(b)`` holds two equations: ``lower`` (the slopes below the threshold) and ``change`` (the
intercept shift ``_cons`` and the slope shifts above it, or, in the kink model, the change in the
slope of ``q``).  The slopes of the **upper** regime are linear combinations ``lower + change`` of
those, with a variance obtained from the same combination (``e(b_upper)``, ``e(V_upper)``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._types import FloatArray

#: A name Stata accepts as a (time-series operated) variable.
_PLAIN = re.compile(r"^([A-Za-z][A-Za-z0-9]*\.)?[A-Za-z_][A-Za-z0-9_]*$")
#: Longest name of a coefficient.
MAX_NAME = 32


def _sanitize(label: str) -> str:
    """Make ``label`` a valid name: dots and slashes become underscores, parentheses go."""
    if _PLAIN.match(label):
        return label
    cleaned = label.replace(".", "_").replace("/", "_").replace("(", "").replace(")", "")
    return cleaned[:MAX_NAME]


def slope_names(labels: tuple[str, ...]) -> tuple[str, ...]:
    """Names of the slopes, made valid and unique within the equation."""
    # Stata: coefficient labels (xtdpthresh.ado:1571-1593)
    taken: list[str] = []
    for label in labels:
        name = _sanitize(label)
        candidate, counter = name, 1
        while candidate in taken:
            suffix = f"_{counter}"
            candidate = name.replace(".", "_")[: MAX_NAME - len(suffix)] + suffix
            counter += 1
        taken.append(candidate)
    return tuple(taken)


def coefficient_names(labels: tuple[str, ...], *, kink: bool, q: str) -> tuple[str, ...]:
    """Names ``lower:x``, then ``change:_cons`` and ``change:x`` (or ``change:q`` under kink)."""
    # Stata: cnames (xtdpthresh.ado:1594-1605)
    slopes = slope_names(labels)
    lower = tuple(f"lower:{name}" for name in slopes)
    if kink:
        return (*lower, f"change:{q}")
    return (*lower, "change:_cons", *(f"change:{name}" for name in slopes))


@dataclass(frozen=True)
class UpperRegime:
    """Slopes of the upper regime.

    Attributes
    ----------
    names
        ``upper:x`` for each slope.
    b, cov
        Estimates and their variance (``e(b_upper)``, ``e(V_upper)``).
    combination
        Matrix ``A`` with ``b_upper = A b`` (``e(b)`` as a column).
    """

    names: tuple[str, ...]
    b: FloatArray
    cov: FloatArray
    combination: FloatArray


def upper_regime(
    theta: FloatArray, cov: FloatArray, names: tuple[str, ...], *, kink: bool, q: str
) -> UpperRegime | None:
    """Slopes of the upper regime from ``e(b)`` and ``e(V)`` (``None`` when there are none).

    Jump model: ``lower + change`` for every slope (the intercept shift stays in
    ``change:_cons``).  Kink model: the slope of ``q`` above the threshold, ``lower:q +
    change:q``; when ``q`` is not a regressor there is no upper block.
    """
    # Stata: _xdpt_upper (xtdpthresh.ado:2257)
    k = theta.size
    lower = [i for i, name in enumerate(names) if name.startswith("lower:")]
    if not kink and not lower:
        return None
    upper: tuple[str, ...]
    if kink:
        position = [i for i in lower if names[i] == f"lower:{q}"]
        if not position:
            return None
        a = np.zeros((1, k))
        a[0, k - 1] = 1.0
        a[0, position[0]] = 1.0
        upper = (f"upper:{q}",)
    else:
        a = np.zeros((len(lower), k))
        for j in range(len(lower)):
            a[j, j] = 1.0
            a[j, len(lower) + 1 + j] = 1.0
        upper = tuple(names[j].replace("lower:", "upper:", 1) for j in lower)
    v = a @ cov @ a.T
    return UpperRegime(upper, a @ theta, (v + v.T) / 2, a)
