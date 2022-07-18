from __future__ import annotations

import typing
from unittest.mock import Mock

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Any, Callable, Optional, Type, TypeVar
    from typing_extensions import ParamSpec

    TP = ParamSpec("TP")
    TR = TypeVar("TR")

    SP = ParamSpec("SP")
    SR = TypeVar("SR")

__all__ = ["start_transaction", "start_span", "with_transaction", "with_span"]


class WithMock(Mock):
    """Mock that can be used with a `with` block."""

    def __enter__(self) -> WithMock:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass


try:
    from sentry_sdk import Hub, start_transaction, start_span

    sentry_available = True

except ImportError:
    start_transaction = WithMock()
    start_span = WithMock()

    sentry_available = False


def with_transaction(
    pass_transaction: bool = False,
    **kwargs: Any,
) -> Callable[[Callable[TP, TR]], Callable[TP, TR]]:
    """
    Wrap the function inside the Sentry transaction.

    If `pass_transaction` is `True` and Sentry is installed, the transaction
    will be passed as a `transaction` keyword-argument. If Sentry is not
    installed, empty transaction mock will be passed instead.

    :param bool pass_transaction: Should the transaction be passed to the wrapped function?
    :param dict kwargs: Arguments to be passed to `start_transaction`
    :return: The function decorator
    """

    def _transaction_decorator(function: Callable[TP, TR]) -> Callable[TP, TR]:
        def _transaction_wrapper(*fargs: TP.args, **fkwargs: TP.kwargs) -> TR:
            if not sentry_available:
                if pass_transaction:
                    fkwargs["transaction"] = Mock()
                return function(*fargs, **fkwargs)

            with start_transaction(**kwargs) as transaction:
                if pass_transaction:
                    fkwargs["transaction"] = transaction
                return function(*fargs, **fkwargs)

        return _transaction_wrapper

    return _transaction_decorator


def with_span(
    pass_span: bool = False,
    **kwargs: Any,
) -> Callable[[Callable[SP, SR]], Callable[SP, SR]]:
    """
    Wrap the function inside the Sentry span.

    If `pass_span` is `True` and Sentry is installed, the span
    will be passed as a `span` keyword-argument. If Sentry is not
    installed, empty span mock will be passed instead.

    :param bool pass_span: Should the span be passed to the wrapped function?
    :param dict kwargs: Arguments to be passed to `start_child`
    :return: The function decorator
    """

    def _span_decorator(function: Callable[SP, SR]) -> Callable[SP, SR]:
        def _span_wrapper(*fargs: SP.args, **fkwargs: SP.kwargs) -> SR:
            if not sentry_available or not Hub.current.scope.span:
                if pass_span:
                    fkwargs["span"] = Mock()
                return function(*fargs, **fkwargs)

            with Hub.current.scope.span.start_child(**kwargs) as span:
                if pass_span:
                    fkwargs["span"] = span
                return function(*fargs, **fkwargs)

        return _span_wrapper

    return _span_decorator
