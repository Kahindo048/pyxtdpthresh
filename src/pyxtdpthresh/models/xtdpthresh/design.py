"""Specification of an ``xtdpthresh`` model: the variables, their roles and the checks.

The checks follow the order of the Stata command, so that when a call breaks several rules the
first one reported is the same.  Variables are named with strings (``"x"``, ``"L2.x"``) or with
:func:`~pyxtdpthresh.data.operators.lag` and its companions; the resulting
:class:`Specification` holds canonical :class:`~pyxtdpthresh.data.operators.Term` objects.
Two terms are the same variable when their canonical spellings are equal (``"x"`` and
``"L0.x"`` are).
"""

from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh.data.operators import Term, parse_term, parse_terms
from pyxtdpthresh.models.xtdpthresh.options import (
    XtdpthreshOptions,
    check_time_effects,
    make_options,
)

TermLike = str | Term
TermList = TermLike | Sequence[TermLike] | None
Roles = Mapping[str, Sequence[Term]]

#: Pairs of roles that may not share a variable, in the order Stata tests them.
_OVERLAPS = (
    ("endogenous", "x", "spec_overlap_endog_x"),
    ("endogenous", "exogenous", "spec_overlap_endog_exog"),
    ("x", "exogenous", "spec_overlap_x_exog"),
    ("predetermined", "x", "spec_overlap_predet_x"),
    ("predetermined", "exogenous", "spec_overlap_predet_exog"),
    ("predetermined", "endogenous", "spec_overlap_predet_endog"),
)
#: Roles in the order Stata scans them for duplicates and for the term guards.
_ROLE_ORDER = ("x", "exogenous", "endogenous", "predetermined", "iv")


@dataclass(frozen=True)
class Specification:
    """A validated specification.

    Attributes
    ----------
    y, q
        Dependent variable and threshold variable.
    x, exogenous, endogenous, predetermined, iv
        Terms of each role, in the order given (ranges expanded).
    options
        The validated options.
    """

    y: str
    q: str
    x: tuple[Term, ...]
    exogenous: tuple[Term, ...]
    endogenous: tuple[Term, ...]
    predetermined: tuple[Term, ...]
    iv: tuple[Term, ...]
    options: XtdpthreshOptions

    @property
    def lag_of_y(self) -> Term | None:
        """The lag of ``y`` the dynamic model adds as its first regressor (``None`` if static)."""
        return None if self.options.static else Term(self.y, shift=1, raw=f"L.{self.y}")


def _as_list(value: TermList) -> list[TermLike]:
    """Return a role, given as one name, one term or a sequence, as a list."""
    if value is None:
        return []
    if isinstance(value, str | Term):
        return [value]
    return list(value)


def _fail(key: str, **fields: Any) -> SpecificationError:
    return SpecificationError(message(key, **fields), stata_code=198, key=key)


def _names(terms: Sequence[Term]) -> list[str]:
    return [t.name for t in terms]


def _common(first: Sequence[Term], second: Sequence[Term]) -> list[str]:
    """Names of ``first`` that are also in ``second`` (Stata ``list a & b``), once each."""
    other = set(_names(second))
    found: list[str] = []
    for name in _names(first):
        if name in other and name not in found:
            found.append(name)
    return found


# ------------------------------------------------------------------------- role checks
def check_overlaps(roles: Roles) -> None:
    """Refuse a variable that has two roles, and an instrument that is also declared."""
    # Stata: xtdpthresh.ado:502-545
    for first, second, key in _OVERLAPS:
        shared = _common(roles[first], roles[second])
        if shared:
            raise _fail(key, names=", ".join(shared))
    declared = [*roles["endogenous"], *roles["predetermined"]]
    clash = _common(roles["iv"], declared)
    if clash:
        raise _fail("spec_iv_declared", names=", ".join(clash))


def check_static_not_empty(y: str, roles: Roles, static: bool) -> None:
    """Require at least one regressor or external instrument in a static model."""
    # Stata: xtdpthresh.ado:558-562
    if static and not any(roles[name] for name in _ROLE_ORDER):
        raise _fail("spec_static_empty", y=y)


