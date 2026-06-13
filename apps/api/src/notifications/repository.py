from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.models import DeviceToken


class DeviceTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, *, user_id: str, token: str, platform: str) -> DeviceToken:
        """Insert or update a device token for the given user.

        Uses PostgreSQL ON CONFLICT DO UPDATE so that re-registering the same
        token updates updated_at without creating a duplicate row.
        """
        stmt = (
            pg_insert(DeviceToken)
            .values(user_id=user_id, token=token, platform=platform)
            .on_conflict_do_update(
                constraint="uq_device_token_user_token",
                set_={
                    "platform": platform,
                    "updated_at": func.now(),
                },
            )
            .returning(DeviceToken)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        row = result.scalar_one()
        await self.session.refresh(row)
        return row

    async def find_by_user(self, *, user_id: str) -> list[DeviceToken]:
        stmt = (
            select(DeviceToken)
            .where(DeviceToken.user_id == user_id)
            .order_by(DeviceToken.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_user_and_token(
        self, *, user_id: str, token: str
    ) -> DeviceToken | None:
        stmt = select(DeviceToken).where(
            DeviceToken.user_id == user_id,
            DeviceToken.token == token,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_user_and_token(self, *, user_id: str, token: str) -> bool:
        """Delete a specific token for the user. Returns True if a row was deleted."""
        stmt = (
            delete(DeviceToken)
            .where(
                DeviceToken.user_id == user_id,
                DeviceToken.token == token,
            )
            .returning(DeviceToken.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none() is not None
