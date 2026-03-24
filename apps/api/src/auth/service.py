from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.repository import AuthRepository
from src.auth.schemas import ProfileUpdate
from src.lib.exceptions import UnauthorizedException


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AuthRepository(session)

    async def get_me(self, user_id: str) -> User:
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise UnauthorizedException(message="User not found")
        return user

    async def update_me(self, user_id: str, data: ProfileUpdate) -> User:
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise UnauthorizedException(message="User not found")
        return await self.repo.update(user, name=data.name)

    async def delete_me(self, user_id: str) -> None:
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise UnauthorizedException(message="User not found")
        await self.repo.delete(user)
