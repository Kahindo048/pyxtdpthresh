"""MT19937-64 kernel, its pure Python reference and the StataRNG wrapper."""

import numpy as np
import pytest

from pyxtdpthresh.inference.bootstrap.rng import MAX_SEED, StataRNG, component_seed
from pyxtdpthresh.kernels import rng as mt64
from pyxtdpthresh.kernels.reference.rng import MT64


def test_published_mt19937_64_values():
    # std::mt19937_64 with its default seed 5489: first and 10000th outputs
    out = mt64.next_uint64(mt64.seed_state(5489), 10000)
    assert int(out[0]) == 14514284786278117030
    assert int(out[-1]) == 9981545732273789042


@pytest.mark.parametrize("seed", [0, 1, 123, 2**31 - 1, 2**40 + 5])
def test_kernel_equals_pure_python_reference_across_twists(seed):
    n = 312 * 3 + 17  # crosses two regenerations of the state
    ref = MT64(seed)
    expected = [ref.next() for _ in range(n)]
    assert mt64.next_uint64(mt64.seed_state(seed), n).tolist() == expected


def test_state_advances_in_place_so_calls_chain():
    state = mt64.seed_state(7)
    first, second = mt64.next_uint64(state, 100), mt64.next_uint64(state, 50)
    whole = mt64.next_uint64(mt64.seed_state(7), 150)
    assert np.concatenate([first, second]).tolist() == whole.tolist()


def test_seed_range():
    with pytest.raises(ValueError):
        mt64.seed_state(-1)
    with pytest.raises(ValueError):
        StataRNG(MAX_SEED + 1)
    StataRNG(0)
    StataRNG(MAX_SEED)


def test_uniform_is_in_open_unit_interval_and_never_zero():
    u = StataRNG(1).uniform(200_000)
    assert u.min() > 0.0 and u.max() < 1.0
    assert abs(u.mean() - 0.5) < 0.005


def test_shapes_and_row_major_fill():
    rng = StataRNG(5)
    flat = StataRNG(5).uniform(12)
    np.testing.assert_array_equal(rng.uniform((3, 4)), flat.reshape(3, 4))
    assert StataRNG(5).uniform().shape == ()
    assert StataRNG(5).uniform(0).shape == (0,)
    assert StataRNG(5).normal((2, 3)).shape == (2, 3)


def test_normal_is_the_inverse_cdf_of_the_uniform_stream():
    from scipy.stats import norm

    z = StataRNG(3).normal(1000)
    np.testing.assert_allclose(norm.cdf(z), StataRNG(3).uniform(1000), rtol=1e-12)
    assert abs(z.mean()) < 0.1 and abs(z.std() - 1.0) < 0.1


def test_copy_and_reseed():
    rng = StataRNG(9)
    rng.uniform(10)
    twin = rng.copy()
    np.testing.assert_array_equal(rng.uniform(5), twin.uniform(5))
    rng.reseed(9)
    np.testing.assert_array_equal(rng.uniform(3), StataRNG(9).uniform(3))


def test_component_seed_wraps_like_xtdpthresh():
    assert component_seed(100, 7) == 107
    assert component_seed(2**31 - 1, 5) == 4
