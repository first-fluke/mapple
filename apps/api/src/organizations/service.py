from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.exceptions import AppException
from src.organizations.models import Organization
from src.organizations.repository import OrganizationRepository


class OrganizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = OrganizationRepository(session)

    async def search(self, query: str) -> list[Organization]:
        return await self.repo.search(query)

    async def create(self, *, name: str, org_type: str) -> Organization:
        existing = await self.repo.find_by_name_and_type(name, org_type)
        if existing:
            raise AppException(
                status_code=409,
                code="DUPLICATE_ORGANIZATION",
                message=f"Organization '{name}' with type '{org_type}' already exists",
            )
        return await self.repo.create(name=name, org_type=org_type)
