from __future__ import annotations

import typing

import pdfplumber

if typing.TYPE_CHECKING:
    from typing import Any

    Tables = list[list[list[str | None]]]


def keep_visible_lines(obj: dict[str, Any]) -> bool:
    if obj["object_type"] == "rect":
        visible: bool = obj["non_stroking_color"] == [0, 0, 0]
        return visible
    return True


def extract_tables(filename: str) -> Tables:
    """Extract tables from a PDF file using pdfplumber."""

    tables = []

    with pdfplumber.open(filename) as file:
        for page in file.pages:
            page = page.filter(keep_visible_lines)
            tables.extend(page.extract_tables())

    return tables
