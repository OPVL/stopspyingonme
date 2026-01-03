from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.destination import Destination
    from app.models.user import User


class Alias(BaseModel):
    """Email aliases for forwarding."""

    __tablename__ = "aliases"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_id: Mapped[int] = mapped_column(
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(32), nullable=False)  # Updated max length
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    labels: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(50)), nullable=True, default=list
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="aliases")
    destination: Mapped["Destination"] = relationship(
        "Destination", back_populates="aliases"
    )

    @property
    def full_address(self) -> str:
        """Return the full email address."""
        return f"{self.name}@{self.domain}"

    __table_args__ = (
        Index("ix_aliases_name_domain", "name", "domain", unique=True),
        Index("ix_aliases_user_active", "user_id", "is_active"),
        Index("ix_aliases_expires_at", "expires_at"),
    )
