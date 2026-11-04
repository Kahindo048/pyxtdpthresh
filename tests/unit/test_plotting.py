"""Graphs of a fit (block I.1): the figures read validated results and draw them faithfully."""

import math
import subprocess
import sys
import warnings

import matplotlib
import numpy as np
import pytest
from test_search import simulate

from pyxtdpthresh._config import option_context
from pyxtdpthresh._errors import DataError, PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.extras.plotting import FIT_KINDS, PLOT_KINDS, plot
from pyxtdpthresh.extras.plotting.coef import estimates_by_variable
from pyxtdpthresh.extras.plotting.instruments import instruments_by_period
from pyxtdpthresh.extras.plotting.profile import FLAT_GAP, flatness
from pyxtdpthresh.extras.plotting.style import chart_style, save_figure
from pyxtdpthresh.extras.plotting.switch import regime_paths
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

matplotlib.use("Agg")


def estimate(df, regressors=("x",), **options):
    options = {"collapse": True, "grid": 25, "grid_ci": 25, "seed": 3, "n_boot": 49, **options}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(df, "y", regressors, q="q", id="id", time="t", **options)


@pytest.fixture(scope="module")
def jump():
    return estimate(simulate(n=300, t=7, seed=4))


@pytest.fixture(scope="module")
def kink():
    return estimate(simulate(n=300, t=7, seed=4, kink=True), ("x", "q"), kink=True)


@pytest.fixture(scope="module")
def point_only():
    return estimate(simulate(n=300, t=7, seed=4), bootstrap=False)


def texts(fig):
    return [t.get_text() for ax in fig.axes for t in ax.texts]


# ------------------------------------------------------------------- what the fit holds
def test_the_linearity_test_keeps_the_draws_its_p_value_counts():
    fit = estimate(simulate(n=300, t=7, seed=4))
    test = fit.bootstrap.linearity
    assert test.draws.size == test.n_valid == 49
    exceed = int(np.sum(test.draws >= test.statistic))
    assert test.p_value == pytest.approx((1 + exceed) / (1 + test.draws.size), abs=1e-15)


def test_the_profile_is_the_criterion_of_the_reported_estimate_at_each_grid_threshold(jump):
    gammas, values = jump.search.profile()
    assert gammas.size == jump.search.n_stage1
    on_grid = np.isclose(gammas, jump.search.fit.gamma, rtol=0, atol=1e-12)
    assert on_grid.any()
    assert values[on_grid][0] == pytest.approx(jump.search.fit.obj, rel=1e-12)
    assert np.nanmin(values) == pytest.approx(jump.search.fit.obj, rel=1e-12)


def test_flatness_reads_the_share_of_thresholds_within_the_chi_square_gap():
    sharp = np.array([0.0, 40.0, 80.0, 120.0, np.nan])
    assert flatness(sharp) == (0.25, False)
    flat = np.array([0.0, 1.0, 2.0, 3.0, 50.0, np.nan])
    share, is_flat = flatness(flat)
    assert share == pytest.approx(0.8) and is_flat
    assert flatness(np.array([FLAT_GAP, 0.0]))[0] == 1.0
    assert math.isnan(flatness(np.array([np.nan]))[0])


# ----------------------------------------------------------------------------- the figures
def test_every_kind_draws_a_figure_with_labelled_axes(jump):
    for kind in FIT_KINDS:
        options = {"var": "x"} if kind == "effect" else {}
        fig = plot(jump, kind, **options)
        assert fig.axes, kind
        assert all(ax.get_ylabel() or ax.get_xlabel() for ax in fig.axes), kind


def test_profile_draws_the_grid_criterion_and_marks_the_estimate(jump):
    fig = plot(jump, "profile")
    ax = fig.axes[0]
    gammas, values = jump.search.profile()
    ok = np.isfinite(values)
    curve = ax.lines[0]
    np.testing.assert_array_equal(curve.get_xdata(), gammas[ok])
    np.testing.assert_array_equal(curve.get_ydata(), values[ok])
    marker = ax.collections[0].get_offsets()[0]
    assert marker[0] == jump.search.fit.gamma and marker[1] == jump.search.fit.obj
    assert any(f"{jump.search.fit.gamma:.3f}" in t for t in texts(fig))
    assert ax.get_xlabel() == "Threshold (q)"


