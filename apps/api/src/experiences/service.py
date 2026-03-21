from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.experiences.models import Experience
from src.experiences.repository import ExperienceRepository
from src.lib.exceptions import NotFoundException


class ExperienceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ExperienceRepository(session)

    async def _ensure_contact_exists(self, contact_id: int) -> None:
        contact = await self.session.get(Contact, contact_id)
        if not contact:
            raise NotFoundException(message=f"Contact {contact_id} not found")

    async def list_by_contact(self, contact_id: int) -> list[Experience]:
        await self._ensure_contact_exists(contact_id)
        return await self.repo.find_by_contact(contact_id)

    async def create(
        self,
        *,
        contact_id: int,
        organization_id: int,
        role: str | None,
        major: str | None,
    ) -> Experience:
        await self._ensure_contact_exists(contact_id)
        return await self.repo.create(
            contact_id=contact_id,
            organization_id=organization_id,
            role=role,
            major=major,
        )

    async def update(
        self,
        *,
        contact_id: int,
        experience_id: int,
        organization_id: int | None = None,
        role: str | None = None,
        major: str | None = None,
    ) -> Experience:
        experience = await self.repo.find_by_id(experience_id, contact_id)
        if not experience:
            raise NotFoundException(message=f"Experience {experience_id} not found")
        return await self.repo.update(
            experience,
            organization_id=organization_id,
            role=role,
            major=major,
        )

    async def delete(self, *, contact_id: int, experience_id: int) -> None:
        experience = await self.repo.find_by_id(experience_id, contact_id)
        if not experience:
            raise NotFoundException(message=f"Experience {experience_id} not found")
        await self.repo.delete(experience)
