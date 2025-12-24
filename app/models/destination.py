from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.alias import Alias
    from app.models.user import User


class Destination(BaseModel):
    """Destination email addresses for forwarding."""

    __tablename__ = "destinations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verification_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="destinations")
    aliases: Mapped[list["Alias"]] = relationship("Alias", back_populates="destination")

    __table_args__ = (
        Index("ix_destinations_user_email", "user_id", "email", unique=True),
        Index("ix_destinations_verification_token", "verification_token"),
    )