def test_a_weakly_identified_threshold_adds_the_flat_profile_note(jump):
    # 300 units and one-step-wide moments: the profile is within the gap on most of the grid, and
    # the confidence set of the threshold is the whole grid
    assert flatness(jump.search.profile()[1])[1]
    assert any("Flat profile" in t for t in texts(plot(jump, "profile")))
    assert math.isnan(jump.bootstrap.ci.lo) or jump.bootstrap.ci.n_admitted > 0


def test_a_sharp_profile_has_no_note():
    fit = estimate(simulate(n=1000, t=7, seed=4), bootstrap=False)
    assert not flatness(fit.search.profile()[1])[1]
    assert not any("Flat profile" in t for t in texts(plot(fit, "profile")))


def test_ci_plot_draws_the_statistic_the_critical_value_and_the_accepted_runs(jump):
    ci = jump.bootstrap.ci
    fig = plot(jump, "ci")
    ax = fig.axes[0]
    table = ci.table
    decided = np.isin(table[:, 5], (1.0, 2.0))
    ordered = table[np.argsort(table[:, 0])]
    keep = np.isin(ordered[:, 5], (1.0, 2.0))
    np.testing.assert_array_equal(ax.lines[0].get_xdata(), ordered[keep, 0])
    np.testing.assert_array_equal(ax.lines[0].get_ydata(), ordered[keep, 1])
    critical = ax.lines[1]
    finite = keep & np.isfinite(ordered[:, 2])
    np.testing.assert_array_equal(critical.get_ydata(), ordered[finite, 2])
    spans = [p for p in ax.patches if p.get_alpha() is not None and p.get_alpha() < 0.2]
    assert len(spans) == len(np.atleast_2d(ci.segments)) * (1 if ci.segments.size else 0)
    accepted = ax.collections[0].get_offsets()
    assert len(accepted) == int(np.sum(decided & (table[:, 3] == 1)))
    assert any("confidence set" in t for t in texts(fig))


def test_ci_plot_needs_the_bootstrap(point_only):
    with pytest.raises(DataError) as caught:
        plot(point_only, "ci")
    assert caught.value.key == "plot_needs_ci"
    with pytest.raises(DataError) as caught:
        plot(point_only, "linearity")
    assert caught.value.key == "plot_needs_linearity"


def test_linearity_plot_is_the_bootstrap_distribution_with_the_observed_statistic(jump):
    test = jump.bootstrap.linearity
    fig = plot(jump, "linearity")
    ax = fig.axes[0]
    assert sum(p.get_height() for p in ax.patches) == test.draws.size
    marked = [ln for ln in ax.lines if len(set(ln.get_xdata())) == 1]
    assert marked[0].get_xdata()[0] == test.statistic
    assert any(f"p = {test.p_value:.3f}" in t for t in texts(fig))


def test_coef_plot_has_one_interval_per_estimate_and_the_zero_line(jump):
    blocks = estimates_by_variable(jump)
    fig = plot(jump, "coef")
    ax = fig.axes[0]
    n_estimates = sum(len(v) for v in blocks.values())
    intervals = [ln for ln in ax.lines if len(ln.get_xdata()) == 2 and ln.get_xdata()[0] != 0]
    assert len(intervals) == n_estimates
    assert [t.get_text() for t in ax.get_yticklabels()] == list(blocks)
    only = plot(jump, "coef", variables=["x"])
    assert [t.get_text() for t in only.axes[0].get_yticklabels()] == ["x"]


def test_coef_intervals_are_the_estimate_plus_or_minus_the_normal_quantile(jump):
    from scipy.stats import norm

    blocks = estimates_by_variable(jump)
    z = norm.ppf(0.975)
    b, se = blocks["x"]["lower"]
    fig = plot(jump, "coef", variables=["x"])
    spans = [tuple(ln.get_xdata()) for ln in fig.axes[0].lines if len(ln.get_xdata()) == 2]
    assert any(s == pytest.approx((b - z * se, b + z * se), rel=1e-12) for s in spans), (
        "no interval for the lower slope"
    )


