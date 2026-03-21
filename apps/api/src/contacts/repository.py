import base64
from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.contacts.models import Contact, contact_tags
from src.tags.models import Tag


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_contacts(
        self,
        *,
        user_id: int,
        per_page: int = 20,
        cursor: int | None = None,
        tag: str | None = None,
        country: str | None = None,
        city: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Contact], str | None, bool]:
        stmt = (
            select(Contact)
            .options(selectinload(Contact.tags))
            .where(
                Contact.user_id == user_id,
                Contact.deleted_at.is_(None),
            )
            .order_by(Contact.id.desc())
        )

        if cursor is not None:
            stmt = stmt.where(Contact.id < cursor)

        if tag:
            stmt = stmt.where(
                Contact.id.in_(
                    select(contact_tags.c.contact_id).join(Tag, contact_tags.c.tag_id == Tag.id).where(Tag.name == tag)
                )
            )

        if country:
            stmt = stmt.where(Contact.country.ilike(country))

        if city:
            stmt = stmt.where(Contact.city.ilike(city))

        if q:
            search = f"%{q}%"
            stmt = stmt.where(
                Contact.name.ilike(search)
                | Contact.email.ilike(search)
                | Contact.phone.ilike(search)
                | Contact.notes.ilike(search)
            )

        # Fetch one extra to determine has_more
        stmt = stmt.limit(per_page + 1)

        result = await self.session.execute(stmt)
        contacts = list(result.scalars().unique().all())

        has_more = len(contacts) > per_page
        if has_more:
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

        self.session.add(contact)
        await self.session.flush()

        if tag_ids:
            await self._set_tags(contact, tag_ids)

        await self.session.refresh(contact, attribute_names=["tags"])
        return contact

    async def update(self, contact: Contact, **data: Any) -> Contact:
        tag_ids: list[int] | None = data.pop("tag_ids", None)
        latitude: float | None = data.pop("latitude", None)
        longitude: float | None = data.pop("longitude", None)

        for key, value in data.items():
            setattr(contact, key, value)

        if latitude is not None and longitude is not None:
            contact.location = from_shape(Point(longitude, latitude), srid=4326)
        elif "latitude" in data and latitude is None:
            contact.location = None

        if tag_ids is not None:
            await self._set_tags(contact, tag_ids)

        await self.session.flush()
        await self.session.refresh(contact, attribute_names=["tags"])
        return contact

    async def soft_delete(self, contact: Contact) -> None:
        from datetime import UTC, datetime

        contact.deleted_at = datetime.now(UTC)
        await self.session.flush()

    async def _set_tags(self, contact: Contact, tag_ids: list[int]) -> None:
        # Remove all existing tags
        await self.session.execute(contact_tags.delete().where(contact_tags.c.contact_id == contact.id))

        # Insert new tags
        if tag_ids:
            await self.session.execute(
                contact_tags.insert(),
                [{"contact_id": contact.id, "tag_id": tid} for tid in tag_ids],
            )


def _encode_cursor(contact_id: int) -> str:
    return base64.urlsafe_b64encode(str(contact_id).encode()).decode()


def decode_cursor(cursor: str) -> int:
    return int(base64.urlsafe_b64decode(cursor.encode()).decode())
