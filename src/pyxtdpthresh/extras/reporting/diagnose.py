"""Plain-language diagnostic report of an ``xtdpthresh`` fit (layer 6).

``diagnose(fit)`` reads what the fit already holds and lists what deserves attention: too many
instruments, Hansen and AR(2) tests, a threshold at the edge of the grid or weakly identified, thin
regimes, a panel that suits forward deviations better, a one-step estimate and the continuity
test.  Each alert carries its recommendation, in English or French.  The cut-offs below are
rules of thumb of the literature, not results of Stata; they are named so that they can be read.
"""

from __future__ import annotations

import html
import math
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting.profile import FLAT_GAP, flatness
from pyxtdpthresh.extras.plotting.style import resolve_lang
from pyxtdpthresh.extras.reporting.diagnose_texts import TEXTS
from pyxtdpthresh.models.xtdpthresh.variance import MIN_Q_VALUES

#: Instruments over units above which the count is a notice, and above 1 a warning (Roodman 2009).
IV_RATIO_NOTICE = 0.5
#: A Hansen p-value at or above this is read as a test too weak to detect anything.
HANSEN_NEAR_ONE = 0.95
#: Level of the Hansen and AR(2) tests.
TEST_LEVEL = 0.05
#: Level of the continuity test (a kink is kept when it is not rejected at this level).
CONTINUITY_LEVEL = 0.10
#: Share (percent) of the grid covered by the confidence set above which the threshold is weak.
WIDE_SHARE = 90.0
#: A confidence set narrower than this many steps of its candidate grid is read too coarsely.
#: Monte Carlo of a Seo-Shin design with an exogenous threshold (n = 200, 300 replications): a
#: grid step of the order of the estimation error cut the coverage of the hull from 0.93 (400
#: points) to 0.78 (100 points).  At 2 steps the rule flags 12 % of the replications, 54 % of them
#: miss the true threshold (22 % overall) and it finds 31 % of the misses: a sign to read, not a
#: detector (4 steps finds 60 % of the misses with 42 % of the flagged ones missing).
CI_COARSE_STEPS = 2.0
#: A regime is thin when it has fewer equations than this, a smaller share (percent), or fewer
#: units than this.
REGIME_MIN_OBS, REGIME_MIN_SHARE, REGIME_MIN_UNITS = 50, 10.0, 10
#: Distance (share of the grid span) beyond which a second minimum is a different threshold.
RIVAL_DISTANCE = 0.1

_DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")
WARNING, NOTICE = "warning", "notice"
_RAW = tuple[str, str, dict[str, Any]]


@dataclass(frozen=True)
class Alert:
    """One finding of the report.

    Attributes
    ----------
    code
        Stable identifier (``iv_more_than_units``, ``ar2_rejected``...).
    level
        ``"warning"`` (act on it) or ``"notice"`` (worth knowing).
    message, recommendation
        What was found and what to do, in the language of the report.
    """

    code: str
    level: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class Diagnosis:
    """The alerts of a fit, warnings first; prints as a report and displays in Jupyter."""

    alerts: tuple[Alert, ...]
    lang: Lang

    def __iter__(self) -> Iterator[Alert]:
        return iter(self.alerts)

    def __len__(self) -> int:
        return len(self.alerts)

    @property
    def codes(self) -> tuple[str, ...]:
        """Codes of the alerts, in report order."""
        return tuple(a.code for a in self.alerts)

    def to_dict(self) -> list[dict[str, str]]:
        """Return the alerts as plain dictionaries."""
        return [asdict(a) for a in self.alerts]

    def _counts(self) -> tuple[int, int]:
        warnings = sum(a.level == WARNING for a in self.alerts)
        return warnings, len(self.alerts) - warnings

    def __str__(self) -> str:
        if not self.alerts:
            return _text("none", self.lang) + "\n"
        warnings, notices = self._counts()
        lines = [_text("header", self.lang, warnings=warnings, notices=notices), ""]
        label = _text("recommendation", self.lang)
        for alert in self.alerts:
            lines += [
                f"[{_text(alert.level, self.lang)}] {alert.message}",
                f"    {label} {alert.recommendation}",
            ]
        return "\n".join(lines) + "\n"

    def _repr_html_(self) -> str:
        if not self.alerts:
            return f"<p>{html.escape(_text('none', self.lang))}</p>"
        warnings, notices = self._counts()
        items = "".join(
            f"<li><b>[{html.escape(_text(a.level, self.lang))}]</b> {html.escape(a.message)}<br>"
            f"<i>{html.escape(_text('recommendation', self.lang))}</i> "
            f"{html.escape(a.recommendation)}</li>"
            for a in self.alerts
        )
        title = _text("header", self.lang, warnings=warnings, notices=notices)
        return f"<p><b>{html.escape(title)}</b></p><ul>{items}</ul>"


