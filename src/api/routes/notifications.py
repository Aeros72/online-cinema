from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.models.notifications import Notification
from src.schemas.notifications import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
async def get_notifications_endpoint(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    )

    notifications = result.scalars().all()
    return [
        NotificationResponse.model_validate(notification)
        for notification in notifications
    ]
