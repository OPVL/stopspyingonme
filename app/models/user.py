from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.alias import Alias
    from app.models.destination import Destination
    from app.models.passkey import Passkey
    from app.models.session import Session


class User(BaseModel):
    """User model for authentication and account management."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Relationships
    aliases: Mapped[list["Alias"]] = relationship(
        "Alias", back_populates="user", cascade="all, delete-orphan"
    )
    destinations: Mapped[list["Destination"]] = relationship(
        "Destination", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    passkeys: Mapped[list["Passkey"]] = relationship(
        "Passkey", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_users_email_lower", "email"),)
