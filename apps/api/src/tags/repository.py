from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.models import ContactTag, Tag


class TagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_all(
        self, user_id: str, *, page: int, per_page: int
    ) -> tuple[list[Tag], int]:
        count_q = select(func.count()).select_from(Tag).where(Tag.user_id == user_id)
        total = (await self.session.execute(count_q)).scalar_one()

        q = (
            select(Tag)
            .where(Tag.user_id == user_id)
            .order_by(Tag.name)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        rows = (await self.session.execute(q)).scalars().all()
        return list(rows), total

    async def find_by_id(self, tag_id: int, user_id: str) -> Tag | None:
        q = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        return (await self.session.execute(q)).scalar_one_or_none()

    async def find_by_name(self, user_id: str, name: str) -> Tag | None:
        q = select(Tag).where(Tag.user_id == user_id, Tag.name == name)
        return (await self.session.execute(q)).scalar_one_or_none()

    async def create(self, tag: Tag) -> Tag:
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def update(self, tag: Tag) -> Tag:
        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def delete(self, tag: Tag) -> None:
        await self.session.delete(tag)
        await self.session.flush()

    async def find_contact_tag(
        self, contact_id: int, tag_id: int
    ) -> ContactTag | None:
        q = select(ContactTag).where(
            ContactTag.contact_id == contact_id,
            ContactTag.tag_id == tag_id,
        )
        return (await self.session.execute(q)).scalar_one_or_none()

    async def attach_contact(self, contact_id: int, tag_id: int) -> ContactTag:
        ct = ContactTag(contact_id=contact_id, tag_id=tag_id)
        self.session.add(ct)
        await self.session.flush()
        return ct

    async def detach_contact(self, contact_id: int, tag_id: int) -> bool:
        q = delete(ContactTag).where(
            ContactTag.contact_id == contact_id,
            ContactTag.tag_id == tag_id,
        )
        result = await self.session.execute(q)
        await self.session.flush()
        return (result.rowcount or 0) > 0
