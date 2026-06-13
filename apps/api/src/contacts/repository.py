import datetime

from sqlalchemy import select
from sqlalchemy import func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact, ContactTag
from src.tags.models import Tag


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _not_deleted(self):
        return Contact.deleted_at.is_(None)

    async def _resolve_tags(self, user_id: str, tag_ids: list[int]) -> list[Tag]:
        """Return Tag objects that belong to the given user and match the given ids.

        Unknown or foreign tag_ids are silently ignored — only the user's own tags
        are associated.
        """
        if not tag_ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_paginated(
        self,
        *,
        user_id: str,
        cursor: int | None = None,
        per_page: int = 20,
        q: str | None = None,
        tag: str | None = None,
        country: str | None = None,
        city: str | None = None,
        sort: str = "created_at_desc",
    ) -> tuple[list[Contact], bool]:
        stmt = select(Contact).where(Contact.user_id == user_id, self._not_deleted())
        if q:
            stmt = stmt.where(Contact.name.ilike(f"%{q}%"))
        if country:
            stmt = stmt.where(Contact.country == country)
        if city:
            stmt = stmt.where(Contact.city == city)
        if tag:
            # Filter by tag name: join contact_tag → tag and match by name.
            stmt = stmt.where(
                Contact.id.in_(
                    select(ContactTag.contact_id)
                    .join(Tag, Tag.id == ContactTag.tag_id)
                    .where(Tag.user_id == user_id, Tag.name == tag)
                )
            )
        if cursor:
            stmt = stmt.where(Contact.id < cursor)

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
        items = list(result.scalars().unique().all())
        has_more = len(items) > per_page
        if has_more:
            items = items[:per_page]
        return items, has_more

    async def count(
        self,
        *,
        user_id: str,
        q: str | None = None,
        tag: str | None = None,
        country: str | None = None,
        city: str | None = None,
    ) -> int:
        stmt = (
            select(sa_func.count())
            .select_from(Contact)
            .where(Contact.user_id == user_id, self._not_deleted())
        )
        if q:
            stmt = stmt.where(Contact.name.ilike(f"%{q}%"))
        if country:
            stmt = stmt.where(Contact.country == country)
        if city:
            stmt = stmt.where(Contact.city == city)
        if tag:
            stmt = stmt.where(
                Contact.id.in_(
                    select(ContactTag.contact_id)
                    .join(Tag, Tag.id == ContactTag.tag_id)
                    .where(Tag.user_id == user_id, Tag.name == tag)
                )
            )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def find_by_id(self, contact_id: int, user_id: str) -> Contact | None:
        stmt = select(Contact).where(
            Contact.id == contact_id,
            Contact.user_id == user_id,
            self._not_deleted(),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: str,
        name: str,
        email: str | None,
        phone: str | None,
        country: str | None = None,
        city: str | None = None,
        tag_ids: list[int] | None = None,
    ) -> Contact:
        contact = Contact(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            country=country,
            city=city,
        )
        if tag_ids:
            contact.tags = await self._resolve_tags(user_id, tag_ids)
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def update(
        self,
        contact: Contact,
        *,
        user_id: str,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        country: str | None = None,
        city: str | None = None,
        avatar_url: str | None = None,
        tag_ids: list[int] | None = None,
    ) -> Contact:
        if name is not None:
            contact.name = name
        if email is not None:
            contact.email = email
        if phone is not None:
            contact.phone = phone
        if latitude is not None:
            contact.latitude = latitude
        if longitude is not None:
            contact.longitude = longitude
        if avatar_url is not None:
            contact.avatar_url = avatar_url
        if country is not None:
            contact.country = country
        if city is not None:
            contact.city = city
        if tag_ids is not None:
            contact.tags = await self._resolve_tags(user_id, tag_ids)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def soft_delete(self, contact: Contact) -> None:
        contact.deleted_at = datetime.datetime.now(datetime.UTC)
        await self.session.commit()
