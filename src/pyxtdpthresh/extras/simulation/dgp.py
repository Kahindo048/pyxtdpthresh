"""Data generating processes of the dynamic panel threshold model (layer 6).

``simulate_panel(design, n, t, seed=...)`` draws a panel from a named design and returns it in
long form, ready for the estimators.  The designs reproduce those of the two papers the package
follows.

Gong and Seo (2026), section 5 and appendix C.3
    ``y = b_y y(-1) + b_x q + (d0 + d_y y(-1) + d_x q) 1{q > g} + s e`` with ``q = rho q(-1) + u``.
    ``gong_seo``: ``corr(e_t, u_{t+1}) = rho_eu``, the threshold variable is **weakly exogenous**
    (predetermined).  ``gong_seo_endog``: ``corr(e_t, u_t) = rho_eu``, **weakly endogenous**
    (``q(-1)`` is no longer a valid instrument).  ``linear``: the same model without threshold
    effect, the design of the **size** of the linearity test.
Seo and Shin (2016), section 6 and appendix A.4
    Self-exciting models, the threshold variable is ``y(-1)`` itself, without individual effect:
    ``seo_shin_jump`` is equation (16), the discontinuous model of Tong (1990)
    (``y = (0.7 - 0.5 y(-1)) 1{y(-1) <= 0} + (-1.8 + 0.7 y(-1)) 1{y(-1) > 0} + u``) and
    ``seo_shin_cont`` equation (17), the continuous model of Chan and Tsay (1998)
    (``y = (0.52 + 0.6 y(-1)) 1{y(-1) <= 0.8} + (1.48 - 0.6 y(-1)) 1{y(-1) > 0.8} + 0.5 u``).
    The ``*_common`` designs fix the intercept across the regimes (the second experiment of their
    section 6.1) and the ``seo_shin_exogenous*`` designs draw the threshold variable from
    ``U[-1, 1]``, independent of the errors (their appendix A.4).

The *jump* of a design is the jump of its regression function at the threshold (``0`` for a
continuous model, a kink).  Any parameter, ``jump`` included, can be overridden by keyword:
``simulate_panel("gong_seo", jump=0.2)``.

Everything the generator draws is a function of ``seed`` alone, whatever ``unbalanced`` is: the
random gaps are drawn last, so a balanced panel and its unbalanced version share their values.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields, replace
from typing import Any, Literal

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray

Timing = Literal["weak", "same"]
ThresholdKind = Literal["ar", "lag_y", "uniform"]
Regressor = Literal["q", "none"]

#: Range of the threshold variable of the ``uniform`` designs (appendix A.4 of Seo and Shin).
UNIFORM_RANGE = (-1.0, 1.0)


@dataclass(frozen=True)
class Design:
    """Parameters of a data generating process and how to estimate it.

    The regression function is ``beta0 + beta_y y(-1) + beta_x q`` below the threshold and the
    same plus ``delta0 + delta_y y(-1) + delta_x q`` above it (``q`` enters only when
    ``regressor == "q"``).

    Attributes
    ----------
    name
        Name of the design.
    beta0, beta_y, beta_x
        Lower-regime intercept and slopes of ``y(-1)`` and of ``q``.  With first differences the
        intercept is not identified.
    delta0, delta_y, delta_x
        Changes of the intercept and of the two slopes above the threshold.
    gamma
        True threshold (``nan`` when the design has no threshold effect).
    sigma
        Standard deviation of the error.
    threshold_kind
        How the threshold variable ``q`` is drawn: ``"ar"`` an autoregression (Gong-Seo),
        ``"lag_y"`` the lagged outcome (Seo-Shin, ``q_t = y_{t-1}``), ``"uniform"`` independent
        draws from ``U[-1, 1]``.
    rho, u_sd
        Autoregression of ``q`` and standard deviation of its innovation (``"ar"`` only).
    rho_eu, timing
        Correlation between the error and the innovation of ``q`` (``"ar"`` only): with
        ``"weak"`` it is ``corr(e_t, u_{t+1})`` (``q`` predetermined), with ``"same"`` it is
        ``corr(e_t, u_t)``.
    regressor
        ``"q"``: the threshold variable is also a regressor (Gong-Seo); ``"none"``: only ``y(-1)``.
    roles
        How the regressor enters the estimation: ``{"predetermined": ("q",)}``...
    """

    name: str
    beta0: float = 0.0
    beta_y: float = 0.6
    beta_x: float = 1.0
    delta0: float = -0.3
    delta_y: float = 0.0
    delta_x: float = 2.0
    gamma: float = 0.25
    sigma: float = 0.5
    threshold_kind: ThresholdKind = "ar"
    rho: float = 0.7
    u_sd: float = 1.0
    rho_eu: float = 0.5
    timing: Timing = "weak"
    regressor: Regressor = "q"
    roles: dict[str, tuple[str, ...]] = field(default_factory=dict)

    @property
    def x_name(self) -> str | None:
        """Name of the column of the regressor (``None`` when ``y(-1)`` is the only one)."""
        return "q" if self.regressor == "q" else None

    @property
    def _slope_at_threshold(self) -> float:
        """What the changed slopes add to the regression function at the threshold."""
        if self.regressor == "q":
            return self.delta_x * self.gamma
        if self.threshold_kind == "lag_y":
            return self.delta_y * self.gamma
        return 0.0

    @property
    def jump(self) -> float:
        """Jump of the regression function at the threshold (``0``: a continuous model, a kink)."""
        return self.delta0 + self._slope_at_threshold

    @property
    def has_threshold(self) -> bool:
        """Whether the design has a threshold effect at all."""
        return not (self.delta0 == 0.0 and self.delta_y == 0.0 and self.delta_x == 0.0)

    @property
    def truth(self) -> dict[str, float]:
        """True values keyed like the coefficients of the fits (plus ``gamma``).

        ``lower:*`` are the lower-regime slopes, ``change:*`` the changes (``change:_cons`` is the
        intercept change) and ``upper:*`` their sums.
        """
        values = {
            "lower:L.y": self.beta_y,
            "change:_cons": self.delta0,
            "change:L.y": self.delta_y,
            "upper:L.y": self.beta_y + self.delta_y,
        }
        if self.x_name is not None:
            values |= {
                f"lower:{self.x_name}": self.beta_x,
                f"change:{self.x_name}": self.delta_x,
                f"upper:{self.x_name}": self.beta_x + self.delta_x,
            }
        values["gamma"] = self.gamma if self.has_threshold else math.nan
        return values

    def with_jump(self, jump: float) -> Design:
        """Copy of the design whose jump at the threshold is ``jump`` (``0``: a kink)."""
        return replace(self, delta0=jump - self._slope_at_threshold)

    def arguments(self) -> dict[str, Any]:
        """Arguments of the estimators that describe this design (``q``, roles, ``collapse``).

        The instruments of the papers are not collapsed.
        """
        return {"q": "q", "collapse": False, **self.roles}


def _design_table() -> dict[str, Design]:
    gong_seo = Design("gong_seo", roles={"predetermined": ("q",)})
    self_exciting: dict[str, Any] = {
        "threshold_kind": "lag_y",
        "regressor": "none",
        "beta_x": 0.0,
        "delta_x": 0.0,
    }
    jump = Design(
        "seo_shin_jump", beta0=0.7, beta_y=-0.5, delta0=-2.5, delta_y=1.2, gamma=0.0, sigma=1.0,
        **self_exciting,
    )  # fmt: skip
    cont = Design(
        "seo_shin_cont", beta0=0.52, beta_y=0.6, delta0=0.96, delta_y=-1.2, gamma=0.8, sigma=0.5,
        **self_exciting,
    )  # fmt: skip
    uniform: dict[str, Any] = {"threshold_kind": "uniform", "gamma": 0.0}
    table = [
        gong_seo,
        replace(gong_seo, name="gong_seo_endog", timing="same", roles={"endogenous": ("q",)}),
        replace(gong_seo, name="linear", delta0=0.0, delta_y=0.0, delta_x=0.0),
        jump,
        cont,
        replace(jump, name="seo_shin_jump_common", delta0=0.0, gamma=1.5),
        replace(cont, name="seo_shin_cont_common", delta0=0.0, gamma=0.4),
        replace(jump, name="seo_shin_exogenous", **uniform),
        replace(jump, name="seo_shin_exogenous_common", delta0=0.0, **uniform),
    ]
    return {design.name: design for design in table}


#: The named designs.
DESIGNS: dict[str, Design] = _design_table()
_PARAMETERS = tuple(f.name for f in fields(Design) if f.name not in ("name", "roles"))


def resolve_design(design: str | Design = "gong_seo", **changes: Any) -> Design:
    """Return the design named ``design`` with the parameters in ``changes`` replaced.

    ``jump=`` is accepted as a parameter: it sets ``delta0`` so that the regression function jumps
    by that much at the threshold (the ``delta_1 + delta_3 gamma`` of Gong and Seo).
    """
    if isinstance(design, str):
        if design not in DESIGNS:
            raise SpecificationError(
                message("sim_unknown_design", name=design, options=", ".join(DESIGNS)),
                key="sim_unknown_design",
            )
        design = DESIGNS[design]
    jump = changes.pop("jump", None)
    unknown = [name for name in changes if name not in _PARAMETERS]
    if unknown:
        raise SpecificationError(
            message("sim_unknown_parameter", name=unknown[0], options=", ".join(_PARAMETERS)),
            key="sim_unknown_parameter",
        )
    resolved = replace(design, **changes)
    if not -1.0 < resolved.rho_eu < 1.0:
        raise SpecificationError(
            message("sim_bad_correlation", value=resolved.rho_eu), key="sim_bad_correlation"
        )
    return resolved if jump is None else resolved.with_jump(float(jump))


def _check_sizes(n: int, t: int, burn: int, unbalanced: float, min_obs: int) -> None:
    sizes = (("n", n, 2), ("t", t, 2), ("burn", burn, 0), ("min_obs", min_obs, 1))
    for name, value, minimum in sizes:
        if int(value) != value or value < minimum:
            raise SpecificationError(
                message("sim_bad_size", name=name, minimum=minimum, value=value),
                key="sim_bad_size",
            )
    if not 0.0 <= unbalanced < 1.0:
        raise SpecificationError(message("sim_bad_share", value=unbalanced), key="sim_bad_share")


def _autoregressive_threshold(
    spec: Design, rng: np.random.Generator, n: int, total: int
) -> tuple[FloatArray, FloatArray]:
    """Draw the errors ``e`` and the autoregressive ``q``; row ``s`` is the period ``s``.

    The innovation ``u[s]`` moves ``q`` from period ``s - 1`` to ``s``.  With the ``weak`` timing it
    is paired with ``e[s - 1]``; with ``same`` it is paired with ``e[s]``.  ``q`` starts from its
    stationary law.
    """
    e = rng.standard_normal((total + 1, n))
    z2 = rng.standard_normal((total + 1, n))
    paired = spec.rho_eu * e + math.sqrt(1.0 - spec.rho_eu**2) * z2
    u = np.zeros((total + 1, n))
    u[1:] = spec.u_sd * (paired[:-1] if spec.timing == "weak" else paired[1:])
    start = rng.standard_normal(n) * spec.u_sd / math.sqrt(1.0 - spec.rho**2)
    q = np.empty_like(u)
    q[0] = start
    for s in range(1, q.shape[0]):
        q[s] = spec.rho * q[s - 1] + u[s]
    return e, q


def _draw_errors_and_threshold(
    spec: Design, rng: np.random.Generator, n: int, total: int
) -> tuple[FloatArray, FloatArray | None]:
    """Errors and, unless it is the lagged outcome, the threshold variable."""
    if spec.threshold_kind == "ar":
        return _autoregressive_threshold(spec, rng, n, total)
    e = rng.standard_normal((total + 1, n))
    if spec.threshold_kind == "uniform":
        return e, rng.uniform(*UNIFORM_RANGE, size=(total + 1, n))
    return e, None


def _outcome(spec: Design, e: FloatArray, q: FloatArray | None) -> tuple[FloatArray, FloatArray]:
    """Simulate ``y`` period by period; the threshold variable is ``y(-1)`` when ``q`` is None."""
    y = np.zeros_like(e)
    threshold = np.zeros_like(e) if q is None else q
    active = spec.has_threshold
    for s in range(1, e.shape[0]):
        lagged = y[s - 1]
        if q is None:
            threshold[s] = lagged
        x = threshold[s] if spec.regressor == "q" else 0.0
        above = threshold[s] > spec.gamma if active else np.zeros(lagged.shape, dtype=bool)
        y[s] = (
            spec.beta0 + spec.beta_y * lagged + spec.beta_x * x
            + above * (spec.delta0 + spec.delta_y * lagged + spec.delta_x * x)
            + spec.sigma * e[s]
        )  # fmt: skip
    return y, threshold


def _unbalance(rng: np.random.Generator, n: int, t: int, share: float, min_obs: int) -> BoolArray:
    """Mask of the observations kept: random gaps, units under ``min_obs`` observations dropped."""
    keep: BoolArray = rng.random((n, t)) >= share
    keep &= (keep.sum(axis=1) >= min_obs)[:, None]
    return keep


def simulate_panel(
    design: str | Design = "gong_seo",
    n: int = 400,
    t: int = 6,
    *,
    seed: int | np.random.SeedSequence | None = None,
    burn: int = 50,
    unbalanced: float = 0.0,
    min_obs: int = 3,
    **changes: Any,
) -> pd.DataFrame:
    """Draw a panel of ``n`` units over ``t`` periods from a threshold design.

    Parameters
    ----------
    design
        A name of :data:`DESIGNS` or a :class:`Design`.
    n, t
        Number of units and of periods.
    seed
        Seed of the generator (an int or a ``SeedSequence``); the panel is a function of it.
    burn
        Periods simulated and discarded before the first observed one, so that ``q`` and ``y`` are
        close to their stationary behaviour.
    unbalanced
        Share of observations dropped at random (gaps in the panel).  The drop does not change the
        remaining values.  A unit left with fewer than ``min_obs`` observations is removed.
    **changes
        Parameters of the design to override, including ``jump``.

    Returns
    -------
    pandas.DataFrame
        Columns ``id``, ``t`` (1 to ``t``), ``y`` and ``q``.  When the threshold variable is the
        lagged outcome, ``q`` is ``y(-1)``, and ``q`` of the first period is the outcome of the
        period before it (unobserved otherwise).
    """
    spec = resolve_design(design, **changes)
    _check_sizes(n, t, burn, unbalanced, min_obs)
    rng = np.random.default_rng(seed)
    total = burn + t
    e, q = _draw_errors_and_threshold(spec, rng, n, total)
    y, q = _outcome(spec, e, q)
    keep = _unbalance(rng, n, t, unbalanced, min_obs) if unbalanced > 0.0 else None
    observed = slice(burn + 1, total + 1)
    frame = pd.DataFrame(
        {
            "id": np.repeat(np.arange(1, n + 1), t),
            "t": np.tile(np.arange(1, t + 1), n),
            "y": y[observed].T.ravel(),
            "q": q[observed].T.ravel(),
        }
    )
    return frame if keep is None else frame[keep.ravel()].reset_index(drop=True)
