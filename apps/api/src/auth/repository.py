import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_id(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_by_email(
        self,
        *,
        email: str,
        name: str,
        image: str | None,
    ) -> User:
        existing = await self.find_by_email(email)
        if existing:
            existing.name = name or existing.name
            if image is not None:
                existing.image = image
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        user = User(
            id=secrets.token_urlsafe(16),
            email=email,
            name=name or email,
            image=image,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, **kwargs: str | None) -> User:
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()
