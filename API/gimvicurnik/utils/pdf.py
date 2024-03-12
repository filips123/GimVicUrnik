from __future__ import annotations

import typing

import pdfplumber

if typing.TYPE_CHECKING:
    from typing import Any
    from io import BytesIO

    Tables = list[list[list[str | None]]]


def keep_visible_lines(obj: dict[str, Any]) -> bool:
    if obj["object_type"] == "rect":
        visible = obj["non_stroking_color"] in ((0,), (0, 0, 0))
        return visible
    return True


def extract_tables(stream: BytesIO) -> Tables:
    """Extract tables from a PDF file using pdfplumber."""

    tables = []

    with pdfplumber.open(stream) as file:
        for page in file.pages:
            page = page.filter(keep_visible_lines)
            tables.extend(page.extract_tables())

    return tables
