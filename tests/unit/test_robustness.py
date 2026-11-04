"""Automatic robustness analysis (block I.4): the runs are the estimator's, the summaries exact."""

import math
import warnings
from dataclasses import fields, replace

import matplotlib
import numpy as np
import pandas as pd
import pytest
from test_search import simulate

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.extras.plotting import plot
from pyxtdpthresh.extras.robustness import DEFAULT_SETTINGS, RobustnessResult, robustness
from pyxtdpthresh.extras.robustness.sensitivity import REFERENCE, _plan
from pyxtdpthresh.models.xtdpthresh.fit import fit_point
from pyxtdpthresh.models.xtdpthresh.options import XtdpthreshOptions

matplotlib.use("Agg")

BASE = {"collapse": True, "grid": 25, "grid_ci": 25, "n_boot": 49, "seed": 3}
SETTINGS = {"grid": [15, 25, 40], "collapse": [True, False], "method": ["fod"], "kink": [True]}


@pytest.fixture(scope="module")
def frame():
    return simulate(n=300, t=7, seed=4)


@pytest.fixture(scope="module")
def result(frame):
    return robustness(frame, "y", ("x",), q="q", id="id", time="t", settings=SETTINGS, **BASE)


def direct(frame, **changes):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(frame, "y", ("x",), q="q", id="id", time="t", **{**BASE, **changes})


def with_gamma(fit, gamma):
    return replace(fit, search=replace(fit.search, fit=replace(fit.search.fit, gamma=gamma)))


def with_segments(fit, segments, unresolved=0):
    segments = np.asarray(segments, dtype=float)
    ci = replace(
        fit.bootstrap.ci,
        segments=segments,
        lo=float(segments[:, 0].min()),
        hi=float(segments[:, 1].max()),
        n_unresolved=unresolved,
    )
    return replace(fit, bootstrap=replace(fit.bootstrap, ci=ci))


# --------------------------------------------------------------------------------- plan
def test_each_run_changes_one_option_and_skips_the_reference_value():
    plan = _plan(
        {"grid": [25, 50], "collapse": [True, False]}, {"grid": 25, "collapse": True}, product=False
    )
    assert plan == [{"grid": 50}, {"collapse": False}]


def test_the_product_runs_every_other_combination_once():
    settings = {"grid": [25, 50], "collapse": [True, False], "method": ["fd"]}
    base = {"grid": 25, "collapse": True}
    plan = _plan(settings, base, product=True)
    assert len(plan) == 3  # 2 x 2 x 1 minus the reference
    assert {"grid": 25, "collapse": True, "method": "fd"} not in plan
    assert {"grid": 50, "collapse": False, "method": "fd"} in plan


def test_defaults_are_options_of_the_estimator():
    options = {f.name for f in fields(XtdpthreshOptions)}
    assert set(DEFAULT_SETTINGS) <= options


def test_bad_settings_are_refused_with_their_keys(frame):
    for settings, key in (
        ({"gridd": [10]}, "robust_unknown_setting"),
        ({"grid": []}, "robust_empty_setting"),
        ({"method": "fod"}, "robust_empty_setting"),
    ):
        with pytest.raises(SpecificationError) as caught:
            robustness(frame, "y", ("x",), q="q", id="id", time="t", settings=settings, **BASE)
        assert caught.value.key == key


def test_a_reference_that_cannot_be_estimated_raises(frame):
    with pytest.raises(SpecificationError):
        robustness(
            frame,
            "y",
            ("x",),
            q="q",
            id="id",
            time="t",
            settings={"trim": [0.1]},
            **{**BASE, "grid": 1},
        )


# ------------------------------------------------------------------------------ the runs
def test_the_runs_are_the_reference_then_the_variations(result):
    labels = [run.label for run in result.runs]
    assert labels == [
        REFERENCE, "grid=15", "grid=40", "collapse=False", "method=fod", "kink=True",
    ]  # fmt: skip
    assert result.runs[0].changes == {} and result.runs[3].changes == {"collapse": False}


def test_every_run_is_the_estimator_with_the_same_options_and_seed(frame, result):
    for run in result.runs:
        if run.fit is None:
            continue
        expected = direct(frame, **run.changes)
        assert run.fit.search.fit.gamma == expected.search.fit.gamma
        np.testing.assert_array_equal(run.fit.search.fit.theta, expected.search.fit.theta)
        np.testing.assert_array_equal(run.fit.bootstrap.ci.table, expected.bootstrap.ci.table)
        assert run.fit.bootstrap.linearity.p_value == expected.bootstrap.linearity.p_value
        assert run.fit.scalars["rseed"] == BASE["seed"] == result.seed


def test_a_seed_is_drawn_and_shared_when_none_is_given(frame):
    options = {k: v for k, v in BASE.items() if k != "seed"}
    out = robustness(
        frame, "y", ("x",), q="q", id="id", time="t", settings={"grid": [15]}, **options
    )
    seeds = {run.fit.scalars["rseed"] for run in out.runs}
    assert seeds == {float(out.seed)}


def test_a_failed_variation_is_recorded_with_its_message_and_key(frame):
    out = robustness(
        frame, "y", ("x",), q="q", id="id", time="t", settings={"grid": [1, 15]}, **BASE
    )  # fmt: skip
    failed = out.runs[1]
    assert failed.label == "grid=1" and failed.fit is None
    assert failed.error and failed.key
    assert out.runs[2].fit is not None
    assert out.table.loc["grid=1", "status"] == "failed"
    assert out.table.loc["grid=1", "error"] == failed.error
    assert "grid=1" not in out.fits and list(out.fits) == [REFERENCE, "grid=15"]


