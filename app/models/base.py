from typing import Any

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BaseModel(Base, TimestampMixin):
    """Base model with id and timestamps for all tables."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Generate __tablename__ automatically
    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__tablename__") and not cls.__abstract__:
            cls.__tablename__ = cls.__name__.lower()