def check_continuity_test(q: str, roles: Roles, options: XtdpthreshOptions) -> None:
    """``continuity_test`` needs the jump model with ``q`` among the regressors."""
    # Stata: xtdpthresh.ado:751-766
    if not options.continuity_test:
        return
    if options.kink:
        raise _fail("spec_conttest_kink")
    regressors = [*roles["x"], *roles["exogenous"], *roles["endogenous"], *roles["predetermined"]]
    if q not in _names(regressors):
        raise _fail("spec_conttest_q", q=q)


def check_duplicates(roles: Roles) -> None:
    """Refuse a variable listed twice in one role (after lag expansion)."""
    # Stata: xtdpthresh.ado:768-784
    for role in _ROLE_ORDER:
        names = _names(roles[role])
        repeated = sorted({n for n in names if names.count(n) > 1}, key=names.index)
        if repeated:
            raise _fail("spec_duplicates", role=role, names=", ".join(repeated))


def check_depvar_and_q(y: str, q: str, roles: Roles) -> None:
    """``y`` is not its own regressor or instrument, and not the threshold variable."""
    # Stata: xtdpthresh.ado:786-801
    if any(y in _names(roles[role]) for role in _ROLE_ORDER):
        raise _fail("spec_depvar_in_rhs", y=y)
    if q == y:
        raise _fail("spec_q_is_depvar", y=y)


def check_auto_lag(y: str, roles: Roles, static: bool) -> None:
    """Refuse a regressor that is the lag of ``y`` the dynamic model adds by itself."""
    # Stata: xtdpthresh.ado:803-866 (any pure L/F chain of net lag 1, e.g. l1.y, FL2.y, L2F.y)
    if static:
        return
    for role in ("x", "endogenous", "predetermined", "exogenous"):
        for term in roles[role]:
            if term.base == y and term.shift == 1 and not term.diff and not term.seasonal:
                raise _fail("spec_auto_lag_y", y=y, term=term.name)


def _declared_timing(roles: Roles) -> list[tuple[str, int, bool]]:
    """Return ``(base, smallest lag, is endogenous)`` for each endogenous or predetermined term."""
    declared = []
    for role in ("endogenous", "predetermined"):
        for term in roles[role]:
            lag_ = min(term.netlag, 0) if term.has_dsf else term.netlag
            declared.append((term.base, lag_, role == "endogenous"))
    return declared


def _check_depvar_term(y: str, role: str, term: Term) -> None:
    """Guard (a): operated terms of ``y`` (see :func:`check_term_guards`)."""
    if term.base != y or not term.is_operated:
        return
    if role == "x":
        key = (
            "spec_depvar_lag_exogenous"
            if not term.has_dsf and term.netlag >= 1
            else "spec_depvar_current_exogenous"
        )
        raise _fail(key, term=term.name, y=y)
    if term.has_dsf or term.netlag < 1:
        key = "spec_depvar_current_iv" if role == "iv" else "spec_depvar_current_regressor"
        raise _fail(key, term=term.name, y=y)


def _check_iv_lag(y: str, term: Term, declared: list[tuple[str, int, bool]], method: str) -> None:
    """Guard (c): an external instrument must be uncorrelated with the transformed error."""
    # Stata: xtdpthresh.ado:934-963
    fd = method == "fd"
    need: int | None = (2 if fd else 1) if term.base == y else None
    for base, smallest, endogenous in declared:
        if base != term.base:
            continue
        required = smallest + ((2 if fd else 1) if endogenous else (1 if fd else 0))
        if need is None or required > need:
            need = required
    lag_ = min(term.netlag, 0) if term.has_dsf else term.netlag
    if need is not None and lag_ < need:
        raise _fail("spec_iv_lag_needed", term=term.name, method=method, base=term.base, need=need)


def _check_exogenous_term(term: Term, declared: list[tuple[str, int, bool]]) -> None:
    """Guard (b): a strictly exogenous term cannot be a lag of a declared variable."""
    for base, smallest, _ in declared:
        if base == term.base and (term.has_dsf or smallest <= term.netlag):
            raise _fail("spec_exogenous_lag_of_declared", term=term.name, base=base)


