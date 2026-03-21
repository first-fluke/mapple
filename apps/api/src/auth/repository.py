from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import UserAuth


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_provider(
        self, provider: str, provider_id: str
    ) -> UserAuth | None:
        stmt = select(UserAuth).where(
            UserAuth.provider == provider,
            UserAuth.provider_id == provider_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: int) -> UserAuth | None:
        return await self.session.get(UserAuth, user_id)

    async def create(
        self,
        *,
        provider: str,
        provider_id: str,
        email: str,
        name: str | None,
        avatar_url: str | None,
    ) -> UserAuth:
        user = UserAuth(
            provider=provider,
            provider_id=provider_id,
            email=email,
            name=name,
            avatar_url=avatar_url,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: UserAuth, **kwargs: str | None) -> UserAuth:
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: UserAuth) -> None:
        await self.session.delete(user)
        await self.session.commit()