# ------------------------------------------------------------------------------- the table
def test_the_table_holds_the_threshold_its_set_the_slopes_and_the_tests(result):
    table = result.table
    assert list(table.index) == [r.label for r in result.runs]
    assert {
        "gamma",
        "gamma_lo",
        "gamma_hi",
        "ci_nseg",
        "pval_lin",
        "hansen_p",
        "lower:x",
        "upper:x",
    } <= set(table.columns)
    for run in result.runs:
        s = run.fit.scalars
        row = table.loc[run.label]
        assert row["gamma"] == s["gamma"]
        assert (row["gamma_lo"] == s["gamma_lo"]) or (
            math.isnan(row["gamma_lo"]) and math.isnan(s["gamma_lo"])
        )
        assert row["n_units"] == s["N_units"] and row["status"] == "ok"
    ref = result.reference
    assert table.loc[REFERENCE, "lower:x"] == ref.search.fit.theta[ref.names.index("lower:x")]
    assert table.loc[REFERENCE, "upper:x"] == ref.upper.b[ref.upper.names.index("upper:x")]
    assert table.loc["kink=True", "shape"] == "kink" and table.loc["method=fod", "method"] == "fod"
    assert str(table["in_reference_ci"].dtype) == "boolean"
    assert table.loc[REFERENCE, "in_reference_ci"]
    assert isinstance(result.to_dataframe(), pd.DataFrame)


def test_the_slope_frame_has_every_coefficient_of_every_run(result):
    frame = result.coefficients()
    assert frame.index.names == ["setting", "block", "variable"]
    assert set(frame.index.get_level_values("setting")) == set(result.fits)
    ref = result.reference
    value = frame.loc[(REFERENCE, "change", "_cons"), "estimate"]
    assert value == ref.search.fit.theta[ref.names.index("change:_cons")]


def test_the_stargazer_has_one_column_per_successful_run(result):
    table = result.stargazer()
    assert table.spec.columns == tuple(result.fits)
    assert len(table.spec.stats[0].values) == len(result.fits)
    custom = result.stargazer(statistic="t", digits=2)
    assert custom.options.digits == 2


# ------------------------------------------------------------------- the stability index
def test_the_stability_index_is_the_share_of_runs_inside_the_reference_set(result):
    reference = with_segments(result.reference, [[0.2, 0.4], [0.6, 0.7]])
    others = [with_gamma(result.reference, g) for g in (0.3, 0.5, 0.65, 0.9)]
    runs = tuple(
        [replace(result.runs[0], fit=reference)]
        + [replace(result.runs[i + 1], fit=f) for i, f in enumerate(others)]
    )
    out = RobustnessResult(runs, result.seed)
    assert out.stability() == pytest.approx(2 / 4)  # 0.3 and 0.65 are inside a segment
    assert out.stability("hull") == pytest.approx(3 / 4)  # 0.5 is in the gap between segments
    with pytest.raises(SpecificationError):
        out.stability("both")
    assert bool(out.table.loc["grid=15", "in_reference_ci"]) is True


def test_the_stability_index_is_missing_without_a_complete_reference_set(result):
    incomplete = with_segments(result.reference, [[0.2, 0.4]], unresolved=2)
    runs = (replace(result.runs[0], fit=incomplete), *result.runs[1:])
    assert math.isnan(RobustnessResult(runs, result.seed).stability())
    alone = RobustnessResult(result.runs[:1], result.seed)
    assert math.isnan(alone.stability())


def test_failed_runs_do_not_count_in_the_stability_index(frame):
    out = robustness(
        frame, "y", ("x",), q="q", id="id", time="t", settings={"grid": [1, 15]}, **BASE
    )
    assert out.stability() == pytest.approx(float(out.table.loc["grid=15", "in_reference_ci"]))


# --------------------------------------------------------------------------------- the plot
def test_the_robustness_graph_has_a_row_per_run_the_reference_in_orange(result):
    fig = result.plot()
    ax = fig.axes[0]
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert labels == ["reference", *[r.label for r in result.runs[1:]]]
    offsets = ax.collections[-len(result.runs) :]
    estimates = [c.get_offsets()[0][0] for c in offsets]
    expected = [run.fit.search.fit.gamma for run in result.runs]
    np.testing.assert_allclose(estimates, expected)
    assert matplotlib.colors.to_hex(offsets[0].get_facecolor()[0]) == "#eb6834"
    assert matplotlib.colors.to_hex(offsets[1].get_facecolor()[0]) == "#2a78d6"
    text = [t.get_text() for t in ax.texts]
    assert any(t.startswith("stability index") for t in text)


def test_the_graph_marks_failed_runs_and_speaks_french(frame):
    out = robustness(
        frame, "y", ("x",), q="q", id="id", time="t", settings={"grid": [1, 15]}, **BASE
    )
    fig = plot(out, "robustness", lang="fr")
    ax = fig.axes[0]
    assert [t.get_text() for t in ax.texts if "estimé" in t.get_text()] == ["non estimé"]
    assert ax.get_yticklabels()[0].get_text() == "référence"
    assert ax.get_xlabel() == "Seuil (q)"


def test_the_graph_is_written_to_a_file(result, tmp_path):
    result.plot(path=tmp_path / "robust.png")
    result.plot(path=tmp_path / "robust.pdf")
    assert (tmp_path / "robust.png").stat().st_size > 1000
    assert (tmp_path / "robust.pdf").read_bytes()[:4] == b"%PDF"


def test_a_robustness_result_cannot_be_drawn_as_a_fit(result):
    with pytest.raises(SpecificationError) as caught:
        plot(result, "profile")
    assert caught.value.key == "plot_wrong_result"