def test_regimes_plot_counts_every_equation_once_and_writes_the_shares(jump):
    fig = plot(jump, "regimes", trim=0)
    ax = fig.axes[0]
    stack = jump.stack
    q = stack.level_q[stack.current_level]
    bars = [bar for container in ax.containers for bar in container]
    assert sum(bar.get_height() for bar in bars) == np.isfinite(q).sum()
    shares = [t for t in texts(fig) if "regime" in t]
    low = int(np.sum(q <= jump.search.fit.gamma))
    assert any(f"{low} obs." in t for t in shares)


def test_the_window_cuts_the_tails_keeps_the_threshold_and_says_how_many_are_hidden(jump):
    stack = jump.stack
    q = stack.level_q[stack.current_level]
    fig = plot(jump, "regimes", trim=0.2)
    ax = fig.axes[0]
    lo, hi = ax.get_xlim()
    assert lo <= jump.search.fit.gamma <= hi
    shown = (q >= lo) & (q <= hi)
    bars = [bar for container in ax.containers for bar in container]
    assert sum(bar.get_height() for bar in bars) == shown.sum()
    assert any(f"{int((~shown).sum())} observations outside" in t for t in texts(fig))
    full = plot(jump, "regimes", trim=0)
    assert not any("outside" in t for t in texts(full))
    effect = plot(jump, "effect", var="x", trim=0.2)
    assert effect.axes[0].get_xlim() == pytest.approx((lo, hi))


def test_regressors_on_very_different_scales_get_a_panel_each(jump, monkeypatch):
    from pyxtdpthresh.extras.plotting import coef

    names = list(estimates_by_variable(jump))
    assert len(plot(jump, "coef", free_scale=False).axes) == 1
    facets = plot(jump, "coef", free_scale=True)
    assert [ax.get_title(loc="left") for ax in facets.axes] == names
    assert len(plot(jump, "coef").axes) == 1  # similar scales: one axis by default
    monkeypatch.setattr(coef, "SCALE_RATIO", 1.0)
    assert len(plot(jump, "coef").axes) == len(names)
    only_change = [ax for ax in facets.axes if ax.get_title(loc="left") == "_cons"][0]
    assert [t.get_text() for t in only_change.get_yticklabels()] == ["Change"]


def test_effect_plot_is_a_staircase_with_the_lower_and_upper_slopes(jump):
    fig = plot(jump, "effect", var="x")
    ax = fig.axes[0]
    blocks = estimates_by_variable(jump)["x"]
    levels = sorted(
        seg[0][1]
        for coll in ax.collections
        if type(coll).__name__ == "LineCollection"
        for seg in coll.get_segments()
    )
    assert levels == pytest.approx(sorted([blocks["lower"][0], blocks["upper"][0]]))
    assert ax.get_ylabel() == "Effect of x"


def test_effect_plot_of_a_kink_is_a_broken_line_through_the_threshold(kink):
    fig = plot(kink, "effect", var="q")
    ax = fig.axes[0]
    xs, ys = ax.lines[0].get_xdata(), ax.lines[0].get_ydata()
    gamma = kink.search.fit.gamma
    assert ys[np.flatnonzero(xs == gamma)[0]] == 0.0
    slope = kink.search.fit.theta[kink.names.index("lower:q")]
    delta = kink.search.fit.theta[-1]
    left, right = xs < gamma, xs > gamma
    np.testing.assert_allclose(np.diff(ys[left]) / np.diff(xs[left]), slope, rtol=1e-8)
    np.testing.assert_allclose(np.diff(ys[right]) / np.diff(xs[right]), slope + delta, rtol=1e-8)
    assert "Contribution of q" in ax.get_ylabel()


def test_effect_plot_asks_for_a_regressor_of_the_model(jump):
    with pytest.raises(SpecificationError) as caught:
        plot(jump, "effect")
    assert caught.value.key == "plot_no_variable"
    with pytest.raises(SpecificationError) as caught:
        plot(jump, "effect", var="nope")
    assert caught.value.key == "plot_unknown_variable"
    assert "x" in str(caught.value)


def test_switch_plot_splits_the_units_into_three_exhaustive_groups(jump):
    periods, share, counts = regime_paths(jump)
    assert counts.sum() == jump.n_units
    assert np.all((share >= 0) & (share <= 1))
    fig = plot(jump, "switch")
    line, bars = fig.axes
    np.testing.assert_allclose(line.lines[0].get_ydata(), 100 * share)
    assert [p.get_width() for p in bars.patches] == list(counts)


