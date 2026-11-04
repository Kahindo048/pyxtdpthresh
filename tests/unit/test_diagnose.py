"""Diagnostic report of a fit (block I.3): an alert fires when its condition holds, not else."""

import warnings
from dataclasses import replace

import numpy as np
import pytest
from test_search import simulate

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.core.weights import FirstStepWeight
from pyxtdpthresh.extras.reporting import diagnose
from pyxtdpthresh.extras.reporting.diagnose import (
    HANSEN_NEAR_ONE,
    IV_RATIO_NOTICE,
    Diagnosis,
)
from pyxtdpthresh.extras.reporting.diagnose_texts import TEXTS
from pyxtdpthresh.models.xtdpthresh.bootstrap import ContinuityTest
from pyxtdpthresh.models.xtdpthresh.diagnostics import HansenTest
from pyxtdpthresh.models.xtdpthresh.fit import fit_point
from pyxtdpthresh.models.xtdpthresh.search import SearchResult


def fit(df=None, regressors=("x",), **options):
    df = simulate(n=600, t=7, seed=4) if df is None else df
    options = {"collapse": True, "grid": 25, "grid_ci": 25, "seed": 3, "n_boot": 49, **options}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(df, "y", regressors, q="q", id="id", time="t", **options)


@pytest.fixture(scope="module")
def base():
    return fit()


def healthy(base):
    """The fit with the conditions that the base case happens to trigger removed."""
    return replace(base, hansen=HansenTest(5.0, 3.0, 0.4))


def with_search(base, **changes):
    return replace(base, search=replace(base.search, **changes))


def with_threshold(base, **changes):
    return with_search(base, fit=replace(base.search.fit, **changes))


def with_ci(base, **changes):
    boot = replace(base.bootstrap, ci=replace(base.bootstrap.ci, **changes))
    return replace(base, bootstrap=boot)


def codes(result, lang="en"):
    return diagnose(result, lang).codes


# ------------------------------------------------------------------------------ structure
def test_every_code_has_english_and_french_text_with_the_same_fields():
    import re

    fields = re.compile(r"\{(\w+)")
    for code, texts in TEXTS.items():
        assert set(texts) == {"en", "fr"}, code
        for position in (0, 1):
            en, fr = texts["en"][position], texts["fr"][position]
            assert set(fields.findall(en)) == set(fields.findall(fr)), (code, position)


def test_a_clean_fit_has_no_alert_and_says_so(monkeypatch):
    grid = np.linspace(0.1, 0.9, 41)
    monkeypatch.setattr(SearchResult, "profile", lambda self: (grid, 2000.0 * (grid - 0.5) ** 2))
    clean = fit(simulate(n=3000, t=7, seed=11), bootstrap=False)
    result = diagnose(clean)
    assert isinstance(result, Diagnosis)
    assert len(result) == 0 and "No alert" in str(result)
    assert "Aucune alerte" in str(diagnose(clean, "fr"))


def test_the_report_lists_warnings_first_and_each_alert_has_a_recommendation(base):
    broken = replace(with_threshold(base, twostep=False), hansen=HansenTest(40.0, 3.0, 0.0001))
    report = diagnose(broken)
    levels = [a.level for a in report]
    assert levels == sorted(levels, key=lambda lv: lv != "warning")
    assert all(a.message and a.recommendation for a in report)
    text = str(report)
    assert "Diagnostic report" in text and "Recommendation:" in text
    assert report.to_dict()[0]["code"] == report.codes[0]
    assert "<li>" in report._repr_html_()


def test_the_french_report_has_french_text_and_decimal_commas(base):
    broken = replace(base, hansen=HansenTest(40.0, 3.0, 0.0123))
    alert = next(a for a in diagnose(broken, "fr") if a.code == "hansen_rejected")
    assert "0,012" in alert.message and "rejette" in alert.message
    assert "Rapport de diagnostic" in str(diagnose(broken, "fr"))


# ------------------------------------------------------------------------------ instruments
def test_more_instruments_than_units_is_a_warning_with_the_levers_left(base):
    panel = simulate(n=25, t=12, seed=2)
    many = fit(panel, collapse=False, grid=15, bootstrap=False)
    assert many.n_instruments > many.n_units
    alert = next(a for a in diagnose(many) if a.code == "iv_more_than_units")
    assert alert.level == "warning"
    assert "collapse=True" in alert.recommendation and "maxlag" in alert.recommendation

    def advice(**options):
        spec = replace(many.spec, options=replace(many.spec.options, **options))
        result = replace(many, spec=spec)
        return next(a for a in diagnose(result) if a.code == "iv_more_than_units").recommendation

    narrower = advice(maxlag=(2, 3))
    assert "maxlag" not in narrower and "collapse=True" in narrower
    collapsed = advice(collapse=True)
    assert "collapse=True" not in collapsed and "maxlag" in collapsed
    nothing_left = advice(collapse=True, maxlag=(2, 3))
    assert "collapse=True" not in nothing_left and "maxlag" not in nothing_left
    assert "fewer" in nothing_left


