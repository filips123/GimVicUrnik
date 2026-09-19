from __future__ import annotations

import typing

import mammoth  # type: ignore

if typing.TYPE_CHECKING:
    from io import BytesIO
    from mammoth.documents import Image, Hyperlink  # type: ignore


def ignore_images(_image: Image) -> dict:
    return {}


def transform_hyperlinks(hyperlink: Hyperlink) -> Hyperlink:
    hyperlink.target_frame = "_blank"
    return hyperlink


def extract_content(stream: BytesIO) -> str:
    """Extract the document content from DOCX using mammoth and return it as HTML."""

    result = mammoth.convert_to_html(
        stream,
        convert_image=ignore_images,
        transform_document=mammoth.transforms.element_of_type(
            mammoth.documents.Hyperlink,
            transform_hyperlinks,
        ),
    )

    return typing.cast(str, result.value)
