"""Journal of the effective settings of an ``xtdpthresh`` fit (layer 6).

``settings_log(fit)`` lists what the estimation really did, which is not always what was asked:
the sample that remained, the instruments kept and those removed (and why), the weight the first
step fell back on, the grid actually searched, the bootstrap seed (drawn and recorded when none was
given) and the options in force.  It reads the fit and never estimates; the entries have stable
keys, so ``to_dict()`` serves a program as well as the printed report serves a reader.
"""

from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass
from typing import Any

from pyxtdpthresh._types import Lang
from pyxtdpthresh._version import __version__
from pyxtdpthresh.extras.plotting.style import resolve_lang
from pyxtdpthresh.extras.reporting.settings_log_texts import LABELS, SECTIONS, WORDS

#: The Stata command whose results the package reproduces.
REFERENCE = "xtdpthresh 0.9.38 (Stata 17)"
_DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")
_ROLES = ("x", "exogenous", "endogenous", "predetermined", "iv")


@dataclass(frozen=True)
class Entry:
    """One line of the journal.

    Attributes
    ----------
    section, key
        Section (``sample``, ``model``...) and stable key of the entry.
    label, value
        Text in the language of the journal.
    raw
        The value as a program reads it (a number, a boolean, a string or a tuple).
    """

    section: str
    key: str
    label: str
    value: str
    raw: Any


