from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.experiences.models import Experience
from src.tags.models import ContactTag, Tag


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_user(self, user_id: int) -> list[Contact]:
        stmt = (
            select(Contact)
            .where(Contact.user_id == user_id)
            .order_by(Contact.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, contact_id: int, user_id: int) -> Contact | None:
        stmt = select(Contact).where(
            Contact.id == contact_id,
            Contact.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: int,
        name: str,
        email: str | None,
        phone: str | None,
        latitude: float | None,
        longitude: float | None,
        country: str | None,
        city: str | None,
    ) -> Contact:
        contact = Contact(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            country=country,
            city=city,
        )
        self.session.add(contact)
        await self.session.flush()
        return contact

    async def update(
        self,
        contact: Contact,
        *,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        country: str | None = None,
        city: str | None = None,
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
        if country is not None:
            contact.country = country
        if city is not None:
            contact.city = city
        await self.session.flush()
        return contact

    async def delete(self, contact: Contact) -> None:
        await self.session.delete(contact)
        await self.session.flush()

    async def get_tags(self, contact_id: int) -> list[Tag]:
        stmt = (
            select(Tag)
            .join(ContactTag, Tag.id == ContactTag.tag_id)
            .where(ContactTag.contact_id == contact_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_tags(self, contact_id: int, tag_ids: list[int]) -> None:
        # Remove existing tags
        stmt = select(ContactTag).where(ContactTag.contact_id == contact_id)
        result = await self.session.execute(stmt)
        for ct in result.scalars().all():
            await self.session.delete(ct)
        # Add new tags
        for tag_id in tag_ids:
            self.session.add(ContactTag(contact_id=contact_id, tag_id=tag_id))
        await self.session.flush()

    async def get_experiences(self, contact_id: int) -> list[Experience]:
        stmt = (
            select(Experience)
            .where(Experience.contact_id == contact_id)
            .order_by(Experience.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