def check_term_guards(y: str, roles: Roles, method: str) -> None:
    """Guards on operated terms, role by role (strictly exogenous, declared, instruments).

    (a) Operated terms of ``y`` (lags only, and only as predetermined or endogenous).
    (b) A strictly exogenous term cannot be a lag, or the same date, of a variable declared
    endogenous or predetermined.
    (c) An external instrument cannot be built on ``y`` or a declared variable at a lag that
    still contains an error the transformation does not remove.
    """
    # Stata: xtdpthresh.ado:868-982
    declared = _declared_timing(roles)
    groups = (
        ("x", (*roles["x"], *roles["exogenous"])),
        ("endogenous", (*roles["endogenous"], *roles["predetermined"])),
        ("iv", tuple(roles["iv"])),
    )
    for role, terms in groups:
        for term in terms:
            _check_depvar_term(y, role, term)
            if role == "iv":
                _check_iv_lag(y, term, declared, method)
            if role == "x" and declared:
                _check_exogenous_term(term, declared)


def _warn(key: str, **fields: Any) -> None:
    warnings.warn(message(key, **fields), PyxdpthreshWarning, stacklevel=4)


def _warn_about_specification(y: str, q: str, roles: Roles, options: XtdpthreshOptions) -> None:
    """Print the notes the Stata command prints unless ``nowarn`` is given."""
    # Stata: xtdpthresh.ado:573-597
    if not options.warn:
        return
    regressors = [*roles["x"], *roles["exogenous"], *roles["endogenous"], *roles["predetermined"]]
    if options.kink and q not in _names(regressors):
        _warn("warn_kink_no_q", q=q)
    if options.maxlag[1] < 2 and (not options.static or roles["endogenous"]):
        _warn("warn_maxlag_one", y=y)


def check_specification(
    y: str,
    x: TermList = None,
    *,
    q: str,
    endogenous: TermList = None,
    predetermined: TermList = None,
    exogenous: TermList = None,
    iv: TermList = None,
    **options: Any,
) -> Specification:
    """Validate a call to ``xtdpthresh`` and return the specification.

    Parameters
    ----------
    y
        Dependent variable (a plain column name).
    x
        Strictly exogenous regressors (``indepvars`` of the Stata command).
    q
        Threshold variable.
    endogenous, predetermined, exogenous, iv
        Roles of the other variables; ``iv`` are external instruments.
    **options
        The options accepted by :func:`~pyxtdpthresh.models.xtdpthresh.options.make_options`.

    Raises
    ------
    SpecificationError
        On the first rule that fails; ``key`` names it and ``stata_code`` is Stata's code.
    """
    # Stata: xtdpthresh.ado:58-1030
    roles: dict[str, tuple[Term, ...]] = {
        "x": tuple(parse_terms(_as_list(x))),
        "endogenous": tuple(parse_terms(_as_list(endogenous))),
        "predetermined": tuple(parse_terms(_as_list(predetermined))),
        "exogenous": tuple(parse_terms(_as_list(exogenous))),
        "iv": tuple(parse_terms(_as_list(iv))),
    }
    depvar = parse_term(y)
    named = [t.name for ts in (depvar, *roles.values()) for t in ts]
    opts = make_options(terms=named, **options)
    if len(depvar) != 1 or depvar[0].is_operated:
        raise _fail("spec_depvar_operator", term=str(y))
    name, threshold = depvar[0].base, str(q)

    check_overlaps(roles)
    check_static_not_empty(name, roles, opts.static)
    _warn_about_specification(name, threshold, roles, opts)
    check_continuity_test(threshold, roles, opts)
    check_duplicates(roles)
    check_depvar_and_q(name, threshold, roles)
    check_auto_lag(name, roles, opts.static)
    check_term_guards(name, roles, opts.method)
    check_time_effects(opts)
    return Specification(name, threshold, options=opts, **roles)
