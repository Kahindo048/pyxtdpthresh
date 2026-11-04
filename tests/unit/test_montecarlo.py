"""Monte Carlo experiments (block I.5.2): each replication is the estimator, the summaries exact."""

import math

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh.extras.reporting.extract import extract
from pyxtdpthresh.extras.simulation import DESIGNS, MonteCarloResult, monte_carlo, simulate_panel
from pyxtdpthresh.extras.simulation.montecarlo import _columns, _Job, _replicate, rate
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

FAST = {"n_boot": 29, "grid": 25, "grid_ci": 25}


def run(**changes):
    arguments = {"reps": 4, "seed": 11, "workers": 1, **FAST} | changes
    return monte_carlo(arguments.pop("design", "gong_seo"), 300, 6, **arguments)


@pytest.fixture(scope="module")
def result():
    return run()


def synthetic(design="gong_seo", rows=(), shifts=(0.1, 0.5), alpha=0.05):
    """A result whose records are written by hand, to check the summaries."""
    spec = DESIGNS[design]
    frame = pd.DataFrame(list(rows)).reindex(columns=_columns(spec, shifts))
    return MonteCarloResult(spec, 300, 6, len(frame), 1, alpha, tuple(shifts), frame)


# ------------------------------------------------------------- a replication is the estimator
def test_a_replication_is_the_estimator_on_its_own_seeds(result):
    child = np.random.SeedSequence(11).spawn(4)[2]
    data_seed, boot_seed = child.spawn(2)
    design = DESIGNS["gong_seo"]
    frame = simulate_panel(design, 300, 6, seed=data_seed)
    seed = int(boot_seed.generate_state(1)[0] & 0x7FFFFFFF)
    fit = fit_point(frame, "y", id="id", time="t", seed=seed, **design.arguments(), **FAST)
    row = result.records.iloc[2]
    assert row["gamma"] == fit.scalars["gamma"]
    assert row["gamma_lo"] == fit.scalars["gamma_lo"] and row["pval_lin"] == fit.scalars["pval_lin"]
    coefs = extract(fit).coefs
    for name in ("lower:L.y", "change:q", "upper:q"):
        block, _, variable = name.partition(":")
        assert row[f"b:{name}"] == coefs[(block, variable)].b
        assert row[f"se:{name}"] == coefs[(block, variable)].se
    assert row["n_obs"] == fit.scalars["N"] and row["n_units"] == fit.scalars["N_units"]


def test_the_columns_are_fixed_and_the_truth_is_the_designs(result):
    assert list(result.records.columns) == _columns(result.design, result.shifts)
    assert result.records["rep"].tolist() == [0, 1, 2, 3]
    assert (result.records["status"] == "ok").all() and result.n_failed == 0
    assert set(result.estimates().index) >= {"gamma", "lower:L.y", "upper:q"}
    assert result.estimates().loc["gamma", "truth"] == 0.25


def test_the_coverage_columns_are_the_confidence_set_tested_at_the_truth(result):
    ok = result.ok
    for _, row in ok.iterrows():
        inside = row["gamma_lo"] <= 0.25 <= row["gamma_hi"]
        assert bool(row["cover_hull"]) == inside
        assert bool(row["cover_segments"]) <= bool(row["cover_hull"])
        assert bool(row["reject_0"]) is (not bool(row["cover_segments"]))


def test_slope_coverage_uses_the_normal_interval_of_the_level(result):
    for _, row in result.ok.iterrows():
        z = 1.959964
        for name, truth in (("lower:L.y", 0.6), ("upper:q", 3.0)):
            held = abs(row[f"b:{name}"] - truth) <= z * row[f"se:{name}"]
            assert bool(row[f"cover:{name}"]) == held
    wide = run(level=99.0, reps=2)
    assert wide.records["cover:upper:q"].notna().all()


# ------------------------------------------------------------------------- reproducibility
def test_the_experiment_is_a_function_of_the_seed(result):
    again = run()
    pd.testing.assert_frame_equal(again.records, result.records)
    other = run(seed=12)
    assert not np.allclose(other.records["gamma"], result.records["gamma"])


