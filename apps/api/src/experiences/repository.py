from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.experiences.models import Experience


class ExperienceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_contact(self, contact_id: int) -> list[Experience]:
        stmt = (
            select(Experience)
            .where(Experience.contact_id == contact_id)
            .order_by(Experience.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(
        self, experience_id: int, contact_id: int
    ) -> Experience | None:
        stmt = select(Experience).where(
            Experience.id == experience_id,
            Experience.contact_id == contact_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        contact_id: int,
        organization_id: int,
        role: str | None,
        major: str | None,
    ) -> Experience:
        experience = Experience(
            contact_id=contact_id,
            organization_id=organization_id,
            role=role,
            major=major,
        )
        self.session.add(experience)
        await self.session.commit()
        await self.session.refresh(experience)
        return experience

    async def update(
        self,
        experience: Experience,
        *,
        organization_id: int | None = None,
        role: str | None = None,
        major: str | None = None,
    ) -> Experience:
        if organization_id is not None:
            experience.organization_id = organization_id
        if role is not None:
            experience.role = role
        if major is not None:
            experience.major = major
        await self.session.commit()
        await self.session.refresh(experience)
        return experience

    async def delete(self, experience: Experience) -> None:
        await self.session.delete(experience)
        await self.session.commit()