@dataclass(frozen=True)
class SettingsLog:
    """The entries of a fit, by section; prints as a report and displays in Jupyter."""

    entries: tuple[Entry, ...]
    lang: Lang

    def __iter__(self) -> Any:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, key: str) -> Any:
        """Return the raw value of the entry ``key``."""
        for entry in self.entries:
            if entry.key == key:
                return entry.raw
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        return any(entry.key == key for entry in self.entries)

    @property
    def keys(self) -> tuple[str, ...]:
        """Keys of the entries, in report order."""
        return tuple(entry.key for entry in self.entries)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Return the raw values as ``{section: {key: value}}``."""
        out: dict[str, dict[str, Any]] = {}
        for entry in self.entries:
            out.setdefault(entry.section, {})[entry.key] = entry.raw
        return out

    def _sections(self) -> list[tuple[str, list[Entry]]]:
        grouped: dict[str, list[Entry]] = {}
        for entry in self.entries:
            grouped.setdefault(entry.section, []).append(entry)
        return list(grouped.items())

    def __str__(self) -> str:
        lines = [WORDS["header"][self.lang], ""]
        for section, rows in self._sections():
            lines.append(SECTIONS[section][self.lang])
            width = max(len(row.label) for row in rows)
            lines += [f"  {row.label:<{width}}  {row.value}" for row in rows]
            lines.append("")
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        parts = [f"<p><b>{html.escape(WORDS['header'][self.lang])}</b></p>"]
        for section, rows in self._sections():
            body = "".join(
                f"<tr><td>{html.escape(r.label)}</td><td>{html.escape(r.value)}</td></tr>"
                for r in rows
            )
            parts.append(f"<p><i>{html.escape(SECTIONS[section][self.lang])}</i></p>")
            parts.append(f"<table>{body}</table>")
        return "".join(parts)


class _Builder:
    """Collects the entries of one journal in one language."""

    def __init__(self, lang: Lang) -> None:
        self.lang = lang
        self.entries: list[Entry] = []

    def word(self, key: str) -> str:
        return WORDS[key][self.lang]

    def yes_no(self, flag: bool) -> str:
        return self.word("yes" if flag else "no")

    def add(self, section: str, key: str, raw: Any, value: str | None = None) -> None:
        text = str(raw) if value is None else value
        if self.lang == "fr" and section != "software":  # version numbers keep their points
            text = _DECIMAL.sub(",", text)
        self.entries.append(Entry(section, key, LABELS[key][self.lang], text, raw))

    def flag(self, section: str, key: str, flag: bool) -> None:
        self.add(section, key, bool(flag), self.yes_no(bool(flag)))

    def choice(self, section: str, key: str, raw: str) -> None:
        self.add(section, key, raw, self.word(raw))


def _number(value: float) -> str:
    return "-" if not math.isfinite(value) else f"{value:.6g}"


def _sample(fit: Any, out: _Builder) -> None:
    out.add("sample", "n_units", int(fit.n_units))
    out.add("sample", "n_equations", int(fit.n_obs))
    out.add("sample", "n_units_dropped", int(fit.data.n_units_dropped))
    out.choice("sample", "history", fit.spec.options.history)


def _model(fit: Any, out: _Builder) -> None:
    opts, spec = fit.spec.options, fit.spec
    out.choice("model", "method", opts.method)
    out.choice("model", "shape", "kink" if fit.stack.kink else "jump")
    out.choice("model", "dynamics", "static" if opts.static else "dynamic")
    out.flag("model", "time_effects", opts.time_effects)
    out.add("model", "threshold_variable", spec.q)
    for role in _ROLES:
        names = tuple(term.raw for term in getattr(spec, role))
        if names:
            out.add("model", role, names, ", ".join(names))


def _instruments(fit: Any, out: _Builder) -> None:
    opts, cleaned = fit.spec.options, fit.stack.instruments
    out.add("instruments", "n_instruments", int(fit.n_instruments))
    out.flag("instruments", "collapse", opts.collapse)
    out.flag("instruments", "iv_collapse", opts.collapse or opts.iv_collapse)
    low, high = opts.maxlag
    unlimited = math.isinf(high)
    span = f"{int(low)} {out.word('to')} {out.word('unlimited') if unlimited else int(high)}"
    out.add("instruments", "maxlag", (low, high), span)
    for key, count in (
        ("removed_common", cleaned.n_common),
        ("removed_zero", cleaned.n_zero),
        ("removed_duplicate", cleaned.n_duplicate),
        ("removed_dependent", cleaned.n_dependent),
    ):
        out.add("instruments", key, int(count))
    if cleaned.n_dependent:
        out.add(
            "instruments", "dependent_residual", float(cleaned.dep_res), _number(cleaned.dep_res)
        )
    out.choice("instruments", "first_weight", f"weight_{int(fit.stack.first_weight.fallback)}")
    out.choice("instruments", "estimator", "twostep" if fit.search.fit.twostep else "onestep")


def _search(fit: Any, out: _Builder) -> None:
    opts, search = fit.spec.options, fit.search
    out.choice("search", "grid_type", opts.grid_type)
    out.add("search", "grid_requested", int(search.grid_requested))
    out.add("search", "grid_effective", int(search.grid_effective))
    out.add("search", "grid_admitted", int(search.grid_admitted))
    bounds = (float(search.q_lo), float(search.q_hi))
    out.add("search", "q_range", bounds, f"[{_number(bounds[0])}, {_number(bounds[1])}]")
    out.add("search", "trim", float(opts.trim))
    out.add("search", "min_regime", int(search.min_regime))
    if fit.stack.kink:
        out.flag("search", "kink_refined", bool(search.kink_refined))


def _inference(fit: Any, out: _Builder) -> None:
    opts, boot = fit.spec.options, fit.bootstrap
    out.add("inference", "vce", opts.vce)
    out.flag("inference", "joint_vce", bool(fit.variance.joint))
    if math.isfinite(fit.variance.bandwidth):
        out.add(
            "inference", "bandwidth", float(fit.variance.bandwidth), _number(fit.variance.bandwidth)
        )
    out.add("inference", "level", float(opts.level), f"{opts.level:g}")
    out.flag("inference", "bootstrap", boot is not None)
    if boot is None:
        return
    out.choice("inference", "boot_type", opts.boot_type)
    out.add("inference", "n_boot", int(opts.n_boot))
    out.add("inference", "seed", boot.seed, None if boot.seed is not None else out.word("unset"))
    out.add("inference", "grid_ci", int(opts.grid_ci))
    if boot.ci is not None:
        out.add("inference", "ci_unresolved", int(boot.ci.n_unresolved))


def settings_log(fit: Any, lang: Lang | None = None) -> SettingsLog:
    """Return the journal of the effective settings of an ``xtdpthresh`` fit.

    Parameters
    ----------
    fit
        Result of an ``xtdpthresh`` estimation.
    lang : {"en", "fr"}, optional
        Language of the journal (default: the global ``lang`` option).

    Returns
    -------
    SettingsLog
        The entries by section; ``print(journal)`` shows the report, ``journal["seed"]`` and
        ``journal.to_dict()`` give the values.
    """
    chosen = resolve_lang(lang)
    out = _Builder(chosen)
    for step in (_sample, _model, _instruments, _search, _inference):
        step(fit, out)
    out.add("software", "package", f"pyxtdpthresh {__version__}")
    out.add("software", "reference", REFERENCE)
    return SettingsLog(tuple(out.entries), chosen)
