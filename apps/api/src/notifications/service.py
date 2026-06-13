from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.exceptions import NotFoundException
from src.notifications.models import DeviceToken
from src.notifications.repository import DeviceTokenRepository


class DeviceTokenService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = DeviceTokenRepository(session)

    async def register(
        self, *, user_id: str, token: str, platform: str
    ) -> DeviceToken:
        """Upsert a device token. Idempotent: re-registering the same token
        updates updated_at and platform without duplicating the row."""
        return await self.repo.upsert(user_id=user_id, token=token, platform=platform)

    async def list_tokens(self, *, user_id: str) -> list[DeviceToken]:
        return await self.repo.find_by_user(user_id=user_id)

    async def unregister(self, *, user_id: str, token: str) -> None:
        """Remove a device token. Raises NotFoundException if the token does not
        exist or does not belong to the requesting user."""
        deleted = await self.repo.delete_by_user_and_token(
            user_id=user_id, token=token
        )
        if not deleted:
            raise NotFoundException(
                message=f"Device token not found for the current user"
            )
