import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete

from src.db.session import AsyncSessionLocal
from src.models.accounts import ActivationToken, PasswordResetToken
from src.tasks.celery_app import celery_app


async def cleanup_expired_tokens_async() -> None:
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(ActivationToken).where(ActivationToken.expires_at < now)
        )
        await db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.expires_at < now)
        )
        await db.commit()


@celery_app.task(name="cleanup_expired_tokens")
def cleanup_expired_tokens() -> None:
    asyncio.run(cleanup_expired_tokens_async())
