"""``xthenreg``: dynamic panel threshold model of Seo, Kim and Kim (2019)."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from pyxtdpthresh._types import BoolArray, FloatArray
from pyxtdpthresh.models.xthenreg.design import prepare_data
from pyxtdpthresh.models.xthenreg.estimate import estimate
from pyxtdpthresh.models.xthenreg.moments import Engine
from pyxtdpthresh.results.public import XthenregResult


def xthenreg(
    data: pd.DataFrame,
    y: str,
    x: Sequence[str] | str = (),
    *,
    q: str,
    endogenous: Sequence[str] | str = (),
    exogenous: Sequence[str] | str = (),
    inst: Sequence[str] | str = (),
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
    static: bool = False,
    kink: bool = False,
    grid_num: int = 100,
    trim_rate: float = 0.4,
    h_0: float = 1.5,
    boot_reps: int = 0,
    seed: int | None = None,
    draws: FloatArray | None = None,
    engine: Engine = "fast",
) -> XthenregResult:
    """Estimate the dynamic panel threshold model of Seo, Kim and Kim (2019).

    Parameters
    ----------
    data
        Strongly balanced long data, one row per (unit, period).
    y, x, q
        Dependent variable, regressors and threshold variable.
    endogenous, exogenous, inst
        Regressors treated as endogenous or as exogenous, and external instruments.
    id, time
        Identifier and time columns (or index level names).
    where
        Condition selecting the sample.
    static, kink
        Static model; continuous effect (kink) instead of a jump.
    grid_num, trim_rate
        Number of candidate thresholds and total trimmed share of ``q``.
    h_0
        Multiplier of the kernel bandwidth of the covariance in the jump model (Silverman's rule
        of thumb, ``h = h_0 * 1.06 * N**-0.2 * sd(q)``); ``h_0(#)`` of the Stata command.
    boot_reps
        Bootstrap replications of the linearity test; ``0`` skips the test.
    seed
        Seed of the bootstrap weights; drawn and recorded (``result.seed``) when omitted.
    draws
        Standard normal weights ``(boot_reps, N)`` to use instead of the generator.
    engine
        ``"fast"`` or ``"literal"`` moment computation.

    Returns
    -------
    XthenregResult
        Estimates, confidence intervals and the methods to print and export.

    Examples
    --------
    >>> import pyxtdpthresh as pyx
    >>> df = pyx.load_dataset("invest")
    >>> df = df[~df["firm"].isin([137, 391, 407, 488, 538])]
    >>> sk = pyx.xthenreg(df, "invest", ["cashflow", "tobin_q"], q="debt", id="firm", time="year",
    ...                   boot_reps=19, seed=3)
    >>> sk.names[:3]
    ('Lag_y_b', 'cashflow_b', 'tobin_q_b')
    >>> round(sk.gamma, 4)
    0.2226
    """
    sample = prepare_data(
        data, y, q, _names(x), _names(endogenous), _names(exogenous), _names(inst),
        id=id, time=time, where=where,
    )  # fmt: skip
    fit = estimate(
        sample, static=static, kink=kink, grid_num=grid_num, trim_rate=trim_rate,
        h_0=h_0, boot_reps=boot_reps, seed=seed, draws=draws, engine=engine,
    )  # fmt: skip
    return XthenregResult(fit)


def _names(value: Sequence[str] | str) -> Sequence[str]:
    """Return a role given as one name or as a sequence of names, as a sequence."""
    return [value] if isinstance(value, str) else value
