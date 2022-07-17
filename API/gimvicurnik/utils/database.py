from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar
    from sqlalchemy.orm import Session
    from ..database import Base

    BaseModel = TypeVar("BaseModel", bound=Base)


def get_or_create(session: Session, model: Type[BaseModel], **kwargs: Any) -> Tuple[BaseModel, bool]:
    """Get SQLAlchemy model or create a new one."""

    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False

    instance = model(**kwargs)
    session.add(instance)
    session.flush()
    return instance, True
