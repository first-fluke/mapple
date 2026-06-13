from sqlalchemy.ext.asyncio import AsyncSession

from src.contact_relationships.models import ContactRelationship
from src.contact_relationships.repository import ContactRelationshipRepository
from src.contact_relationships.schemas import ContactRelationshipCreate
from src.lib.exceptions import ForbiddenException, NotFoundException


class ContactRelationshipCRUDService:
    """CRUD operations for contact relationships, scoped to the authenticated user."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = ContactRelationshipRepository(session)

    async def list_for_contact(
        self, user_id: str, contact_id: int
    ) -> list[ContactRelationship]:
        return await self.repo.find_by_contact(user_id, contact_id)

    async def create(
        self, user_id: str, data: ContactRelationshipCreate
    ) -> ContactRelationship:
        if data.contact_id_1 == data.contact_id_2:
            raise ForbiddenException(message="A contact cannot have a relationship with itself")
        return await self.repo.upsert(
            user_id=user_id,
            contact_id_1=data.contact_id_1,
            contact_id_2=data.contact_id_2,
            strength=data.strength,
        )

    async def delete(self, user_id: str, relationship_id: int) -> None:
        rel = await self.repo.find_by_id(relationship_id, user_id)
        if rel is None:
            raise NotFoundException(message=f"Relationship {relationship_id} not found")
        await self.repo.delete(rel)
