from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notifications import Notification, NotificationTypeEnum


async def create_notification(
    db: AsyncSession,
    user_id: int,
    type_: NotificationTypeEnum,
    message: str,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type_,
        message=message,
    )

    db.add(notification)
    return notification