def test_the_result_does_not_depend_on_the_number_of_workers(result):
    parallel = run(workers=2)
    pd.testing.assert_frame_equal(parallel.records, result.records)


def test_a_seed_is_drawn_and_recorded_when_none_is_given():
    drawn = run(seed=None, reps=2)
    assert isinstance(drawn.seed, int)
    pd.testing.assert_frame_equal(run(seed=drawn.seed, reps=2).records, drawn.records)


# ---------------------------------------------------------------------------- the summaries
def test_bias_rmse_and_coverage_of_a_hand_made_experiment():
    rows = [
        {"status": "ok", "gamma": g, "cover_segments": c, "cover_hull": True, "ci_complete": True}
        for g, c in ((0.15, True), (0.35, True), (0.45, False), (0.05, True))
    ]
    out = synthetic(rows=rows)
    gamma = out.estimates().loc["gamma"]
    errors = np.array([-0.10, 0.10, 0.20, -0.20])
    assert gamma["n"] == 4 and gamma["mean"] == pytest.approx(0.25)
    assert gamma["bias"] == pytest.approx(0.0, abs=1e-12)
    assert gamma["rmse"] == pytest.approx(math.sqrt(np.mean(errors**2)))
    assert gamma["sd"] == pytest.approx(np.std(errors, ddof=1))
    assert gamma["bias_mcse"] == pytest.approx(np.std(errors, ddof=1) / 2)
    assert gamma["median_bias"] == pytest.approx(0.0, abs=1e-12)
    assert gamma["coverage"] == 0.75
    assert gamma["coverage_mcse"] == pytest.approx(math.sqrt(0.75 * 0.25 / 4))
    table = out.threshold_coverage()
    assert table.loc["hull", "coverage"] == 1.0 and table.loc["segments", "coverage"] == 0.75


def test_slope_coverage_counts_only_the_defined_intervals():
    rows = [
        {"status": "ok", "b:lower:q": 1.1, "cover:lower:q": True},
        {"status": "ok", "b:lower:q": 0.9, "cover:lower:q": False},
        {"status": "ok", "b:lower:q": 1.0, "cover:lower:q": None},
        {"status": "failed"},
    ]
    row = synthetic(rows=rows).estimates().loc["lower:q"]
    assert row["n"] == 3 and row["n_coverage"] == 2 and row["coverage"] == 0.5
    assert row["bias"] == pytest.approx(0.0, abs=1e-12)


def test_incomplete_sets_are_left_out_of_the_coverage_and_counted():
    rows = [
        {"status": "ok", "gamma": 0.2, "cover_segments": True, "ci_complete": True},
        {"status": "ok", "gamma": 0.3, "cover_segments": None, "ci_complete": False},
    ]
    table = synthetic(rows=rows).threshold_coverage()
    assert table.loc["segments", "n"] == 1 and table.loc["segments", "coverage"] == 1.0
    assert table.loc["segments", "incomplete"] == 0.5


def test_power_is_the_rejection_of_the_shifted_thresholds():
    rows = [
        {"status": "ok", "reject_0": r0, "reject_0.1": r1, "reject_0.5": r5}
        for r0, r1, r5 in (
            (False, False, True),
            (False, True, True),
            (True, True, True),
            (False, False, True),
        )
    ]
    power = synthetic(rows=rows).power()
    assert list(power.index) == [0.0, 0.1, 0.5]
    assert power["rejection"].tolist() == [0.25, 0.5, 1.0]
    assert power.loc[0.1, "mcse"] == pytest.approx(math.sqrt(0.25 / 4))


def test_the_linearity_rate_is_a_size_without_threshold_and_a_power_with_one():
    rows = [{"status": "ok", "reject_linearity": r} for r in (True, False, False, False)]
    assert synthetic("linear", rows).linearity()["kind"] == "size"
    assert synthetic("gong_seo", rows).linearity()["kind"] == "power"
    lin = synthetic("gong_seo", rows, alpha=0.05).linearity()
    assert lin["rate"] == 0.25 and lin["n"] == 4 and lin["alpha"] == 0.05


