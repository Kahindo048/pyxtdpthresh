"""Variances and diagnostics of ``xtdpthresh`` against the frozen Stata 17 run (block G).

For the jump and kink models, ``vce(robust|windmeijer)``, ``bwscale``, ``nocenter``, forward
deviations, time effects and unbalanced panels: ``e(V)``, ``e(V_cond)``, ``e(b_upper)``,
``e(V_upper)``, the joint-variance scalars, the Hansen test and the AR(1) and AR(2) tests with
their pieces, to four decimals.
"""

import json
import warnings

import numpy as np
import pytest
from validation.compare import ATOL, RTOL
from validation.estimation_cases import unpack
from validation.variance_cases import _NAMES, GOLDEN, SCALARS, frame
from validation.variance_cases import CASES as ALL_CASES

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN}
_FITS: dict[str, object] = {}


def close(got, want, what):
    """Equal within the tolerance of the project; missing values must be missing on both sides."""
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    assert got.shape == want.shape, f"{what}: shape {got.shape} != {want.shape}"
    both_nan = np.isnan(got) & np.isnan(want)
    diff = np.abs(got - want)
    ok = both_nan | (diff <= ATOL) | (diff <= RTOL * np.abs(want))
    assert ok.all(), f"{what}: got {got.ravel()[~ok][:4]}, want {want.ravel()[~ok][:4]}"


def estimate(name):
    """Fit of a case, once per session."""
    if name not in _FITS:
        case = CASES[name]
        args = case.full_args()
        y, q = args.pop("y"), args.pop("q")
        x = args.pop("x", ())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", PyxdpthreshWarning)
            _FITS[name] = fit_point(frame(case), y, x, q=q, id="firm", time="year", **args)
    return _FITS[name]


def empty(entry):
    return unpack(entry).size == 0


@pytest.mark.parametrize("name", list(CASES))
def test_variance_matches_stata(name):
    ref, fit = FROZEN[name], estimate(name)
    sc = ref["scalars"]
    var = fit.variance
    close(fit.search.fit.gamma, sc["gamma"], "e(gamma)")
    close(fit.search.fit.theta, unpack(ref["b"]).ravel(), "e(b)")
    close(var.cov, unpack(ref["v"]), "e(V)")
    if empty(ref["vcond"]):
        assert not var.joint
    else:
        close(var.cond, unpack(ref["vcond"]), "e(V_cond)")
    assert var.joint == bool(sc["joint_vce"])
    assert var.wind_applied == bool(sc["vce_applied"])
    close(var.same_threshold, sc["wind_same_threshold"], "e(wind_same_threshold)")
    close(var.bandwidth, sc["gamma_bw"], "e(gamma_bw)")
    close(var.q_nvals_bw, sc["q_nvals_bw"], "e(q_nvals_bw)")
    assert (fit.n_obs, fit.n_units) == (sc["n"], sc["n_units"])
    assert fit.n_switch == sc["n_switch"]


@pytest.mark.parametrize("name", list(CASES))
def test_upper_regime_matches_stata(name):
    ref, fit = FROZEN[name], estimate(name)
    upper = fit.upper
    if empty(ref["bup"]):
        assert upper is None
        return
    assert upper is not None
    close(upper.b, unpack(ref["bup"]).ravel(), "e(b_upper)")
    close(upper.cov, unpack(ref["vup"]), "e(V_upper)")


@pytest.mark.parametrize("name", list(CASES))
def test_hansen_matches_stata(name):
    sc, fit = FROZEN[name]["scalars"], estimate(name)
    close(fit.hansen.statistic, sc["hansen"], "e(hansen)")
    close(fit.hansen.df, sc["hansen_df"], "e(hansen_df)")
    close(fit.hansen.p_value, sc["hansen_p"], "e(hansen_p)")