def _text(code: str, lang: Lang, **fields: object) -> str:
    """Return the message of ``code`` in ``lang``."""
    return TEXTS[code][lang][0].format(**fields)


def _levers(fit: Any, lang: Lang) -> str:
    """Name the ways left to shrink the instrument set (``collapse``, ``maxlag``...)."""
    options = fit.spec.options
    keys = []
    if not options.collapse:
        keys.append("levers_collapse")
    if math.isinf(options.maxlag[1]):
        keys.append("levers_maxlag")
    keys = keys or ["levers_fewer"]
    joiner = " or " if lang == "en" else " ou "
    return joiner.join(_text(k, lang) for k in keys)


# ------------------------------------------------------------------------------- the checks
def _instruments(fit: Any) -> list[_RAW]:
    n_iv, n_units = fit.n_instruments, fit.n_units
    ratio = n_iv / max(n_units, 1)
    fields = {"n_iv": n_iv, "n_units": n_units, "ratio": ratio}
    if n_iv > n_units:
        return [("iv_more_than_units", WARNING, fields)]
    if ratio > IV_RATIO_NOTICE:
        return [("iv_high_ratio", NOTICE, fields)]
    return []


def _tests(fit: Any) -> list[_RAW]:
    out: list[_RAW] = []
    p = fit.hansen.p_value
    if math.isfinite(p) and p < TEST_LEVEL:
        out.append(("hansen_rejected", WARNING, {"p": p}))
    elif math.isfinite(p) and p >= HANSEN_NEAR_ONE:
        out.append(("hansen_near_one", NOTICE, {"p": p}))
    p2 = fit.serial.ar2.p_value
    if math.isfinite(p2) and p2 < TEST_LEVEL:
        out.append(("ar2_rejected", WARNING, {"p": p2}))
    return out


def _edge(fit: Any) -> list[_RAW]:
    """Threshold at an edge of the search grid."""
    search, gamma = fit.search, fit.search.fit.gamma
    low, high = search.admitted_lo, search.admitted_hi
    tol = 1e-12 * max(1.0, abs(high - low))
    side = "side_lower" if gamma <= low + tol else "side_upper" if gamma >= high - tol else ""
    if not side or high <= low:
        return []
    return [("gamma_at_edge", WARNING, {"gamma": gamma, "low": low, "high": high, "side": side})]


def _confidence_set(fit: Any) -> list[_RAW]:
    boot = fit.bootstrap
    ci = boot.ci if boot is not None else None
    if ci is None:
        return []
    out: list[_RAW] = []
    if ci.empty == 1:
        return [("ci_empty", WARNING, {})]
    if ci.n_unresolved > 0 or ci.incomplete == 1:
        out.append(("ci_incomplete", WARNING, {"n": ci.n_unresolved}))
    if ci.boundary_warn:
        side = {1: "side_lower", 2: "side_upper", 3: "side_both"}[ci.boundary_warn]
        out.append(("ci_boundary", NOTICE, {"side": side}))
    if ci.n_segments > 1:
        out.append(("ci_multiple", NOTICE, {"n": int(ci.n_segments)}))
    span = ci.grid_hi - ci.grid_lo
    if math.isfinite(ci.lo) and span > 0:
        share = 100.0 * (ci.hi - ci.lo) / span
        if share >= WIDE_SHARE:
            out.append(("ci_wide", NOTICE, {"share": share, "q": fit.spec.q}))
        out += _coarse_grid(ci)
    return out


def _coarse_grid(ci: Any) -> list[_RAW]:
    """Flag an accepted set of few grid steps: the true value may fall between two points."""
    steps = np.diff(np.sort(np.asarray(ci.grid, dtype=float)))
    steps = steps[steps > 0]
    if steps.size == 0:
        return []
    step = float(np.median(steps))
    width = float(ci.hi - ci.lo)
    if width >= CI_COARSE_STEPS * step:
        return []
    n_grid = int(np.asarray(ci.grid).size)
    fields = {"width": width, "steps": width / step, "n_grid": n_grid, "suggested": 4 * n_grid}
    return [("ci_grid_coarse", WARNING, fields)]


