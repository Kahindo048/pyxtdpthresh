"""Projected memory of a fit and the warning before a large one (J.2.5)."""

import tracemalloc
import warnings

import pytest

from pyxtdpthresh import _config, simulate_panel
from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh._i18n import message
from pyxtdpthresh.models.xtdpthresh import fit as fit_module
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.fit import fit_point, projected_memory
from pyxtdpthresh.models.xtdpthresh.sample import prepare_data

KEYS = {"q": "q", "id": "id", "time": "t"}


@pytest.fixture(scope="module")
def panel():
    return simulate_panel("gong_seo", 3000, 8, seed=3)


def estimate(frame, **options):
    spec = check_specification(y="y", x=[], q="q", **options)
    return projected_memory(prepare_data(frame, spec, id="id", time="t"))


def test_the_projected_memory_follows_the_measured_peak(panel):
    tracemalloc.start()
    fit_point(panel, "y", [], bootstrap=False, **KEYS)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    assert 0.6 < estimate(panel, bootstrap=False) / peak < 1.6


def test_the_projected_memory_grows_with_the_data_and_with_the_draws(panel):
    bigger = simulate_panel("gong_seo", 6000, 8, seed=3)
    assert estimate(bigger, bootstrap=False) > 1.8 * estimate(panel, bootstrap=False)
    assert (
        estimate(panel, n_boot=999) > estimate(panel, n_boot=99) > estimate(panel, bootstrap=False)
    )


def test_a_small_fit_gives_no_memory_warning(panel):
    with warnings.catch_warnings():
        warnings.simplefilter("error", PyxdpthreshWarning)
        fit_point(panel, "y", [], bootstrap=False, **KEYS)


def test_the_note_and_the_warning_appear_at_their_thresholds(panel, monkeypatch):
    monkeypatch.setattr(fit_module, "NOTE_GB", 1e-6)
    with pytest.warns(PyxdpthreshWarning, match=r"expected to use about .* GB"):
        fit_point(panel, "y", [], bootstrap=False, **KEYS)
    monkeypatch.setattr(fit_module, "WARN_GB", 1e-5)
    with pytest.warns(PyxdpthreshWarning, match="may fail or swap"):
        fit_point(panel, "y", [], bootstrap=False, **KEYS)


def test_warn_false_silences_the_memory_warning(panel, monkeypatch):
    monkeypatch.setattr(fit_module, "NOTE_GB", 1e-6)
    monkeypatch.setattr(fit_module, "WARN_GB", 1e-5)
    with warnings.catch_warnings():
        warnings.simplefilter("error", PyxdpthreshWarning)
        fit_point(panel, "y", [], bootstrap=False, warn=False, **KEYS)


def test_the_messages_exist_in_both_languages():
    for key in ("warn_memory", "warn_memory_high"):
        assert "GB" in message(key, "en", gb="3.2") and "3.2" in message(key, "en", gb="3.2")
        assert "Go" in message(key, "fr", gb="3.2") and "3.2" in message(key, "fr", gb="3.2")
    previous = _config.set_options(lang="fr")
    try:
        assert "Go de mémoire" in message("warn_memory", gb="1.0")
    finally:
        _config.set_options(lang=previous.lang)
