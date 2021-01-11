from unittest.mock import Mock

try:
    from sentry_sdk import Hub, start_transaction

    sentry_available = True
except ImportError:
    sentry_available = False


def with_transaction(pass_transaction=False, **kwargs):
    """
    Wrap the function inside the Sentry transaction if the Sentry
    is installed, otherwise return transaction stub/mock.

    :param bool pass_transaction: Should the transaction be passes to wrapped function?
    :return: The function decorator
    """

    def _transaction_decorator(function):
        def _transaction_wrapper(*fargs, **fkwargs):
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


def with_span(pass_span=False, **kwargs):
    """
    Wrap the function inside the Sentry span if the Sentry
    is installed, otherwise return span stub/mock.

    :param bool pass_span: Should the span be passes to wrapped function?
    :return: The function decorator
    """

    def _span_decorator(function):
        def _span_wrapper(*fargs, **fkwargs):
            if not sentry_available:
                if pass_span:
                    fkwargs["span"] = Mock()
                return function(*fargs, **fkwargs)

            with Hub.current.scope.span.start_child(**kwargs) as span:
                if pass_span:
                    fkwargs["span"] = span
                return function(*fargs, **fkwargs)

        return _span_wrapper

    return _span_decorator
