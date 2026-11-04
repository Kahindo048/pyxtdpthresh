"""Public entry points and result classes (I.2.11): they delegate, they never recompute."""

import json
import subprocess
import sys
import time
import warnings

import matplotlib
import numpy as np
import pandas as pd
import pytest

import pyxtdpthresh
from pyxtdpthresh import (
    ThresholdStargazer,
    XtdpthreshResult,
    XthenregResult,
    compare,
    load_dataset,
    xtdpthresh,
    xthenreg,
)
from pyxtdpthresh._errors import DataError, SpecificationError
from pyxtdpthresh.extras.augment import augment
from pyxtdpthresh.extras.reporting import diagnose, settings_log, summary, to_dataframe
from pyxtdpthresh.models.xtdpthresh.fit import fit_point
from pyxtdpthresh.models.xthenreg.design import prepare_data
from pyxtdpthresh.models.xthenreg.estimate import estimate

matplotlib.use("Agg")

CALL = {"q": "tobin_q", "id": "firm", "time": "year"}
BOOT = {"n_boot": 29, "grid_ci": 30}


@pytest.fixture(scope="module")
def frame():
    df = load_dataset("invest")
    return df[df["firm"] <= df["firm"].unique()[120]].reset_index(drop=True)


@pytest.fixture(scope="module")
def balanced(frame):
    return frame[frame["year"] <= 1980].reset_index(drop=True)


@pytest.fixture(scope="module")
def result(frame):
    return xtdpthresh(frame, "invest", ["cashflow"], seed=7, **CALL, **BOOT)


@pytest.fixture(scope="module")
def henreg(balanced):
    return xthenreg(
        balanced, "invest", ["cashflow", "tobin_q"], q="debt", id="firm", time="year",
        grid_num=30, boot_reps=19, seed=3,
    )  # fmt: skip


# ------------------------------------------------------------------------------- import
def test_importing_the_package_loads_neither_numba_nor_pandas_nor_matplotlib():
    code = (
        "import sys, pyxtdpthresh; "
        "print([m for m in ('numba', 'pandas', 'matplotlib') if m in sys.modules])"
    )
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True)
    assert out.stdout.strip() == "[]", out.stderr


def test_every_public_name_loads_and_an_unknown_one_is_refused():
    for name in pyxtdpthresh.__all__:
        assert getattr(pyxtdpthresh, name) is not None
    with pytest.raises(AttributeError):
        pyxtdpthresh.nothing_of_the_kind  # noqa: B018
    assert "xtdpthresh" in dir(pyxtdpthresh)


def test_warmup_is_public_and_can_be_called_twice():
    pyxtdpthresh.warmup()
    start = time.perf_counter()
    pyxtdpthresh.warmup()
    assert time.perf_counter() - start < 0.5  # everything is compiled or loaded by now


# --------------------------------------------------------------------- the same numbers
def test_the_result_holds_exactly_the_numbers_of_fit_point(frame, result):
    direct = fit_point(frame, "invest", ["cashflow"], seed=7, **CALL, **BOOT)
    assert isinstance(result, XtdpthreshResult)
    np.testing.assert_array_equal(result.params.to_numpy(), direct.search.fit.theta)
    np.testing.assert_array_equal(result.cov.to_numpy(), direct.cov)
    assert list(result.scalars) == list(direct.scalars)
    np.testing.assert_array_equal(list(result.scalars.values()), list(direct.scalars.values()))
    assert result.gamma == direct.search.fit.gamma
    assert list(result.params.index) == list(direct.names)
    np.testing.assert_allclose(result.se.to_numpy() ** 2, np.diag(direct.cov))
    assert (result.n_obs, result.n_units) == (direct.n_obs, direct.n_units)


def test_the_gamma_interval_is_the_hull_of_the_confidence_set(result):
    low, high = result.gamma_ci
    assert low < high
    assert (low, high) == (result.scalars["gamma_lo"], result.scalars["gamma_hi"])


def test_the_upper_regime_is_a_frame_and_a_hinge_without_the_threshold_variable_has_none(
    frame, result
):
    assert list(result.upper.index) == ["upper:L.invest", "upper:cashflow"]
    kink = xtdpthresh(frame, "invest", ["cashflow", "tobin_q"], kink=True, bootstrap=False, **CALL)
    assert list(kink.upper.index) == ["upper:tobin_q"]
    with pytest.warns(UserWarning, match="one-sided hinge"):
        hinge = xtdpthresh(frame, "invest", ["cashflow"], kink=True, bootstrap=False, **CALL)
    assert hinge.upper is None


# ------------------------------------------------------------------------------- the seed
def test_a_seed_is_drawn_recorded_and_replays_the_run(frame):
    first = xtdpthresh(frame, "invest", ["cashflow"], **CALL, **BOOT)
    assert isinstance(first.seed, int) and first.scalars["rseed"] == first.seed
    again = xtdpthresh(frame, "invest", ["cashflow"], seed=first.seed, **CALL, **BOOT)
    assert again.gamma_ci == first.gamma_ci
    assert again.scalars["pval_lin"] == first.scalars["pval_lin"]


