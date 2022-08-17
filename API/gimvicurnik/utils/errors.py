"""
File based on the `TracebackException` from the Python Standard Library
with all unnecessary functionalities (stack formatting, etc.) removed.

Sources:
- https://github.com/python/cpython/blob/d4c4a76ed1427c947fcbbe692625b3f644cf3aaf/Lib/traceback.py#L609-L629
- https://github.com/python/cpython/blob/d4c4a76ed1427c947fcbbe692625b3f644cf3aaf/Lib/traceback.py#L868-L966
"""

from __future__ import annotations

import textwrap
import typing
from traceback import TracebackException as _TracebackException

if typing.TYPE_CHECKING:
    from typing import Iterable, Iterator, List, Optional, Union


class TracebackException(_TracebackException):
    exceptions: Optional[List[TracebackException]] = None


class _ExceptionPrintContext:
    def __init__(self) -> None:
        self.exception_group_depth = 0

    def indent(self) -> str:
        return " " * (2 * self.exception_group_depth)

    def emit(self, text_gen: Union[str, Iterable]) -> Iterator[str]:
        indent_str = self.indent()

        if isinstance(text_gen, str):
            yield textwrap.indent(text_gen, indent_str, lambda line: True)
        else:
            for text in text_gen:
                yield textwrap.indent(text, indent_str, lambda line: True)


def _format_traceback_exception(
    exc: TracebackException,
    ctx: Optional[_ExceptionPrintContext] = None,
) -> Iterator[str]:
    if ctx is None:
        ctx = _ExceptionPrintContext()

    if exc.exceptions is None:
        # Format plain exception
        yield from ctx.emit(exc.format_exception_only())

    else:
        # Format exception group
        is_toplevel = ctx.exception_group_depth == 0
        if is_toplevel:
            ctx.exception_group_depth += 1

        yield from ctx.emit(exc.format_exception_only())

        for i in range(len(exc.exceptions)):
            ctx.exception_group_depth += 1
            yield from _format_traceback_exception(exc.exceptions[i], ctx)
            ctx.exception_group_depth -= 1

        if is_toplevel:
            assert ctx.exception_group_depth == 1
            ctx.exception_group_depth = 0


def format_exception(error: BaseException) -> str:
    """Format exception and exception group without the code stack."""

    te = TracebackException(type(error), error, error.__traceback__, limit=None)
    return "".join(_format_traceback_exception(te))
