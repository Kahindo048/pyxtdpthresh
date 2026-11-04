"""Intermediate representation of a table, independent of the output format (layer 6).

A :class:`TableSpec` holds the text of every cell, already formatted (digits, decimal sign,
statistic in parentheses), so the renderers only decide how a table looks: escaping, rules,
fonts.  Every renderer reads this one object and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:
    """One coefficient cell.

    Attributes
    ----------
    text
        Estimate (with its statistic when the table is on a single row).
    stars
        Number of significance stars.
    below
        Statistic printed under the estimate, for example ``(0.045)`` (empty on a single row).
    """

    text: str = ""
    stars: int = 0
    below: str = ""

    def inline(self) -> str:
        """Return the cell on one line: estimate, stars, then the statistic."""
        head = self.text + "*" * self.stars
        return f"{head} {self.below}".strip() if self.below else head


@dataclass(frozen=True)
class CoefRow:
    """A coefficient row: its label, one cell per column and the block it belongs to."""

    label: str
    cells: tuple[Cell, ...]
    block: str = ""


@dataclass(frozen=True)
class StatRow:
    """A row of the lines under the coefficients: a label and one text per column."""

    label: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class TableSpec:
    r"""Content of a table of models side by side.

    Attributes
    ----------
    dep_var_label
        Words that introduce the dependent variable (``Dependent variable``).
    dep_vars
        Dependent variable of each column.
    column_labels
        Optional group labels above the column names (one per column, empty to skip the line).
    columns
        Column names (``(1)``, ``(2)`` or the model names).
    rows
        Coefficient rows; a row whose ``block`` differs from the previous one starts a block.
    stats
        Rows under the coefficients: added lines, then diagnostics.
    notes
        Lines under the table, the legend of the stars first.
    title, label
        Caption and anchor of the table (``\\label`` in LaTeX).
    font_size
        LaTeX size command without the backslash (``footnotesize``); empty for the default.
    single_row
        Whether each coefficient and its statistic share a line.
    """

    dep_var_label: str
    dep_vars: tuple[str, ...]
    columns: tuple[str, ...]
    rows: tuple[CoefRow, ...]
    stats: tuple[StatRow, ...]
    notes: tuple[str, ...] = ()
    column_labels: tuple[str, ...] = ()
    title: str = ""
    label: str = ""
    font_size: str = ""
    single_row: bool = False

    @property
    def n_columns(self) -> int:
        """Number of model columns (without the label column)."""
        return len(self.columns)

    def lines(self) -> list[list[str]]:
        """Return the table as plain rows of text, header included (stars after the estimate).

        This is the common flattening the text, CSV and Excel renderers build on.
        """
        out: list[list[str]] = []
        if len(set(self.dep_vars)) == 1:
            out.append([f"{self.dep_var_label}: {self.dep_vars[0]}", *[""] * (self.n_columns)])
        else:
            out.append([self.dep_var_label, *self.dep_vars])
        if any(self.column_labels):
            out.append(["", *self.column_labels])
        out.append(["", *self.columns])
        block = None
        for row in self.rows:
            if row.block != block and row.block:
                out.append([row.block, *[""] * self.n_columns])
            block = row.block
            if self.single_row:
                out.append([row.label, *[c.inline() for c in row.cells]])
            else:
                out.append([row.label, *[c.text + "*" * c.stars for c in row.cells]])
                out.append(["", *[c.below for c in row.cells]])
        out.extend([stat.label, *stat.values] for stat in self.stats)
        out.extend([[note] + [""] * self.n_columns for note in self.notes])
        return out
