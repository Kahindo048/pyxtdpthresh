"""Recalcule le tableau d'avancement de PLAN.md et vérifie ses références.

Usage
-----
    python tools/avancement.py [--plan CHEMIN] [--check]

Sans option, réécrit le tableau entre les marqueurs ``<!-- AVANCEMENT:DEBUT -->`` et
``<!-- AVANCEMENT:FIN -->``. Avec ``--check``, n'écrit rien et sort avec le code 1 si le
tableau est périmé ou si une dépendance cite un identifiant inexistant.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_PLAN = Path(__file__).resolve().parents[2] / "PLAN.md"
START, END = "<!-- AVANCEMENT:DEBUT -->", "<!-- AVANCEMENT:FIN -->"
BLOCK_RE = re.compile(r"^## ([A-Z])\. (.*)")
ITEM_RE = re.compile(r"^- \[( |x)\] \*\*(\d+\.\d+)\*\* (.*)")
REF_RE = re.compile(r"\b([A-K](?:\.\d+){0,2})\b")


def parse(text: str) -> tuple[dict[str, str], dict[str, tuple[bool, str]]]:
    """Retourne les titres de blocs et les sous-points {id: (fait, texte)}."""
    body = text.split("\n## A. ", 1)
    if len(body) < 2:
        raise SystemExit("Bloc A introuvable dans le plan.")
    titles: dict[str, str] = {}
    items: dict[str, tuple[bool, str]] = {}
    block = ""
    for line in ("## A. " + body[1]).splitlines():
        if m := BLOCK_RE.match(line):
            block = m.group(1)
            titles[block] = m.group(2)
        elif (m := ITEM_RE.match(line)) and block:
            items[f"{block}.{m.group(2)}"] = (m.group(1) == "x", m.group(3))
    return titles, items


def unknown_references(items: dict[str, tuple[bool, str]], titles: dict[str, str]) -> list[str]:
    """Identifiants cités dans une dépendance mais absents du plan."""
    known = set(items) | {i.rsplit(".", 1)[0] for i in items} | set(titles)
    bad = []
    for ident, (_, text) in items.items():
        for label in re.findall(r"`(?:après|progressif :) ([^`]*)`", text):
            bad.extend(f"{ident} -> {ref}" for ref in REF_RE.findall(label) if ref not in known)
    return bad


def bar(pct: int) -> str:
    return "█" * (pct // 10) + "░" * (10 - pct // 10)


def table(titles: dict[str, str], items: dict[str, tuple[bool, str]]) -> str:
    rows = ["| Bloc | Fait | Total | Avancement | En attente |", "|---|---:|---:|---|---:|"]
    done_all = total_all = wait_all = 0
    for block, title in titles.items():
        mine = [(i, v) for i, v in items.items() if i.startswith(block + ".")]
        total = len(mine)
        done = sum(1 for _, v in mine if v[0])
        wait = sum(1 for _, v in mine if not v[0] and "`attend :" in v[1])
        pct = round(100 * done / total) if total else 0
        rows.append(f"| {block}. {title} | {done} | {total} | `{bar(pct)}` {pct} % | {wait} |")
        done_all, total_all, wait_all = done_all + done, total_all + total, wait_all + wait
    pct = round(100 * done_all / total_all) if total_all else 0
    rows.append(
        f"| **Ensemble du plan** | **{done_all}** | **{total_all}** | "
        f"`{bar(pct)}` **{pct} %** | **{wait_all}** |"
    )
    hors = total_all - wait_all
    pct_h = round(100 * done_all / hors) if hors else 0
    rows.append(
        f"| Hors attentes extérieures | {done_all} | {hors} | `{bar(pct_h)}` {pct_h} % | — |"
    )
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = args.plan.read_text(encoding="utf-8")
    titles, items = parse(text)
    bad = unknown_references(items, titles)
    for line in bad:
        print(f"référence inconnue : {line}", file=sys.stderr)

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("Marqueurs d'avancement introuvables.")
    # on conserve l'introduction existante : seul le tableau est remplacé
    old_block = pattern.search(text).group(0)  # type: ignore[union-attr]
    new_block = re.sub(
        r"\| Bloc \|.*?(?=\n\n)", lambda _: table(titles, items), old_block, flags=re.S
    )
    new_text = text.replace(old_block, new_block)
    done = sum(1 for v in items.values() if v[0])
    print(f"{done}/{len(items)} sous-points faits ; {len(bad)} référence(s) inconnue(s).")
    if args.check:
        stale = new_text != text
        if stale:
            print("Le tableau d'avancement est périmé.", file=sys.stderr)
        return 1 if (stale or bad) else 0
    args.plan.write_text(new_text, encoding="utf-8", newline="\n")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