def test_two_unseeded_runs_draw_different_seeds(frame):
    seeds = {xtdpthresh(frame, "invest", ["cashflow"], **CALL, **BOOT).seed for _ in range(3)}
    assert len(seeds) > 1


def test_a_given_seed_is_kept_and_no_seed_is_drawn_without_bootstrap(frame, result):
    assert result.seed == 7
    off = xtdpthresh(frame, "invest", ["cashflow"], bootstrap=False, **CALL)
    assert off.seed is None


def test_the_journal_reports_the_drawn_seed(frame):
    run = xtdpthresh(frame, "invest", ["cashflow"], **CALL, **BOOT)
    text = str(run.settings_log())
    assert str(run.seed) in text and "cannot be repeated" not in text


# ----------------------------------------------------------------------------- the text
def test_print_and_repr_give_the_summary(result):
    assert str(result) == repr(result) == result.summary()
    assert result.summary() == summary(result.fit, when=result._when)
    assert "Lower regime" in str(result) and "Diagnostic Tests" in str(result)
    assert "Régime haut" in result.summary(lang="fr")


def test_the_notebook_displays_are_the_table(result):
    assert "<table" in result._repr_html_()
    assert "tabular" in result._repr_latex_()


# ------------------------------------------------------------------------------- tables
def test_the_exports_are_the_table_of_this_model_alone(result):
    reference = ThresholdStargazer([result.fit])
    assert result.to_latex() == reference.to_latex()
    assert result.to_html() == reference.to_html()
    assert result.to_markdown() == reference.to_markdown()
    assert result.to_text() == reference.to_text()
    assert result.to_csv() == reference.to_csv()


def test_the_options_of_the_table_are_passed_on(result):
    text = result.to_text(digits=2, covariate_labels={"cashflow": "Cash flow"})
    assert "Cash flow" in text
    assert result.to_markdown(statistic="ci") != result.to_markdown()


def test_full_output_adds_the_scalars_of_the_fit(result):
    short, full = result.to_text(), result.to_text(full_output=True)
    assert len(full.splitlines()) > len(short.splitlines())
    assert "N_units" in full and "hansen" in full and "N_units" not in short


def test_the_files_are_written(tmp_path, result):
    tex = tmp_path / "t.tex"
    assert result.to_latex(tex) == tex.read_text(encoding="utf-8")
    assert result.to_word(tmp_path / "t.docx").exists()
    assert result.to_excel(tmp_path / "t.xlsx").exists()


def test_compare_accepts_results_and_containers_alike(frame, result):
    other = xtdpthresh(frame, "invest", ["cashflow"], method="fod", seed=7, **CALL, **BOOT)
    by_result = compare([result, other], model_names=["FD", "FOD"]).to_text()
    by_fit = compare([result.fit, other.fit], model_names=["FD", "FOD"]).to_text()
    assert by_result == by_fit
    assert isinstance(compare([result, result]), ThresholdStargazer)


def test_to_dataframe_and_to_json_read_the_fit(result):
    pd.testing.assert_frame_equal(result.to_dataframe(), to_dataframe(result.fit))
    record = json.loads(result.to_json())
    assert record["coefficients"] and record["options"]["seed"] == 7


# ---------------------------------------------------------------------------- the reports
def test_the_reports_are_those_of_the_extras(result):
    assert str(result.diagnose()) == str(diagnose(result.fit))
    assert str(result.settings_log("fr")) == str(settings_log(result.fit, "fr"))
    assert not result.ci_table().empty
    assert list(result.regime_table().index) == ["lower", "upper"]


def test_plot_draws_and_writes_a_file(tmp_path, result):
    figure = result.plot("regimes", path=tmp_path / "r.png")
    assert figure is not None and (tmp_path / "r.png").exists()
    with pytest.raises(SpecificationError) as caught:
        result.plot("nothing")
    assert caught.value.key == "plot_unknown_kind"


# ------------------------------------------------------------------------------ the data
def test_predict_and_augment_use_the_data_given(frame, result):
    residuals = result.predict("residuals", frame)
    pd.testing.assert_series_equal(residuals, result.fit.predict("residuals", frame))
    out = result.augment(frame, kinds=("residuals", "regime"), prefix="m_")
    pd.testing.assert_frame_equal(
        out, augment(result.fit, frame, kinds=("residuals", "regime"), prefix="m_")
    )
    assert {"m_residuals", "m_regime"} <= set(out.columns)


# ----------------------------------------------------------------------------- the inputs
def test_a_multiindex_replaces_id_and_time(frame, result):
    indexed = frame.set_index(["firm", "year"])
    run = xtdpthresh(indexed, "invest", ["cashflow"], q="tobin_q", seed=7, **BOOT)
    np.testing.assert_array_equal(run.params.to_numpy(), result.params.to_numpy())