def test_rate_ignores_missing_values_and_handles_an_empty_column():
    assert rate(pd.Series([True, False, None, True])) == (
        pytest.approx(2 / 3),
        pytest.approx(math.sqrt(2 / 9 / 3)),
        3,
    )
    share, error, count = rate(pd.Series([None, None], dtype=object))
    assert math.isnan(share) and math.isnan(error) and count == 0


def test_the_text_summary_names_the_design_and_the_counts(result):
    text = result.summary()
    assert "design gong_seo" in text and "4 replications (0 failed)" in text and "seed 11" in text
    assert "linearity test, power" in text


# ---------------------------------------------------------------------- designs and options
def test_the_linear_design_reports_a_size_and_has_no_threshold_rows():
    out = run(design="linear", reps=3)
    assert out.linearity()["kind"] == "size"
    assert "gamma" not in out.estimates().index
    assert out.records["cover_segments"].isna().all()
    assert out.estimates().loc["lower:L.y", "truth"] == 0.6


def test_simulation_parameters_reach_the_design_and_the_generator():
    out = run(simulation={"jump": 0.5, "unbalanced": 0.3}, reps=2)
    assert out.design.delta0 == pytest.approx(0.0) and out.design.jump == pytest.approx(0.5)
    assert out.estimates().loc["change:_cons", "truth"] == pytest.approx(0.0)
    assert (out.ok["n_obs"] < 300 * 5).all()  # gaps: fewer equations than a balanced panel
    assert out.simulation["unbalanced"] == 0.3


def test_options_override_the_arguments_of_the_design():
    default = run(reps=2)
    collapsed = run(reps=2, collapse=True)
    assert (collapsed.ok["n_instruments"] < default.ok["n_instruments"]).all()


def test_the_instruments_are_those_of_the_paper_plus_a_constant_per_equation():
    """Gong and Seo, section 5: (y_{t-2..1}, q_{t-1..1}) is 24 instruments at T = 6, with T - 2 = 4
    equations; the estimator adds one constant per equation (the regime intercept needs it).
    Appendix C.3 drops q_{t-1}: (y_{t-2..1}, q_{t-2..1}) is 20."""
    weak = run(reps=2)
    assert (weak.ok["n_instruments"] == 24 + 4).all()
    endogenous = run(reps=2, design="gong_seo_endog")
    assert (endogenous.ok["n_instruments"] == 20 + 4).all()


def test_a_failing_replication_is_recorded_with_its_message_and_key():
    out = run(reps=3, grid=1)
    assert out.n_failed == 3 and (out.records["status"] == "failed").all()
    assert (out.records["error"] != "").all() and out.records["key"].notna().all()
    estimates = out.estimates()
    assert list(estimates.index) == ["gamma"] and estimates.loc["gamma", "n"] == 0
    assert math.isnan(out.linearity()["rate"])
    assert "3 failed" in out.summary()


def test_failures_are_excluded_from_the_means_not_from_the_records():
    frame = synthetic(rows=[{"status": "ok", "gamma": 0.25}, {"status": "failed", "error": "x"}])
    assert frame.n_failed == 1 and len(frame.ok) == 1 and len(frame.to_dataframe()) == 2
    assert frame.estimates().loc["gamma", "n"] == 1


@pytest.mark.parametrize(
    ("changes", "key"),
    [
        ({"reps": 0}, "sim_bad_size"),
        ({"alpha": 1.5}, "sim_bad_alpha"),
        ({"workers": 0}, "sim_bad_size"),
        ({"simulation": {"nope": 1.0}}, "sim_unknown_parameter"),
        ({"design": "nope"}, "sim_unknown_design"),
    ],
)
def test_bad_experiments_are_refused_with_their_key(changes, key):
    with pytest.raises(SpecificationError) as caught:
        run(**changes)
    assert caught.value.key == key


def test_the_job_is_picklable_for_the_workers():
    import pickle

    job = _Job(0, DESIGNS["gong_seo"], 50, 5, np.random.SeedSequence(1), {}, FAST, (0.1,), 0.05)
    assert pickle.loads(pickle.dumps(job)).seed.entropy == 1
    assert _replicate(job)["status"] == "ok"
