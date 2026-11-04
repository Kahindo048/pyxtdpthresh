"""Journal of effective settings (I.6.5): every entry is read from the fit, none is invented."""

import math
import warnings
from dataclasses import replace

import numpy as np
import pytest
from test_search import simulate

from pyxtdpthresh import __version__
from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.core.weights import FirstStepWeight
from pyxtdpthresh.extras.reporting import SettingsLog, settings_log
from pyxtdpthresh.extras.reporting.settings_log_texts import LABELS, SECTIONS, WORDS
from pyxtdpthresh.models.xtdpthresh.fit import fit_point


def fit(df=None, regressors=("x",), **options):
    df = simulate(n=300, t=7, seed=4) if df is None else df
    options = {"collapse": True, "grid": 25, "grid_ci": 25, "seed": 3, "n_boot": 49, **options}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(df, "y", regressors, q="q", id="id", time="t", **options)


@pytest.fixture(scope="module")
def base():
    return fit()


# -------------------------------------------------------------------------------- structure
def test_every_entry_has_a_label_and_a_section_in_both_languages():
    for key, texts in LABELS.items():
        assert set(texts) == {"en", "fr"}, key
    for table in (SECTIONS, WORDS):
        for key, texts in table.items():
            assert set(texts) == {"en", "fr"}, key


def test_the_entries_come_in_the_order_of_their_sections(base):
    journal = settings_log(base)
    order = [entry.section for entry in journal]
    assert order == sorted(order, key=list(SECTIONS).index)
    assert set(order) == set(SECTIONS)
    assert len(journal) == len(journal.keys) and "seed" in journal and "nope" not in journal


def test_the_raw_values_are_the_fit_and_the_options(base):
    journal = settings_log(base)
    scalars = base.scalars
    assert journal["n_units"] == scalars["N_units"] and journal["n_equations"] == scalars["N"]
    assert journal["n_instruments"] == scalars["N_iv"]
    assert journal["grid_admitted"] == scalars["grid_admitted"]
    assert journal["q_range"] == (scalars["q_lo"], scalars["q_hi"])
    assert journal["level"] == 95.0 and journal["trim"] == 0.10
    assert journal["method"] == "fd" and journal["shape"] == "jump"
    assert journal["dynamics"] == "dynamic" and journal["collapse"] is True
    assert journal["maxlag"] == (1, math.inf)
    assert journal["threshold_variable"] == "q" and journal["x"] == ("x",)
    assert journal["estimator"] == "twostep" and journal["first_weight"] == "weight_0"
    assert journal["n_boot"] == 49 and journal["boot_type"] == "wild"
    assert journal["grid_ci"] == 25 and journal["bootstrap"] is True
    assert journal["package"] == f"pyxtdpthresh {__version__}"


def test_to_dict_groups_the_raw_values_by_section(base):
    out = settings_log(base).to_dict()
    assert set(out) == set(SECTIONS)
    assert out["instruments"]["removed_dependent"] == 0
    assert out["search"]["grid_requested"] == 25 and out["inference"]["seed"] == 3


# ----------------------------------------------------------------------------- the seed
def test_a_given_seed_is_the_seed_of_the_run(base):
    journal = settings_log(base)
    assert journal["seed"] == 3
    entry = next(e for e in journal if e.key == "seed")
    assert entry.value == "3"


def test_a_missing_seed_is_reported_as_not_reproducible():
    unseeded = fit(seed=None)
    journal = settings_log(unseeded)
    assert journal["seed"] is None
    entry = next(e for e in journal if e.key == "seed")
    assert "not set" in entry.value and "cannot be repeated" in entry.value
    french = next(e for e in settings_log(unseeded, "fr") if e.key == "seed")
    assert "non fixée" in french.value and "reproductible" in french.value


# ------------------------------------------------------------------------ what was removed
def test_the_instruments_removed_are_counted_by_reason():
    """A regressor that repeats another is removed as a dependent instrument column."""
    df = simulate(n=300, t=7, seed=4)
    df["x2"] = 2.0 * df["x"]
    journal = settings_log(fit(df, regressors=("x",), iv=("x2",)))
    removed = {
        k: journal[k]
        for k in ("removed_common", "removed_zero", "removed_duplicate", "removed_dependent")
    }
    assert all(isinstance(v, int) and v >= 0 for v in removed.values())
    assert journal["iv"] == ("x2",)
    if removed["removed_dependent"]:
        assert "dependent_residual" in journal
    else:
        assert "dependent_residual" not in journal


