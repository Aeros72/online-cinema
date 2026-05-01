import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class NotificationTypeEnum(str, enum.Enum):
    COMMENT_REPLY = "comment_reply"
    COMMENT_LIKE = "comment_like"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    type: Mapped[NotificationTypeEnum] = mapped_column(
        Enum(NotificationTypeEnum),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(String(255), nullable=False)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