def test_instrument_plot_counts_the_columns_each_period_uses(jump):
    periods, counts = instruments_by_period(jump)
    assert periods.size == np.unique(jump.stack.time).size
    assert counts.max() <= jump.n_instruments
    ax = plot(jump, "instruments").axes[0]
    assert [p.get_height() for p in ax.patches] == list(counts)
    assert any(f"N = {jump.n_units} units" in t for t in texts(plot(jump, "instruments")))


def test_instrument_count_grows_without_collapse():
    fit = estimate(simulate(n=300, t=7, seed=4), collapse=False, bootstrap=False)
    _, counts = instruments_by_period(fit)
    assert np.all(np.diff(counts) >= 0) and counts[-1] > counts[0]


def test_residual_plot_shows_the_serial_correlation_statistics(jump):
    fig = plot(jump, "residuals")
    left, right = fig.axes
    heights = sorted(p.get_height() for p in right.patches)
    stats = sorted([jump.serial.ar1.statistic, jump.serial.ar2.statistic])
    np.testing.assert_allclose(heights, stats)
    assert [t.get_text() for t in right.get_xticklabels()] == ["AR(1)", "AR(2)"]


# ------------------------------------------------------------------ language, files, style
def test_the_french_figure_has_french_labels_and_a_decimal_comma(jump):
    fig = plot(jump, "ci", lang="fr")
    ax = fig.axes[0]
    assert ax.get_ylabel() == "Distance bootstrap D"
    assert ax.get_xlabel() == "Seuil (q)"
    assert any("," in t and "." not in t for t in texts(fig))
    assert any("," in t.get_text() for t in ax.get_xticklabels())


def test_the_language_defaults_to_the_global_option(jump):
    with option_context(lang="fr"):
        assert plot(jump, "linearity").axes[0].get_ylabel() == "Tirages"
    assert plot(jump, "linearity").axes[0].get_ylabel() == "Draws"


def test_figures_are_written_as_png_pdf_and_svg(jump, tmp_path):
    for suffix in (".png", ".pdf", ".svg"):
        target = tmp_path / f"profile{suffix}"
        plot(jump, "profile", path=target)
        assert target.stat().st_size > 1000
    fig = plot(jump, "profile")
    written = save_figure(fig, tmp_path / "both", formats=(".png", ".pdf"))
    assert [p.suffix for p in written] == [".png", ".pdf"] and all(p.exists() for p in written)
    assert (tmp_path / "profile.pdf").read_bytes()[:4] == b"%PDF"
    assert b"<svg" in (tmp_path / "profile.svg").read_bytes()[:400]


def test_an_unknown_kind_or_format_is_refused_with_its_key(jump, tmp_path):
    with pytest.raises(SpecificationError) as caught:
        plot(jump, "histogram")
    assert caught.value.key == "plot_unknown_kind"
    assert "profile" in str(caught.value)
    with pytest.raises(SpecificationError) as caught:
        save_figure(plot(jump, "profile"), tmp_path / "x.gif")
    assert caught.value.key == "plot_format"


def test_the_chart_style_does_not_leak_into_matplotlib_settings():
    before = dict(matplotlib.rcParams)
    with chart_style():
        assert matplotlib.rcParams["axes.spines.top"] is False
        assert matplotlib.rcParams["pdf.fonttype"] == 42
    assert dict(matplotlib.rcParams) == before


def test_figures_are_the_text_width_of_the_paper(jump):
    assert plot(jump, "profile").get_size_inches()[0] == pytest.approx(6.27)


def test_importing_the_package_does_not_import_matplotlib():
    code = "import sys, pyxtdpthresh; sys.exit('matplotlib' in sys.modules)"
    assert subprocess.run([sys.executable, "-c", code], check=False).returncode == 0


def test_a_fit_and_a_robustness_result_are_not_interchangeable(jump):
    assert set(FIT_KINDS) | {"robustness", "coverage", "power", "distribution"} == set(PLOT_KINDS)
    with pytest.raises(SpecificationError) as caught:
        plot(jump, "robustness")
    assert caught.value.key == "plot_wrong_result"
