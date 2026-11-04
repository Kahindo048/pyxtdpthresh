"""Audit the docstrings of the public API (K.2.5).

    python tools/check_docstrings.py

For every name of ``pyxtdpthresh.__all__`` (and, for a class, every public method and property),
the audit requires a docstring with a one-line summary; for a function or a method it also requires
that every parameter be described in a ``Parameters`` section (several names may share an entry,
``a, b``) and, when the function returns something, a ``Returns`` section.  Exceptions and
warnings need only their summary.  It prints the gaps and exits with status 1 if there are any.
"""

from __future__ import annotations

import inspect
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pyxtdpthresh as pyx  # noqa: E402

_TITLES = "Parameters|Returns|Yields|Raises|Notes|Examples|See Also|Attributes"
_SECTION = re.compile(rf"^\s*({_TITLES})\s*\n\s*-{{3,}}\s*$", re.M)


def sections(doc: str) -> dict[str, str]:
    """The numpy-style sections of a docstring, by title (the text before them is ``""``)."""
    marks = list(_SECTION.finditer(doc))
    out = {"": doc[: marks[0].start()] if marks else doc}
    for i, mark in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(doc)
        out[mark.group(1)] = doc[mark.end() : end]
    return out


def documented_names(section: str) -> set[str]:
    """Names introduced by the entries of a ``Parameters`` section (``a, b : type`` gives both)."""
    names: set[str] = set()
    for line in section.splitlines():
        if line and not line[0].isspace():  # the text of an entry is indented
            head = line.strip().split(":")[0]
            names.update(n.strip().lstrip("*") for n in head.split(",") if n.strip())
    return names


def _returns_something(obj: Any) -> bool:
    note = inspect.signature(obj).return_annotation
    return note not in (inspect.Signature.empty, None, "None")


def audit_callable(label: str, obj: Any) -> Iterator[str]:
    """The gaps of one function or method."""
    doc = inspect.getdoc(obj) or ""
    if not doc.strip():
        yield f"{label}: no docstring"
        return
    parts = sections(doc)
    if not parts[""].strip():
        yield f"{label}: no summary line"
    wanted = [n for n in inspect.signature(obj).parameters if n not in ("self", "cls")]
    if wanted:
        described = documented_names(parts.get("Parameters", ""))
        missing = [n for n in wanted if n not in described]
        if missing:
            yield f"{label}: parameters not described: {', '.join(missing)}"
    if _returns_something(obj) and "Returns" not in parts and "Yields" not in parts:
        yield f"{label}: no Returns section"


def audit_class(label: str, cls: type) -> Iterator[str]:
    """The gaps of a class: its summary and its public methods and properties."""
    if not (inspect.getdoc(cls) or "").strip():
        yield f"{label}: no docstring"
    for name, member in sorted(vars(cls).items()):
        if name.startswith("_") or not (
            inspect.isfunction(member) or isinstance(member, (property, staticmethod, classmethod))
        ):
            continue
        target = member.fget if isinstance(member, property) else getattr(cls, name)
        if isinstance(member, property):
            if not (inspect.getdoc(target) or "").strip():
                yield f"{label}.{name}: no docstring"
        else:
            yield from audit_callable(f"{label}.{name}", target)


def audit() -> list[str]:
    """Every gap of the public API."""
    gaps: list[str] = []
    for name in pyx.__all__:
        if name == "__version__":
            continue
        obj = getattr(pyx, name)
        if inspect.isclass(obj):
            if issubclass(obj, (Exception, Warning)):
                if not (inspect.getdoc(obj) or "").strip():
                    gaps.append(f"{name}: no docstring")
            else:
                gaps += audit_class(name, obj)
        elif callable(obj):
            gaps += audit_callable(name, obj)
    return gaps


if __name__ == "__main__":
    found = audit()
    print("\n".join(found) if found else "the public API is documented")
    sys.exit(1 if found else 0)