@pytest.mark.parametrize("name", list(CASES))
def test_serial_correlation_matches_stata(name):
    sc, fit = FROZEN[name]["scalars"], estimate(name)
    serial = fit.serial
    assert serial.joint == bool(sc["ar_joint"])
    for k, test, cond in ((1, serial.ar1, serial.ar1_cond), (2, serial.ar2, serial.ar2_cond)):
        close(test.statistic, sc[f"ar{k}"], f"e(ar{k})")
        close(test.p_value, sc[f"ar{k}_p"], f"e(ar{k}_p)")
        close(cond.statistic, sc[f"ar{k}_cond"], f"e(ar{k}_cond)")
        close(test.b0, sc[f"ar{k}_b0"], f"e(ar{k}_b0)")
        close(test.t1, sc[f"ar{k}_T1"], f"e(ar{k}_T1)")
        close(test.tt, sc[f"ar{k}_TT"], f"e(ar{k}_TT)")


def test_every_case_was_frozen():
    assert set(CASES) == {c.name for c in ALL_CASES}


@pytest.mark.parametrize("name", list(CASES))
def test_stored_scalars_match_stata(name):
    sc, scalars = FROZEN[name]["scalars"], estimate(name).scalars
    for key in SCALARS:
        close(scalars[_NAMES.get(key, key)], sc[key], f"e({_NAMES.get(key, key)})")


#: ``colfullnames`` of e(b) and e(b_upper) printed by Stata 17 (``names_probe.do``).
STATA_NAMES = {
    "fd_jump": (
        "lower:L.invest lower:cashflow lower:tobin_q change:_cons change:L.invest "
        "change:cashflow change:tobin_q",
        "upper:L.invest upper:cashflow upper:tobin_q",
    ),
    "fd_predet": (
        "lower:L.invest lower:cashflow lower:tobin_q change:_cons change:L.invest "
        "change:cashflow change:tobin_q",
        "upper:L.invest upper:cashflow upper:tobin_q",
    ),
    "fd_jump_q_regressor": (
        "lower:L.invest lower:cashflow lower:debt lower:tobin_q change:_cons change:L.invest "
        "change:cashflow change:debt change:tobin_q",
        "upper:L.invest upper:cashflow upper:debt upper:tobin_q",
    ),
    "fd_kink_q_regressor": (
        "lower:L.invest lower:cashflow lower:debt lower:tobin_q change:debt",
        "upper:debt",
    ),
    "fd_static": (
        "lower:cashflow lower:L.tobin_q change:_cons change:cashflow change:L.tobin_q",
        "upper:cashflow upper:L.tobin_q",
    ),
    "fod_kink": ("lower:L.invest lower:cashflow lower:tobin_q change:debt", ""),
}


@pytest.mark.parametrize("name", list(STATA_NAMES))
def test_coefficient_names_match_stata(name):
    fit = estimate(name)
    names, upper = STATA_NAMES[name]
    assert " ".join(fit.names) == names
    assert (" ".join(fit.upper.names) if fit.upper is not None else "") == upper


def test_one_step_fallback_with_windmeijer_warns_that_the_correction_was_not_applied():
    case = CASES["fd_alternate_wind"]
    args = case.full_args()
    y, q, x = args.pop("y"), args.pop("q"), args.pop("x", ())
    with pytest.warns(PyxdpthreshWarning, match="Windmeijer correction could not be applied"):
        fit = fit_point(frame(case), y, x, q=q, id="firm", time="year", **args)
    assert not fit.search.fit.twostep and not fit.variance.wind_applied
    assert np.isnan(fit.hansen.statistic)  # no Hansen test without the efficient weight


def test_discrete_threshold_variable_warns_about_the_joint_variance():
    case = CASES["fd_discrete_q"]
    args = case.full_args()
    y, q, x = args.pop("y"), args.pop("q"), args.pop("x", ())
    with pytest.warns(PyxdpthreshWarning, match="distinct values"):
        fit_point(frame(case), y, x, q=q, id="firm", time="year", **args)
