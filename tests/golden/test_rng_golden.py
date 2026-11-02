"""StataRNG against the frozen draws of Stata 17 (five seeds, 10 000 values)."""

import json

import numpy as np
import pytest
from validation.rng_cases import GOLDEN, SEEDS

from pyxtdpthresh.inference.bootstrap.rng import StataRNG

pytestmark = pytest.mark.golden
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))


def stata(seed, kind):
    return np.array(MASTER["stata"][str(seed)][kind], dtype=float)


@pytest.mark.parametrize("seed", SEEDS)
def test_uniform_stream_is_identical_bit_for_bit(seed):
    got = StataRNG(seed).uniform(2000)
    np.testing.assert_array_equal(got, stata(seed, "uniform").ravel())


@pytest.mark.parametrize("seed", SEEDS)
def test_invnormal_of_uniform_agrees_to_rounding(seed):
    got = StataRNG(seed).normal(2000)
    expected = stata(seed, "normal").ravel()
    np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("seed", SEEDS)
def test_matrix_is_filled_row_by_row_and_the_stream_continues(seed):
    rng = StataRNG(seed)
    np.testing.assert_array_equal(rng.uniform((3, 4)), stata(seed, "matrix"))
    np.testing.assert_array_equal(rng.uniform(5), stata(seed, "after").ravel())


@pytest.mark.parametrize("seed", SEEDS)
def test_row_vector_runiform_and_successive_bootstrap_blocks(seed):
    np.testing.assert_array_equal(StataRNG(seed).uniform((1, 7)), stata(seed, "row"))
    np.testing.assert_array_equal(StataRNG(seed).uniform(6), stata(seed, "runiform").ravel())
    rng = StataRNG(seed)
    for block in ("boot1", "boot2"):
        np.testing.assert_allclose(rng.normal((1, 50)), stata(seed, block), rtol=1e-12, atol=1e-12)
