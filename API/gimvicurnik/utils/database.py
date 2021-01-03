from contextlib import contextmanager

from ..database import Session


@contextmanager
def session_scope():
    """Wrap SQLAlchemy session into `with` block."""

    session = Session()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def get_or_create(session, model, **kwargs):
    """Get or create a new SQLAlchemy model."""

    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False

    instance = model(**kwargs)
    session.add(instance)
    session.flush()
    return instance, True
