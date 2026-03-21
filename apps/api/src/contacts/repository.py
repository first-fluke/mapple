from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_paginated(
        self,
        *,
        user_id: int,
        cursor: int | None = None,
        per_page: int = 20,
        search: str | None = None,
        sort: str = "created_at_desc",
    ) -> tuple[list[Contact], bool]:
        stmt = select(Contact).where(Contact.user_id == user_id)
        if search:
            stmt = stmt.where(Contact.name.ilike(f"%{search}%"))
        if cursor:
            stmt = stmt.where(Contact.id < cursor)

        # sorting
        sort_map = {
            "name_asc": Contact.name.asc(),
            "name_desc": Contact.name.desc(),
            "created_at_asc": Contact.created_at.asc(),
            "created_at_desc": Contact.created_at.desc(),
        }
        order = sort_map.get(sort, Contact.created_at.desc())
        stmt = stmt.order_by(order, Contact.id.desc())
        stmt = stmt.limit(per_page + 1)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        has_more = len(items) > per_page
        if has_more:
            items = items[:per_page]
        return items, has_more

    async def count(self, *, user_id: int, search: str | None = None) -> int:
        stmt = select(sa_func.count()).select_from(Contact).where(Contact.user_id == user_id)
        if search:
            stmt = stmt.where(Contact.name.ilike(f"%{search}%"))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def find_by_id(self, contact_id: int, user_id: int) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, user_id: int, name: str, email: str | None, phone: str | None) -> Contact:
        contact = Contact(user_id=user_id, name=name, email=email, phone=phone)
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def update(self, contact: Contact, *, name: str | None = None, email: str | None = None, phone: str | None = None) -> Contact:
        if name is not None:
            contact.name = name
        if email is not None:
            contact.email = email
        if phone is not None:
            contact.phone = phone
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def delete(self, contact: Contact) -> None:
        await self.session.delete(contact)
        await self.session.commit()
