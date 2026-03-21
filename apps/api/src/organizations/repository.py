from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.organizations.models import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(self, query: str, limit: int = 10) -> list[Organization]:
        stmt = (
            select(Organization)
            .where(Organization.name.ilike(f"%{query}%"))
            .order_by(Organization.name)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_name_and_type(
        self, name: str, org_type: str
    ) -> Organization | None:
        stmt = select(Organization).where(
            func.lower(Organization.name) == name.lower(),
            func.lower(Organization.type) == org_type.lower(),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, name: str, org_type: str) -> Organization:
        organization = Organization(name=name, type=org_type)
        self.session.add(organization)
        await self.session.commit()
        await self.session.refresh(organization)
        return organization
