"""User-facing result classes (layer 7): a container plus methods delegating to extras.

``XtdpthreshResult`` and ``XthenregResult`` wrap the frozen container of the model layer
(``result.fit``) and add nothing to it: every method calls the tool of ``extras/`` that was
validated on its own, so the numbers of ``result.params`` or ``result.scalars`` are those of
``fit_point`` and ``estimate``.  The heavy modules (tables, plots) are imported when a method
runs, so ``import pyxtdpthresh`` stays light.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from pyxtdpthresh._types import BoolArray, FloatArray, Lang

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from pyxtdpthresh.extras.reporting import Diagnosis, SettingsLog, ThresholdStargazer
    from pyxtdpthresh.models.xtdpthresh.fit import PointFit
    from pyxtdpthresh.results.containers import XthenregFit

#: Digits of the numbers in the extra lines of ``full_output=True``.
_SCALAR_DIGITS = 4


def _standard_errors(cov: FloatArray) -> FloatArray:
    """Return the standard errors of a covariance matrix (``nan`` where a variance is negative)."""
    diag = np.diag(cov)
    return np.asarray(np.where(diag >= 0, np.sqrt(np.clip(diag, 0.0, None)), np.nan))


def _scalar_text(value: float) -> str:
    """Write a scalar of ``e()`` as it appears under a table."""
    if value == int(value) and abs(value) < 1e9:
        return str(int(value))
    return f"{value:.{_SCALAR_DIGITS}g}"


class _Result:
    """What the two result classes share: coefficients, text, tables and records."""

    #: Read by the table extractor to look through the wrapper.
    is_public_result = True

    fit: Any
    _names: tuple[str, ...]
    _theta: FloatArray
    _when: datetime

    # ------------------------------------------------------------------------------ numbers
    @property
    def params(self) -> pd.Series:
        """Estimated coefficients, indexed by their names (``e(b)``)."""
        return pd.Series(self._theta, index=list(self._names), name="params", dtype=float)

    @property
    def cov(self) -> pd.DataFrame:
        """Covariance matrix of the coefficients that is reported (``e(V)``)."""
        names = list(self._names)
        return pd.DataFrame(np.asarray(self.fit.cov), index=names, columns=names)

    @property
    def se(self) -> pd.Series:
        """Standard errors of the coefficients."""
        values = _standard_errors(np.asarray(self.fit.cov))
        return pd.Series(values, index=list(self._names), name="se", dtype=float)

    @property
    def gamma(self) -> float:
        """Estimated threshold."""
        raise NotImplementedError

    @property
    def gamma_ci(self) -> tuple[float, float] | None:
        """Interval of the threshold (hull of the confidence set), ``None`` when not available."""
        from pyxtdpthresh.extras.reporting.extract import extract

        interval = extract(self.fit).stats.get("gamma_ci")
        return interval if isinstance(interval, tuple) else None

    @property
    def seed(self) -> int | None:
        """Seed of the bootstrap draws, given or drawn (``None`` without bootstrap)."""
        raise NotImplementedError

    @property
    def scalars(self) -> dict[str, float]:
        """Scalars of the fit under the names of Stata's ``e()``."""
        raise NotImplementedError

    # ---------------------------------------------------------------------------------- text
    def summary(self, *, level: float = 95.0, lang: Lang | None = None, digits: int = 4) -> str:
        """Report in the layout of ``pyxtabond2`` and ``pyxthreg``, 80 columns wide.

        The header (sample, model, options), the threshold with its interval, the threshold-effect
        test with its bootstrap critical values, the slopes of the three regimes and the
        diagnostic tests.  The date and time are those of the estimation, so printing the result
        twice gives the same text.
        """
        from pyxtdpthresh.extras.reporting import summary

        return summary(self.fit, level=level, lang=lang, digits=digits, when=self._when)

    def __str__(self) -> str:
        return self.summary()

    def __repr__(self) -> str:
        return self.summary()

    def _repr_html_(self) -> str:
        return self.table()._repr_html_()

    def _repr_latex_(self) -> str:
        return self.table()._repr_latex_()

    # ------------------------------------------------------------------------------- records
    def to_dataframe(self, level: float = 95.0) -> pd.DataFrame:
        """Coefficients as a frame indexed by ``(block, variable)``, with the threshold last."""
        from pyxtdpthresh.extras.reporting import to_dataframe

        return to_dataframe(self.fit, level)

    def to_json(self, path: str | Path | None = None, *, level: float = 95.0) -> str:
        """Reproducible record of the fit (versions, options, seed, estimates) as JSON."""
        from pyxtdpthresh.extras.reporting import to_json

        return to_json(self.fit, path, level=level)

    # ------------------------------------------------------------------------------- tables
    def table(self, *, full_output: bool = False, **options: Any) -> ThresholdStargazer:
        """Table of this model alone, to be written in any format.

        Parameters
        ----------
        full_output
            ``False`` (default): the academic table, the three blocks of slopes and the
            diagnostic lines.  ``True``: the same followed by one line per scalar of ``e()``
            the fit has.
        **options
            Options of :class:`~pyxtdpthresh.extras.reporting.ThresholdStargazer`
            (``statistic``, ``digits``, ``covariate_labels``, ``title``, ``lang``...).
        """
        from pyxtdpthresh.extras.reporting import ThresholdStargazer

        if full_output:
            lines = [
                (name, [_scalar_text(v)]) for name, v in self.scalars.items() if math.isfinite(v)
            ]
            options["add_lines"] = [*options.get("add_lines", ()), *lines]
        return ThresholdStargazer([self.fit], **options)

    def to_latex(self, path: str | Path | None = None, **options: Any) -> str:
        """LaTeX table (``full_output`` and the options of :meth:`table`)."""
        return self.table(**options).to_latex(path)

    def to_html(self, path: str | Path | None = None, **options: Any) -> str:
        """HTML table."""
        return self.table(**options).to_html(path)

    def to_markdown(self, path: str | Path | None = None, **options: Any) -> str:
        """Markdown table."""
        return self.table(**options).to_markdown(path)

    def to_text(self, path: str | Path | None = None, **options: Any) -> str:
        """Plain-text table."""
        return self.table(**options).to_text(path)

    def to_csv(self, path: str | Path | None = None, **options: Any) -> str:
        """CSV table."""
        return self.table(**options).to_csv(path)

    def to_word(self, path: str | Path, **options: Any) -> Path:
        """Word table (needs ``python-docx``)."""
        return self.table(**options).to_word(path)

    def to_excel(self, path: str | Path, **options: Any) -> Path:
        """Excel table (needs ``openpyxl``)."""
        return self.table(**options).to_excel(path)