def test_a_misspelled_variable_is_refused_with_its_key(frame):
    with pytest.raises(DataError) as caught:
        xtdpthresh(frame, "invest", ["cashflow"], q="tobinq", id="firm", time="year")
    assert caught.value.key == "variable_not_found"


def test_a_bad_option_is_refused_with_the_rule_and_the_stata_code(frame):
    with pytest.raises(SpecificationError) as caught:
        xtdpthresh(frame, "invest", ["cashflow"], method="nope", **CALL)
    assert caught.value.stata_code == 198


def test_warnings_are_those_of_the_estimator(frame):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        xtdpthresh(frame, "invest", "cashflow", bootstrap=False, warn=False, **CALL)


# --------------------------------------------------------------------------- xthenreg
def test_xthenreg_holds_exactly_the_numbers_of_estimate(balanced, henreg):
    data = prepare_data(balanced, "invest", "debt", ["cashflow", "tobin_q"], id="firm", time="year")
    direct = estimate(data, grid_num=30, boot_reps=19, seed=3)
    assert isinstance(henreg, XthenregResult)
    np.testing.assert_array_equal(henreg.params.to_numpy(), direct.coef)
    np.testing.assert_array_equal(henreg.cov.to_numpy(), direct.cov)
    np.testing.assert_array_equal(henreg.ci.to_numpy(), direct.ci)
    assert henreg.gamma == direct.gamma and henreg.fit.boots_p == direct.boots_p
    assert henreg.scalars["N"] == direct.n_units and henreg.scalars["boots_p"] == direct.boots_p


def test_xthenreg_records_the_seed_given_or_drawn(balanced, henreg):
    assert henreg.seed == 3 and json.loads(henreg.to_json())["options"]["seed"] == 3
    drawn = xthenreg(balanced, "invest", "cashflow", q="debt", id="firm", time="year",
                     grid_num=20, boot_reps=9)  # fmt: skip
    assert isinstance(drawn.seed, int)
    none = xthenreg(balanced, "invest", "cashflow", q="debt", id="firm", time="year", grid_num=20)
    assert none.seed is None


def test_xthenreg_prints_and_exports_like_xtdpthresh(henreg, result):
    assert "Threshold" in str(henreg) and "<table" in henreg._repr_html_()
    assert henreg.to_latex() == ThresholdStargazer([henreg.fit]).to_latex()
    table = compare([result, henreg], model_names=["xtdpthresh", "xthenreg"]).to_text()
    assert "xtdpthresh" in table and "xthenreg" in table
    assert henreg.gamma_ci == (henreg.ci.iloc[-1, 0], henreg.ci.iloc[-1, 1])


def test_xthenreg_has_no_method_that_only_xtdpthresh_provides(henreg):
    for name in ("plot", "diagnose", "predict", "augment", "settings_log"):
        assert not hasattr(henreg, name)


def test_the_exceptions_and_the_warning_are_public():
    from pyxtdpthresh import _errors

    for name in ("PyxdpthreshError", "SpecificationError", "DataError", "NumericalError",
                 "PyxdpthreshWarning"):  # fmt: skip
        assert name in pyxtdpthresh.__all__
        assert getattr(pyxtdpthresh, name) is getattr(_errors, name)
    assert issubclass(pyxtdpthresh.SpecificationError, pyxtdpthresh.PyxdpthreshError)
    assert issubclass(pyxtdpthresh.PyxdpthreshWarning, UserWarning)


def test_a_bad_option_can_be_caught_with_the_public_class(frame):
    with pytest.raises(pyxtdpthresh.SpecificationError) as caught:
        xtdpthresh(frame, "invest", grid=5, bootstrap=False, **CALL)
    assert caught.value.stata_code == 198 and caught.value.key == "opt_grid"


def test_xthenreg_takes_the_bandwidth_multiplier(balanced):
    args = ("invest", "cashflow")
    kw = {"q": "debt", "id": "firm", "time": "year", "grid_num": 20}
    default = xthenreg(balanced, *args, **kw)
    wide = xthenreg(balanced, *args, h_0=3.0, **kw)
    assert wide.scalars["bandwidth"] == pytest.approx(2 * default.scalars["bandwidth"])
    assert wide.gamma == default.gamma
    np.testing.assert_allclose(wide.params, default.params)
    assert not np.allclose(wide.cov.to_numpy(), default.cov.to_numpy())


@pytest.mark.parametrize("kind", ["profile", "regimes", "effect"])
def test_a_graph_of_an_xthenreg_result_is_refused_with_a_clear_message(henreg, kind):
    for target in (henreg, henreg.fit):
        with pytest.raises(pyxtdpthresh.SpecificationError) as caught:
            pyxtdpthresh.plot(target, kind)
        assert caught.value.key == "plot_xthenreg" and "xtdpthresh" in str(caught.value)


def test_pyx_plot_accepts_the_public_result_of_xtdpthresh(result):
    fig = pyxtdpthresh.plot(result, "profile")
    assert fig is not None
