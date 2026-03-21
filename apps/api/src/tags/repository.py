from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.models import Tag


class TagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_user(self, user_id: int) -> list[Tag]:
        stmt = (
            select(Tag)
            .where(Tag.user_id == user_id)
            .order_by(Tag.name)
            .order_by(Tag.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, tag_id: int, user_id: int) -> Tag | None:
        stmt = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str, user_id: int) -> Tag | None:
        stmt = select(Tag).where(Tag.name == name, Tag.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, user_id: int, name: str) -> Tag:
        tag = Tag(user_id=user_id, name=name)
        stmt = select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id,
        )
    async def create(
        self,
        *,
        user_id: int,
        name: str,
        color: str,
    ) -> Tag:
        tag = Tag(
            user_id=user_id,
            name=name,
            color=color,
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def update(self, tag: Tag, **kwargs: str | None) -> Tag:
        for key, value in kwargs.items():
            if value is not None:
                setattr(tag, key, value)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def delete(self, tag: Tag) -> None:
        await self.session.delete(tag)
        await self.session.commit()