class XtdpthreshResult(_Result):
    """Result of :func:`pyxtdpthresh.xtdpthresh`.

    Attributes
    ----------
    fit
        The frozen :class:`~pyxtdpthresh.models.xtdpthresh.fit.PointFit` (everything the
        estimator computed).
    """

    def __init__(self, fit: PointFit) -> None:
        self.fit = fit
        self._when = datetime.now()
        self._names = fit.names
        self._theta = np.asarray(fit.search.fit.theta, dtype=np.float64)

    @property
    def names(self) -> tuple[str, ...]:
        """Coefficient names, ``lower:x``, ``change:_cons`` and ``change:x``."""
        return self._names

    @property
    def gamma(self) -> float:
        """Estimated threshold."""
        return float(self.fit.search.fit.gamma)

    @property
    def scalars(self) -> dict[str, float]:
        """Scalars of the fit under the names of Stata's ``e()`` (``nan`` when missing)."""
        return self.fit.scalars

    @property
    def seed(self) -> int | None:
        """Seed of the bootstrap draws (the one given, or the one drawn and recorded)."""
        return self.fit.spec.options.seed

    @property
    def n_obs(self) -> int:
        """Stacked equations (``e(N)``)."""
        return self.fit.n_obs

    @property
    def n_units(self) -> int:
        """Units that contribute equations (``e(N_units)``)."""
        return self.fit.n_units

    @property
    def n_instruments(self) -> int:
        """Instruments after cleaning (``e(N_iv)``)."""
        return self.fit.n_instruments

    @property
    def upper(self) -> pd.DataFrame | None:
        """Slopes of the upper regime and their standard errors (``e(b_upper)``, ``e(V_upper)``).

        Under ``kink`` it holds only the slope of ``q`` above the threshold, and is ``None`` when
        ``q`` is not a regressor.
        """
        regime = self.fit.upper
        if regime is None:
            return None
        se = _standard_errors(np.asarray(regime.cov))
        return pd.DataFrame({"params": np.asarray(regime.b), "se": se}, index=list(regime.names))

    # ------------------------------------------------------------------------------- reports
    def diagnose(self, lang: Lang | None = None) -> Diagnosis:
        """Plain-language report of what in the estimation deserves attention.

        Parameters
        ----------
        lang : {"en", "fr"}, optional
            Language of the report (default: the global ``lang`` option).

        Returns
        -------
        Diagnosis
            The alerts, warnings first; ``print(result.diagnose())`` shows the report.
        """
        from pyxtdpthresh.extras.reporting import diagnose

        return diagnose(self.fit, lang)

    def settings_log(self, lang: Lang | None = None) -> SettingsLog:
        """Journal of the settings the estimation really used (sample, instruments, seed).

        Parameters
        ----------
        lang : {"en", "fr"}, optional
            Language of the journal (default: the global ``lang`` option).

        Returns
        -------
        SettingsLog
            The settings that were applied, which can differ from those requested.
        """
        from pyxtdpthresh.extras.reporting import settings_log

        return settings_log(self.fit, lang)

    def ci_table(self) -> pd.DataFrame:
        """Inversion of the grid bootstrap: one row per candidate threshold.

        Returns
        -------
        pandas.DataFrame
            Columns ``gamma``, ``statistic``, ``critical``, ``accepted`` (1 when the candidate is
            in the confidence set), ``n_valid`` and ``status``; this is ``e(ci_grid)``.  It needs
            the bootstrap (a ``DataError`` otherwise).
        """
        from pyxtdpthresh.extras.reporting import ci_table

        return ci_table(self.fit)

    def regime_table(self) -> pd.DataFrame:
        """Size of each regime and the mean of the variables in it.

        Returns
        -------
        pandas.DataFrame
            Rows ``lower`` and ``upper``; columns ``observations``, ``units``, ``share`` (percent
            of the equations) and the mean of the dependent variable, of the regressors and of the
            threshold variable in the regime.
        """
        from pyxtdpthresh.extras.reporting import regime_table

        return regime_table(self.fit)

    def plot(
        self, kind: str, *, lang: Lang | None = None, path: str | Path | None = None, **options: Any
    ) -> Figure:
        """Draw the graph ``kind`` (see :data:`pyxtdpthresh.extras.plotting.PLOT_KINDS`).

        Parameters
        ----------
        kind
            One of ``"profile"``, ``"ci"``, ``"linearity"``, ``"coef"``, ``"regimes"``,
            ``"effect"``, ``"switch"``, ``"instruments"`` and ``"residuals"``.
        lang : {"en", "fr"}, optional
            Language of the texts of the figure (default: the global ``lang`` option).
        path
            File to write (``.png``, ``.pdf`` or ``.svg``) in addition to returning the figure.
        **options
            Options of the graph: ``var`` for ``"effect"``, ``variables`` for ``"coef"``, ``bins``
            for ``"regimes"``.

        Returns
        -------
        matplotlib.figure.Figure
            The figure, in the common style of the package.
        """
        from pyxtdpthresh.extras.plotting import plot

        return plot(self.fit, kind, lang=lang, path=path, **options)

    # ------------------------------------------------------------------------------ the data
    def predict(
        self,
        kind: str,
        frame: pd.DataFrame,
        *,
        where: str | Sequence[bool] | BoolArray | None = None,
    ) -> pd.Series:
        """``"residuals"``, ``"xb"``, ``"ar_residuals"`` or ``"regime"`` for the estimation data.

        Parameters
        ----------
        kind
            ``"residuals"`` and ``"xb"`` are those of the estimated (transformed) equation,
            ``"ar_residuals"`` the first-difference residuals of the AR tests, ``"regime"`` is
            ``1`` above the threshold and ``0`` below.
        frame
            The data the model was estimated on (same keys).
        where
            Condition selecting the rows (Stata ``if``): an expression evaluated on the data
            (``pandas.DataFrame.eval``) or a boolean mask.

        Returns
        -------
        pandas.Series
            Aligned with ``frame``; missing where the series is not defined.
        """
        return self.fit.predict(kind, frame, where=where)

    def augment(
        self,
        frame: pd.DataFrame,
        *,
        kinds: Sequence[str] = ("residuals", "xb", "regime"),
        prefix: str = "",
        overwrite: bool = False,
    ) -> pd.DataFrame:
        """Copy of ``frame`` with the residuals, the fitted values and the regime as columns.

        Parameters
        ----------
        frame
            The data the model was estimated on (same keys); it is not modified.
        kinds
            Series to add among ``"residuals"``, ``"xb"``, ``"ar_residuals"`` and ``"regime"``.
        prefix
            Text put before the column names (``prefix="m1_"`` gives ``m1_residuals``).
        overwrite
            Replace a column that already has the name of a series; by default that is an error.

        Returns
        -------
        pandas.DataFrame
            ``frame`` and the new columns.
        """
        from pyxtdpthresh.extras.augment import augment

        return augment(self.fit, frame, kinds=kinds, prefix=prefix, overwrite=overwrite)