def test_the_removal_counts_equal_the_cleaning_of_the_fit(base):
    cleaned = base.stack.instruments
    journal = settings_log(base)
    assert journal["removed_common"] == cleaned.n_common
    assert journal["removed_zero"] == cleaned.n_zero
    assert journal["removed_duplicate"] == cleaned.n_duplicate
    assert journal["removed_dependent"] == cleaned.n_dependent


def test_a_dependent_column_adds_its_residual(base):
    stack = replace(
        base.stack, instruments=replace(base.stack.instruments, n_dependent=2, dep_res=3e-13)
    )
    journal = settings_log(replace(base, stack=stack))
    assert journal["removed_dependent"] == 2 and journal["dependent_residual"] == 3e-13


def test_the_weight_fallback_is_named(base):
    for fallback in (1, 2):
        stack = replace(
            base.stack, first_weight=FirstStepWeight(base.stack.first_weight.weight, fallback)
        )
        journal = settings_log(replace(base, stack=stack))
        assert journal["first_weight"] == f"weight_{fallback}"
    text = next(e for e in settings_log(replace(base, stack=stack)) if e.key == "first_weight")
    assert "identity" in text.value


# ---------------------------------------------------------------------------- the variants
def test_fod_kink_static_and_time_effects_are_recorded():
    journal = settings_log(fit(method="fod", kink=True, time_effects=True, bootstrap=False))
    assert journal["method"] == "fod" and journal["shape"] == "kink"
    assert journal["time_effects"] is True and "kink_refined" in journal
    assert journal["bootstrap"] is False and "seed" not in journal and "n_boot" not in journal
    static = settings_log(fit(static=True, bootstrap=False, collapse=False))
    assert static["dynamics"] == "static"


def test_the_maxlag_text_names_an_unlimited_depth(base):
    entry = next(e for e in settings_log(base) if e.key == "maxlag")
    assert entry.value == "1 to unlimited"
    limited = next(e for e in settings_log(fit(maxlag=(2, 5))) if e.key == "maxlag")
    assert limited.value == "2 to 5"
    french = next(e for e in settings_log(fit(maxlag=(2, 5)), "fr") if e.key == "maxlag")
    assert french.value == "2 à 5"


def test_the_roles_of_the_variables_are_listed():
    df = simulate(n=300, t=7, seed=4)
    df["e"] = df["x"] + 0.5 * df["q"]
    journal = settings_log(fit(df, regressors=("x",), endogenous=("e",)))
    assert journal["x"] == ("x",) and journal["endogenous"] == ("e",)
    assert "predetermined" not in journal and "exogenous" not in journal


# ----------------------------------------------------------------------------- the report
def test_the_report_lists_sections_labels_and_values(base):
    text = str(settings_log(base))
    assert text.startswith("Settings journal")
    for title in SECTIONS.values():
        assert title["en"] in text
    assert "instruments kept" in text and "first differences" in text
    assert "pyxtdpthresh" in text and "xtdpthresh 0.9.38" in text


def test_the_french_report_has_decimal_commas_but_keeps_version_numbers(base):
    journal = settings_log(base, "fr")
    text = str(journal)
    assert text.startswith("Journal des réglages") and "différences premières" in text
    trim = next(e for e in journal if e.key == "trim")
    assert trim.value == "0,1" and trim.raw == 0.1
    assert f"pyxtdpthresh {__version__}" in text and "0.9.38" in text
    low, high = base.search.q_lo, base.search.q_hi
    assert "[" in next(e for e in journal if e.key == "q_range").value
    assert "." not in next(e for e in journal if e.key == "level").value
    assert not np.isnan(low) and not np.isnan(high)


def test_the_html_display_is_escaped_and_complete(base):
    page = settings_log(base)._repr_html_()
    assert page.count("<table>") == len(SECTIONS) and "<i>Sample</i>" in page
    assert "Settings journal" in page
    assert "(Z&#x27;Z)" in page and "Z'Z" not in page  # the apostrophe of the weight is escaped
    assert "<script" not in page and page.startswith("<p><b>")


def test_the_journal_does_not_change_the_fit(base):
    before = (base.search.fit.gamma, base.search.fit.theta.copy())
    settings_log(base)
    settings_log(base, "fr")
    assert base.search.fit.gamma == before[0]
    np.testing.assert_array_equal(base.search.fit.theta, before[1])


def test_the_type_is_exported_with_the_function(base):
    assert isinstance(settings_log(base), SettingsLog)