def _profile(fit: Any) -> list[_RAW]:
    """Flat profile, or a rival threshold that fits almost as well."""
    gammas, values = fit.search.profile()
    share, flat = flatness(values)
    if flat:
        return [("profile_flat", NOTICE, {"share": 100.0 * share, "gap": FLAT_GAP})]
    rival = _rival(gammas, values, fit.search.fit.gamma)
    if rival is None:
        return []
    return [
        ("grid_sensitive", NOTICE, {"other": rival, "gamma": fit.search.fit.gamma, "gap": FLAT_GAP})
    ]


def _rival(gammas: np.ndarray, values: np.ndarray, gamma: float) -> float | None:
    """Return the best distant local minimum within the gap of the global one, if any."""
    ok = np.isfinite(values)
    if ok.sum() < 3:
        return None
    order = np.argsort(gammas[ok])
    g, v = gammas[ok][order], values[ok][order]
    low = v.min()
    local = np.r_[False, (v[1:-1] <= v[:-2]) & (v[1:-1] <= v[2:]), False]
    far = np.abs(g - gamma) > RIVAL_DISTANCE * (g.max() - g.min())
    near = v <= low + FLAT_GAP
    candidates = np.flatnonzero(local & far & near)
    return float(g[candidates[np.argmin(v[candidates])]]) if candidates.size else None


def _regimes(fit: Any) -> list[_RAW]:
    from pyxtdpthresh.extras.plotting._data import upper_regime_flag

    out: list[_RAW] = []
    upper, finite = upper_regime_flag(fit)
    total = int(finite.sum())
    for regime, mask in (("regime_lower", finite & ~upper), ("regime_upper", upper)):
        n_obs = int(mask.sum())
        n_units = int(np.unique(fit.stack.unit[mask]).size)
        share = 100.0 * n_obs / total if total else 0.0
        if n_obs < REGIME_MIN_OBS or share < REGIME_MIN_SHARE or n_units < REGIME_MIN_UNITS:
            out.append(
                (
                    "regime_small",
                    WARNING,
                    {"regime": regime, "n_obs": n_obs, "share": share, "n_units": n_units},
                )
            )
    n_values = int(fit.stack.q_values.size)
    if n_values < MIN_Q_VALUES:
        out.append(("q_few_values", WARNING, {"q": fit.spec.q, "n": n_values}))
    return out


def _method(fit: Any) -> list[_RAW]:
    out: list[_RAW] = []
    rows = np.diff(fit.data.offsets)
    if fit.spec.options.method == "fd" and rows.size and rows.min() != rows.max():
        out.append(("fd_unbalanced", NOTICE, {}))
    if not fit.search.fit.twostep:
        out.append(("one_step", WARNING, {}))
    fallback = fit.stack.first_weight.fallback
    if fallback:
        out.append(("weight_fallback", NOTICE, {"fallback": f"fallback_{fallback}"}))
    return out


def _continuity(fit: Any) -> list[_RAW]:
    boot = fit.bootstrap
    test = boot.continuity if boot is not None else None
    if test is None or not math.isfinite(test.p_value) or fit.stack.kink:
        return []
    if test.p_value >= CONTINUITY_LEVEL:
        return [("continuity_kink", NOTICE, {"p": test.p_value})]
    return [("continuity_jump", NOTICE, {"p": test.p_value})]


_CHECKS = (_instruments, _tests, _edge, _confidence_set, _profile, _regimes, _method, _continuity)


def _alert(raw: _RAW, fit: Any, lang: Lang) -> Alert:
    """Turn a finding into an alert with its texts."""
    code, level, fields = raw
    fields = dict(fields, levers=_levers(fit, lang), q=fields.get("q", fit.spec.q))
    for key in ("side", "regime", "fallback"):
        if key in fields:
            fields[key] = _text(fields[key], lang)
    message, recommendation = (t.format(**fields) for t in TEXTS[code][lang])
    if lang == "fr":
        message, recommendation = (_DECIMAL.sub(",", t) for t in (message, recommendation))
    return Alert(code, level, message, recommendation)


def diagnose(fit: Any, lang: Lang | None = None) -> Diagnosis:
    """Return the diagnostic report of an ``xtdpthresh`` fit.

    Parameters
    ----------
    fit
        Result of an ``xtdpthresh`` estimation.
    lang : {"en", "fr"}, optional
        Language of the report (default: the global ``lang`` option).

    Returns
    -------
    Diagnosis
        The alerts, warnings first; ``print(diagnosis)`` shows the report.
    """
    chosen = resolve_lang(lang)
    raws = [raw for check in _CHECKS for raw in check(fit)]
    raws.sort(key=lambda raw: raw[1] != WARNING)
    return Diagnosis(tuple(_alert(raw, fit, chosen) for raw in raws), chosen)