def test_a_high_instrument_ratio_is_only_a_notice(base):
    result = fit(simulate(n=40, t=8, seed=2), collapse=False, grid=15, bootstrap=False)
    assert IV_RATIO_NOTICE < result.n_instruments / result.n_units < 1
    alert = next(a for a in diagnose(result) if a.code in ("iv_high_ratio", "iv_more_than_units"))
    assert (alert.code, alert.level) == ("iv_high_ratio", "notice")
    assert "iv_high_ratio" not in codes(base) and "iv_more_than_units" not in codes(base)


# ---------------------------------------------------------------------------------- tests
def test_hansen_near_one_and_rejected(base):
    assert "hansen_near_one" in codes(replace(base, hansen=HansenTest(0.1, 3.0, 0.99)))
    assert "hansen_near_one" in codes(replace(base, hansen=HansenTest(0.1, 3.0, HANSEN_NEAR_ONE)))
    assert "hansen_rejected" in codes(replace(base, hansen=HansenTest(30.0, 3.0, 0.01)))
    middle = diagnose(replace(base, hansen=HansenTest(3.0, 3.0, 0.4)))
    assert not {"hansen_near_one", "hansen_rejected"} & set(middle.codes)
    missing = diagnose(replace(base, hansen=HansenTest(np.nan, np.nan, np.nan)))
    assert not {"hansen_near_one", "hansen_rejected"} & set(missing.codes)


def test_ar2_rejected_suggests_deeper_instruments(base):
    bad = base.serial.ar2._replace(p_value=0.01)
    alert = next(
        a
        for a in diagnose(replace(base, serial=replace(base.serial, ar2=bad)))
        if a.code == "ar2_rejected"
    )
    assert alert.level == "warning" and "maxlag=(3, 8)" in alert.recommendation
    assert "ar2_rejected" not in codes(base)


# ----------------------------------------------------------------------------- threshold
def test_a_threshold_at_the_edge_of_the_grid_is_a_warning(base):
    low = with_threshold(base, gamma=base.search.admitted_lo)
    high = with_threshold(base, gamma=base.search.admitted_hi)
    for result, side in ((low, "lower"), (high, "upper")):
        alert = next(a for a in diagnose(result) if a.code == "gamma_at_edge")
        assert alert.level == "warning" and side in alert.message
    assert "gamma_at_edge" not in codes(
        with_threshold(base, gamma=float(np.median(base.search.grid)))
    )


def test_the_confidence_set_alerts(base):
    assert "ci_empty" in codes(with_ci(base, empty=1.0))
    assert "ci_empty" not in codes(with_ci(base, empty=0.0))
    stuck = diagnose(with_ci(base, n_unresolved=3))
    assert next(a for a in stuck if a.code == "ci_incomplete").message.startswith("3 candidate")
    lo, hi = base.bootstrap.ci.grid_lo, base.bootstrap.ci.grid_hi
    edge = with_ci(base, lo=lo, hi=0.5 * (lo + hi), n_segments=1.0, empty=0.0)
    assert "ci_boundary" in codes(edge)
    both = with_ci(base, lo=lo, hi=hi, n_segments=1.0, empty=0.0)
    assert {"ci_boundary", "ci_wide"} <= set(codes(both))
    assert "ci_multiple" in codes(with_ci(base, n_segments=3.0))
    narrow = with_ci(base, lo=lo + 0.4 * (hi - lo), hi=lo + 0.5 * (hi - lo), n_segments=1.0)
    assert not {"ci_wide", "ci_boundary", "ci_multiple"} & set(codes(narrow))


