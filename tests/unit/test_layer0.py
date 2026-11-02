"""Tests of the layer-0 modules: options, errors and message catalogue."""

import pytest

from pyxtdpthresh import _config, _errors, _i18n


@pytest.fixture(autouse=True)
def _restore_options():
    previous = _config.get_options()
    yield
    _config.set_options(lang=previous.lang, threads=previous.threads, progress=previous.progress)


def test_default_options():
    opts = _config.get_options()
    assert opts.lang == "en"
    assert opts.threads is None
    assert opts.progress is False


def test_set_options_returns_previous_and_applies():
    previous = _config.set_options(lang="fr", threads=2)
    assert previous.lang == "en"
    assert _config.get_options().lang == "fr"
    assert _config.get_options().threads == 2


@pytest.mark.parametrize(
    "changes",
    [{"lang": "es"}, {"threads": 0}, {"threads": -3}, {"unknown": 1}],
)
def test_set_options_rejects_invalid_values(changes):
    before = _config.get_options()
    with pytest.raises(ValueError):
        _config.set_options(**changes)
    assert _config.get_options() == before


def test_option_context_restores_on_exit_and_on_error():
    with _config.option_context(lang="fr"):
        assert _config.get_options().lang == "fr"
    assert _config.get_options().lang == "en"
    with pytest.raises(RuntimeError), _config.option_context(lang="fr"):
        raise RuntimeError("boom")
    assert _config.get_options().lang == "en"


def test_error_hierarchy_and_stata_codes():
    assert issubclass(_errors.DataError, ValueError)
    assert issubclass(_errors.SpecificationError, ValueError)
    assert issubclass(_errors.NumericalError, ArithmeticError)
    assert issubclass(_errors.DataError, _errors.PyxdpthreshError)
    assert _errors.SpecificationError("x").stata_code == 198
    assert _errors.DataError("x").stata_code is None
    assert _errors.DataError("x", stata_code=498).stata_code == 498
    assert issubclass(_errors.PyxdpthreshWarning, UserWarning)


def test_message_follows_global_language_and_explicit_language():
    assert "not found" in _i18n.message("variable_not_found", name="debt")
    with _config.option_context(lang="fr"):
        assert "introuvable" in _i18n.message("variable_not_found", name="debt")
    assert "introuvable" in _i18n.message("variable_not_found", lang="fr", name="debt")


def test_message_substitutes_fields():
    assert "debt" in _i18n.message("missing_values", variables="debt")


def test_unknown_key_raises_keyerror():
    with pytest.raises(KeyError):
        _i18n.message("does_not_exist")


@pytest.mark.parametrize("key", _i18n.keys())
def test_every_message_is_translated_in_both_languages(key):
    assert _i18n.has_language(key, "en")
    assert _i18n.has_language(key, "fr")