class XthenregResult(_Result):
    """Result of :func:`pyxtdpthresh.xthenreg`.

    Attributes
    ----------
    fit
        The frozen :class:`~pyxtdpthresh.results.containers.XthenregFit` (``e()`` of the
        Stata command, the grid and the criterion).
    """

    def __init__(self, fit: XthenregFit) -> None:
        self.fit = fit
        self._when = datetime.now()
        self._names = fit.names or tuple(f"b{i}" for i in range(fit.coef.size))
        self._theta = np.asarray(fit.coef, dtype=np.float64)

    @property
    def names(self) -> tuple[str, ...]:
        """Coefficient names as ``xthenreg`` writes them (``Lag_y_b``, ``x_d``, ``r``...)."""
        return self._names

    @property
    def gamma(self) -> float:
        """Estimated threshold (last coefficient)."""
        return float(self.fit.gamma)

    @property
    def ci(self) -> pd.DataFrame:
        """``e(CI)``: lower and upper limits of every coefficient, the threshold last."""
        return pd.DataFrame(
            np.asarray(self.fit.ci), index=list(self._names), columns=["lower", "upper"]
        )

    @property
    def seed(self) -> int | None:
        """Seed of the bootstrap weights (given or drawn); ``None`` without bootstrap."""
        return self.fit.seed

    @property
    def n_units(self) -> int:
        """Units in the sample (``e(N)``)."""
        return self.fit.n_units

    @property
    def scalars(self) -> dict[str, float]:
        """Scalars of the fit under the names of Stata's ``e()`` (``nan`` when missing)."""
        fit = self.fit
        values = {
            "N": fit.n_units, "T": fit.n_periods, "boots_p": fit.boots_p, "grid": fit.grid_num,
            "trim": fit.trim_rate, "bs": fit.boot_reps, "gamma": fit.gamma, "L": fit.n_moments,
            "sup_wald": fit.sup_wald, "bandwidth": fit.bandwidth,
        }  # fmt: skip
        return {name: float(value) for name, value in values.items()}
