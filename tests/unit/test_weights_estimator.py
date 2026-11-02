"""Weights and helpers of the xthenreg estimator."""

import numpy as np

from pyxtdpthresh.core.linalg import invsym
from pyxtdpthresh.core.weights import ma1_weight, second_step_weight
from pyxtdpthresh.models.xthenreg.estimator import first_minimum


def test_ma1_weight_inverts_the_block_tridiagonal_matrix():
    rng = np.random.default_rng(0)
    n = 200
    blocks = [rng.standard_normal((n, m)) for m in (2, 3, 4)]
    w = ma1_weight(blocks)
    starts = np.cumsum([0, 2, 3, 4])
    expected = np.zeros((9, 9))
    for p, b in enumerate(blocks):
        sl = slice(starts[p], starts[p + 1])
        expected[sl, sl] = 2.0 * b.T @ b / n
        if p:
            prev = slice(starts[p - 1], starts[p])
            cross = -blocks[p - 1].T @ b / n
            expected[prev, sl] = cross
            expected[sl, prev] = cross.T
    np.testing.assert_allclose(w @ expected, np.eye(9), atol=1e-8)
    np.testing.assert_allclose(w, w.T, atol=1e-12)


def test_second_step_weight_is_the_inverse_of_the_centred_covariance():
    g = np.random.default_rng(1).standard_normal((300, 5)) + 2.0
    np.testing.assert_allclose(
        second_step_weight(g), invsym(np.cov(g.T, bias=True)), rtol=1e-9, atol=1e-12
    )


def test_first_minimum_takes_the_first_tie_and_ignores_missing():
    assert first_minimum(np.array([3.0, 1.0, 2.0, 1.0])) == 1
    assert first_minimum(np.array([np.nan, 5.0, 4.0])) == 2
