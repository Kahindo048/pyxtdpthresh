"""Bootstraps against the frozen Stata 17 run (block H).

Stata runs with ``rseed()``; Python restarts its Mersenne Twister at the same component seeds, so
the Mammen weights are the very same.  The confidence set (bounds, inversion table, segments),
the linearity test and the other tests must agree to four decimals.
"""

import json
import warnings

import numpy as np
import pytest
from validation.bootstrap_cases import CASES as ALL_CASES
from validation.bootstrap_cases import GOLDEN, frame
from validation.compare import ATOL, RTOL
from validation.estimation_cases import unpack

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN and FROZEN[c.name]["rc"] == 0}
REFUSED = {c.name: c for c in ALL_CASES if c.name in FROZEN and FROZEN[c.name]["rc"] != 0}
_FITS: dict[str, object] = {}
REFUSAL_TEXT = {
    "cont_without_q": "contemporaneous regressor",
    "coef_twostep_td": "not available with td",
}


def close(got, want, what):
    """Equal within the tolerance of the project; missing values must be missing on both sides."""
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    assert got.shape == want.shape, f"{what}: shape {got.shape} != {want.shape}"
    both_nan = np.isnan(got) & np.isnan(want)
    diff = np.abs(got - want)
    ok = both_nan | (diff <= ATOL) | (diff <= RTOL * np.abs(want))
    if not ok.all():
        rows = np.unique(np.argwhere(~ok)[:, 0]) if ok.ndim > 1 else np.flatnonzero(~ok)
        raise AssertionError(f"{what}: rows {rows[:6]}, got {got[~ok][:4]}, want {want[~ok][:4]}")


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


@pytest.mark.parametrize("name", list(CASES))
def test_confidence_set_matches_stata(name):
    ref, fit = FROZEN[name], estimate(name)
    sc, ci = ref["scalars"], fit.bootstrap.ci
    assert ref["rc"] == 0, ref["text"]
    close(fit.search.fit.gamma, sc["gamma"], "e(gamma)")
    close(ci.table, unpack(ref["grid"]), "e(ci_grid)")
    for key, got in (
        ("gamma_lo", ci.lo), ("gamma_hi", ci.hi), ("ci_empty", ci.empty),
        ("ci_nseg", ci.n_segments), ("ci_incomplete", ci.incomplete),
        ("ci_unresolved", ci.n_unresolved), ("boundary_warn", ci.boundary_warn),
    ):  # fmt: skip
        close(got, sc[key], f"e({key})")
    segments = unpack(ref["segments"])
    if segments.size:
        close(ci.segments, segments, "e(ci_segments)")
    elif ci.n_unresolved == 0:
        assert ci.segments.size == 0


@pytest.mark.parametrize("name", list(CASES))
def test_linearity_test_matches_stata(name):
    sc, fit = FROZEN[name]["scalars"], estimate(name)
    test = fit.bootstrap.linearity
    if test is None:
        assert np.isnan(sc["pval_lin"])
        return
    close(test.p_value, sc["pval_lin"], "e(pval_lin)")
    close(test.n_valid, sc["boot_linearity_valid"], "boot_linearity_valid")


@pytest.mark.parametrize("name", list(CASES))
def test_continuity_and_citest_match_stata(name):
    sc, fit = FROZEN[name]["scalars"], estimate(name)
    boot = fit.bootstrap
    scalars = fit.scalars
    close(scalars["pval_cont"], sc["pval_cont"], "e(pval_cont)")
    close(scalars["boot_continuity_valid"], sc["boot_continuity_valid"], "continuity valid")
    for key in ("gamma", "D", "crit", "accept", "draws", "status", "p"):
        want = sc[f"citest_{key}"]
        got = scalars.get(f"citest_{key}", np.nan)
        close(got, want, f"e(citest_{key})")
    assert (boot.citest is not None) == (not np.isnan(sc["citest_gamma"]))


@pytest.mark.parametrize("name", list(CASES))
def test_coefficient_bootstrap_matches_stata(name):
    ref, fit = FROZEN[name], estimate(name)
    sc, coef = ref["scalars"], fit.bootstrap.coefficient
    want = unpack(ref["bootci"])
    if coef is None:
        assert np.isnan(sc["boot_coef_attempted"]) or sc["boot_coef_attempted"] == 0
        assert want.size == 0
        return
    if want.size:
        assert coef.interval is not None
        close(coef.interval, want, "e(b_bootci)")
    else:
        assert coef.interval is None
    scalars = fit.scalars
    for key in ("boot_coef_B", "boot_coef_attempted", "boot_coef_failed", "boot_coef_twostep",
                "boot_grid_stage1", "boot_grid_stage2"):  # fmt: skip
        close(scalars[key], sc[key], f"e({key})")


@pytest.mark.parametrize("name", list(CASES))
def test_stored_scalars_match_stata(name):
    sc, scalars = FROZEN[name]["scalars"], estimate(name).scalars
    for key in (
        "gamma_lo",
        "gamma_hi",
        "ci_empty",
        "ci_nseg",
        "ci_incomplete",
        "pval_lin",
        "rseed",
    ):
        close(scalars[key], sc[key], f"e({key})")


@pytest.mark.parametrize("name", list(REFUSED))
def test_refused_requests_match_stata(name):
    case, ref = REFUSED[name], FROZEN[name]
    args = case.full_args()
    y, q, x = args.pop("y"), args.pop("q"), args.pop("x", ())
    with pytest.raises(SpecificationError) as raised:
        fit_point(frame(case), y, x, q=q, id="firm", time="year", **args)
    assert raised.value.stata_code == ref["rc"] == 198
    assert REFUSAL_TEXT[name] in ref["text"]


def test_every_case_was_frozen():
    assert set(CASES) | set(REFUSED) == {c.name for c in ALL_CASES}