def test_a_confidence_set_of_a_couple_of_grid_steps_is_flagged_as_too_coarsely_read(base):
    grid = np.sort(base.bootstrap.ci.grid)
    step = float(np.median(np.diff(grid)))
    middle = float(grid[len(grid) // 2])

    def width(steps):
        return with_ci(base, lo=middle, hi=middle + steps * step, n_segments=1.0, empty=0.0)

    for steps in (0.0, 1.0, 1.9):  # one accepted point, then barely more
        assert "ci_grid_coarse" in codes(width(steps)), steps
    for steps in (2.0, 3.0):
        assert "ci_grid_coarse" not in codes(width(steps)), steps
    alert = next(a for a in diagnose(width(1.0)) if a.code == "ci_grid_coarse")
    assert alert.level == "warning" and "1.0 steps" in alert.message
    assert f"{len(grid)} points" in alert.message
    assert f"grid_ci (for example to {4 * len(grid)})" in alert.recommendation
    french = next(a for a in diagnose(width(1.0), "fr") if a.code == "ci_grid_coarse")
    assert "1,0 pas" in french.message and "Augmenter grid_ci" in french.recommendation


def test_no_coarse_grid_alert_without_a_complete_confidence_set(base):
    assert "ci_grid_coarse" not in codes(with_ci(base, lo=np.nan, hi=np.nan, n_segments=np.nan))
    assert "ci_grid_coarse" not in codes(with_ci(base, empty=1.0))


def test_the_coarse_grid_alert_never_fires_on_a_fit_without_bootstrap():
    plain = fit(bootstrap=False)
    assert "ci_grid_coarse" not in codes(plain)


def test_a_flat_profile_and_a_rival_threshold(base, monkeypatch):
    grid = np.linspace(0.1, 0.9, 41)
    sharp = 50.0 * (grid - 0.5) ** 2 * 40
    monkeypatch.setattr(SearchResult, "profile", lambda self: (grid, sharp))
    result = with_threshold(base, gamma=0.5)
    assert not {"profile_flat", "grid_sensitive"} & set(codes(result))

    monkeypatch.setattr(SearchResult, "profile", lambda self: (grid, sharp * 0.001))
    assert "profile_flat" in codes(result)

    two_basins = 2000.0 * np.minimum((grid - 0.3) ** 2, (grid - 0.8) ** 2 + 0.001)
    monkeypatch.setattr(SearchResult, "profile", lambda self: (grid, two_basins))
    rival = next(a for a in diagnose(with_threshold(base, gamma=0.3)) if a.code == "grid_sensitive")
    assert "0.8" in rival.message
    assert "profile_flat" not in codes(with_threshold(base, gamma=0.3))


# -------------------------------------------------------------------------------- regimes
def test_a_thin_regime_is_a_warning_with_its_counts(base):
    top = float(np.max(base.stack.level_q))
    thin = with_threshold(base, gamma=top - 1e-9)
    alert = next(a for a in diagnose(thin) if a.code == "regime_small")
    assert alert.level == "warning" and "upper" in alert.message
    assert "regime_small" not in codes(base)


def test_few_distinct_values_of_the_threshold_variable_are_flagged():
    df = simulate(n=600, t=7, seed=4, q_values=np.array([0.2, 0.4, 0.6, 0.8]))
    result = fit(df, bootstrap=False)
    alert = next(a for a in diagnose(result) if a.code == "q_few_values")
    assert "4 distinct values" in alert.message


# ---------------------------------------------------------------------------------- method
def test_an_unbalanced_panel_in_first_differences_suggests_forward_deviations():
    df = simulate(n=600, t=7, seed=4)
    holes = df[~((df["id"] % 3 == 0) & (df["t"] == 3))]
    assert "fd_unbalanced" in codes(fit(holes, bootstrap=False))
    assert "fd_unbalanced" not in codes(fit(holes, bootstrap=False, method="fod"))
    assert "fd_unbalanced" not in codes(fit(df, bootstrap=False))


def test_a_one_step_estimate_and_a_weight_fallback_are_reported(base):
    assert "one_step" in codes(with_threshold(base, twostep=False))
    assert "one_step" not in codes(base)
    stack = replace(base.stack, first_weight=FirstStepWeight(base.stack.first_weight.weight, 2))
    alert = next(a for a in diagnose(replace(base, stack=stack)) if a.code == "weight_fallback")
    assert "identity" in alert.message
    stack1 = replace(base.stack, first_weight=FirstStepWeight(base.stack.first_weight.weight, 1))
    assert (
        "(Z'Z)^-1"
        in next(
            a for a in diagnose(replace(base, stack=stack1)) if a.code == "weight_fallback"
        ).message
    )


# --------------------------------------------------------------------------- continuity
def test_the_continuity_test_recommends_a_kink_or_keeps_the_jump(base):
    def with_continuity(p):
        test = ContinuityTest(p, 1.0, 49, 20)
        return replace(base, bootstrap=replace(base.bootstrap, continuity=test))

    keep = next(a for a in diagnose(with_continuity(0.4)) if a.code == "continuity_kink")
    assert "kink=True" in keep.recommendation
    assert "continuity_jump" in codes(with_continuity(0.03))
    assert not {"continuity_kink", "continuity_jump"} & set(codes(with_continuity(np.nan)))
    assert not {"continuity_kink", "continuity_jump"} & set(codes(base))


def test_diagnosing_does_not_change_the_fit(base):
    before = base.search.fit.theta.copy()
    diagnose(base)
    np.testing.assert_array_equal(base.search.fit.theta, before)
