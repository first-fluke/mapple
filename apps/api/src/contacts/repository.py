import base64

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from sqlalchemy import select, func as sa_func
from typing import Any
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.contacts.models import Contact, contact_tags
from src.tags.models import Tag


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_user_paginated(
        self,
        user_id: int,
        *,
        cursor: str | None = None,
        per_page: int = 20,
        search: str | None = None,
        sort: str = "created_at_desc",
        has_email: bool | None = None,
        has_phone: bool | None = None,
    ) -> tuple[list[Contact], str | None, bool]:
        stmt = select(Contact).where(Contact.user_id == user_id)

        if search:
            stmt = stmt.where(Contact.name.ilike(f"%{search}%"))

        if has_email is True:
            stmt = stmt.where(Contact.email.isnot(None), Contact.email != "")
        if has_phone is True:
            stmt = stmt.where(Contact.phone.isnot(None), Contact.phone != "")

        match sort:
            case "name_asc":
                stmt = stmt.order_by(Contact.name.asc(), Contact.id.asc())
            case "name_desc":
                stmt = stmt.order_by(Contact.name.desc(), Contact.id.desc())
            case "created_at_asc":
                stmt = stmt.order_by(Contact.created_at.asc(), Contact.id.asc())
            case _:
                stmt = stmt.order_by(Contact.created_at.desc(), Contact.id.desc())

        offset = _decode_cursor(cursor) if cursor else 0
        stmt = stmt.offset(offset).limit(per_page + 1)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        has_more = len(items) > per_page
        if has_more:
            items = items[:per_page]

        next_cursor = _encode_cursor(offset + per_page) if has_more else None

        return items, next_cursor, has_more

    async def count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Contact).where(Contact.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()


def _encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(str(offset).encode()).decode()


def _decode_cursor(cursor: str) -> int:
    try:
        return int(base64.urlsafe_b64decode(cursor).decode())
    except Exception:
        return 0
    async def find_paginated(
        cursor: int | None = None,
    ) -> tuple[list[Contact], bool]:
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
        return items, has_more
    async def count(self, *, user_id: int, search: str | None = None) -> int:
        stmt = select(sa_func.count()).select_from(Contact).where(Contact.user_id == user_id)
    async def find_by_id(self, contact_id: int, user_id: int) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
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
    async def delete(self, contact: Contact) -> None:
        await self.session.delete(contact)
    async def find_by_id(self, *, user_id: int, contact_id: int) -> Contact | None:
        stmt = (
            select(Contact)
            .options(selectinload(Contact.tags))
            .where(
                Contact.id == contact_id,
                Contact.user_id == user_id,
                Contact.deleted_at.is_(None),
            )
        )
    async def list_contacts(
        tag: str | None = None,
        country: str | None = None,
        city: str | None = None,
        q: str | None = None,
            .order_by(Contact.id.desc())
        if cursor is not None:
        if tag:
            stmt = stmt.where(
                Contact.id.in_(
                    select(contact_tags.c.contact_id).join(Tag, contact_tags.c.tag_id == Tag.id).where(Tag.name == tag)
                )
        if country:
            stmt = stmt.where(Contact.country.ilike(country))
        if city:
            stmt = stmt.where(Contact.city.ilike(city))
        if q:
            search = f"%{q}%"
                Contact.name.ilike(search)
                | Contact.email.ilike(search)
                | Contact.phone.ilike(search)
                | Contact.notes.ilike(search)
        # Fetch one extra to determine has_more
        contacts = list(result.scalars().unique().all())
        has_more = len(contacts) > per_page
            contacts = contacts[:per_page]
        next_cursor = None
        if has_more and contacts:
            next_cursor = _encode_cursor(contacts[-1].id)
        return contacts, next_cursor, has_more
    async def create(self, *, user_id: int, **data: Any) -> Contact:
        tag_ids: list[int] = data.pop("tag_ids", [])
        latitude: float | None = data.pop("latitude", None)
        longitude: float | None = data.pop("longitude", None)
        contact = Contact(user_id=user_id, **data)
        if latitude is not None and longitude is not None:
            contact.location = from_shape(Point(longitude, latitude), srid=4326)
        await self.session.flush()
        if tag_ids:
            await self._set_tags(contact, tag_ids)
        await self.session.refresh(contact, attribute_names=["tags"])
    async def update(self, contact: Contact, **data: Any) -> Contact:
        tag_ids: list[int] | None = data.pop("tag_ids", None)
        for key, value in data.items():
            setattr(contact, key, value)
        elif "latitude" in data and latitude is None:
            contact.location = None
        if tag_ids is not None:
    async def soft_delete(self, contact: Contact) -> None:
        from datetime import UTC, datetime
        contact.deleted_at = datetime.now(UTC)
    async def _set_tags(self, contact: Contact, tag_ids: list[int]) -> None:
        # Remove all existing tags
        await self.session.execute(contact_tags.delete().where(contact_tags.c.contact_id == contact.id))
        # Insert new tags
            await self.session.execute(
                contact_tags.insert(),
                [{"contact_id": contact.id, "tag_id": tid} for tid in tag_ids],
def _encode_cursor(contact_id: int) -> str:
    return base64.urlsafe_b64encode(str(contact_id).encode()).decode()
def decode_cursor(cursor: str) -> int:
    return int(base64.urlsafe_b64decode(cursor.encode()).decode())
