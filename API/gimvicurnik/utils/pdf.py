import pdfplumber

Tables = list[list[list[str | None]]]


def extract_tables(filename: str) -> Tables:
    """Extract tables from a PDF file using pdfplumber."""

    tables = []

    with pdfplumber.open(filename) as file:
        for page in file.pages:
            tables.extend(page.extract_tables())

    return tables
