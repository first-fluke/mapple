from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.contacts.repository import ContactRepository
from src.contacts.schemas import ExperienceInput
from src.experiences.models import Experience
from src.lib.exceptions import NotFoundException


class ContactService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ContactRepository(session)

    async def list_by_user(self, user_id: int) -> list[dict]:
        contacts = await self.repo.find_by_user(user_id)
        results = []
        for contact in contacts:
            tags = await self.repo.get_tags(contact.id)
            experiences = await self.repo.get_experiences(contact.id)
            results.append(
                {
                    "contact": contact,
                    "tags": tags,
                    "experiences": experiences,
                }
            )
        return results

    async def get(self, *, contact_id: int, user_id: int) -> dict:
        contact = await self.repo.find_by_id(contact_id, user_id)
        if not contact:
            raise NotFoundException(message=f"Contact {contact_id} not found")
        tags = await self.repo.get_tags(contact.id)
        experiences = await self.repo.get_experiences(contact.id)
        return {"contact": contact, "tags": tags, "experiences": experiences}

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
        tag_ids: list[int],
        experiences: list[ExperienceInput],
    ) -> dict:
        contact = await self.repo.create(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            country=country,
            city=city,
        )
        if tag_ids:
            await self.repo.set_tags(contact.id, tag_ids)
        for exp in experiences:
            self.session.add(
                Experience(
                    contact_id=contact.id,
                    organization_id=exp.organization_id,
                    role=exp.role,
                    major=exp.major,
                )
            )
        await self.session.commit()
        await self.session.refresh(contact)
        tags = await self.repo.get_tags(contact.id)
        exps = await self.repo.get_experiences(contact.id)
        return {"contact": contact, "tags": tags, "experiences": exps}

    async def update(
        self,
        *,
        contact_id: int,
        user_id: int,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        country: str | None = None,
        city: str | None = None,
        tag_ids: list[int] | None = None,
    ) -> dict:
        contact = await self.repo.find_by_id(contact_id, user_id)
        if not contact:
            raise NotFoundException(message=f"Contact {contact_id} not found")
        contact = await self.repo.update(
            contact,
            name=name,
            email=email,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            country=country,
            city=city,
        )
        if tag_ids is not None:
            await self.repo.set_tags(contact.id, tag_ids)
        await self.session.commit()
        await self.session.refresh(contact)
        tags = await self.repo.get_tags(contact.id)
        experiences = await self.repo.get_experiences(contact.id)
        return {"contact": contact, "tags": tags, "experiences": experiences}

    async def delete(self, *, contact_id: int, user_id: int) -> None:
        contact = await self.repo.find_by_id(contact_id, user_id)
        if not contact:
            raise NotFoundException(message=f"Contact {contact_id} not found")
        await self.repo.delete(contact)
        await self.session.commit()
