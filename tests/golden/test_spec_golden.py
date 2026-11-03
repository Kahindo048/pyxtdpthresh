"""Specification checks of ``xtdpthresh`` against the frozen Stata 17 behaviour (E.1).

For every case the same rule must fire in both programs (identified by the Stata message
fragment) with the same return code, or neither must raise.  The package's messages are its
own, so the texts are not compared.
"""

import json
import warnings

import pytest
from validation.spec_cases import ALL_CASES, FRAGMENTS, GOLDEN

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.options import make_options

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN}


def run_python(args):
    """Run the package's checks on the arguments of a case."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        check_specification(**args)


@pytest.mark.parametrize("name", list(CASES))
def test_same_rule_and_same_return_code_as_stata(name):
    case, stata = CASES[name], FROZEN[name]
    if case.key is None:
        assert stata["rc"] == 0, f"{name}: Stata refused a command that should be valid"
        run_python(case.full_args())
        return
    assert stata["rc"] != 0, f"{name}: Stata accepted a command that should fail"
    fragment = FRAGMENTS[case.key]
    if fragment is not None:
        assert fragment in stata["text"], f"{name}: Stata said {stata['text']!r}"
    with pytest.raises(SpecificationError) as raised:
        run_python(case.full_args())
    assert raised.value.key == case.key
    assert raised.value.stata_code == stata["rc"]


def test_every_case_was_frozen():
    assert set(CASES) == {c.name for c in ALL_CASES}


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_every_rule_has_a_message_in_both_languages(lang):
    from pyxtdpthresh._i18n import has_language

    assert all(has_language(key, lang) for key in FRAGMENTS)


def test_legacy_coef_boot_warns_unless_silenced():
    with pytest.warns(PyxdpthreshWarning, match="legacy"):
        make_options(coef_boot="onestep")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        make_options(coef_boot="onestep", warn=False)


def test_options_are_normalised():
    got = make_options(method=" FOD ", maxlag=(2, 8), grid_type="Quantile", collapse=True)
    assert (got.method, got.maxlag, got.grid_type, got.iv_collapse) == (
        "fod",
        (2, 8.0),
        "quantile",
        True,
    )
    assert make_options(maxlag=3).maxlag == (1, 3.0)
    assert make_options().maxlag[1] == float("inf")
