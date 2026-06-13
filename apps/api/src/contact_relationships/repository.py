from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.contact_relationships.models import ContactRelationship


class ContactRelationshipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_contact(
        self, user_id: str, contact_id: int
    ) -> list[ContactRelationship]:
        """Return all relationships where the contact appears on either side."""
        stmt = (
            select(ContactRelationship)
            .where(
                ContactRelationship.user_id == user_id,
                (ContactRelationship.contact_id_1 == contact_id)
                | (ContactRelationship.contact_id_2 == contact_id),
            )
            .order_by(ContactRelationship.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(
        self, relationship_id: int, user_id: str
    ) -> ContactRelationship | None:
        stmt = select(ContactRelationship).where(
            ContactRelationship.id == relationship_id,
            ContactRelationship.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        user_id: str,
        contact_id_1: int,
        contact_id_2: int,
        strength: float,
    ) -> ContactRelationship:
        """Insert or update a relationship; enforces ordered IDs per DB constraint."""
        c1, c2 = sorted([contact_id_1, contact_id_2])
        stmt = (
            insert(ContactRelationship)
            .values(
                user_id=user_id,
                contact_id_1=c1,
                contact_id_2=c2,
                strength=strength,
            )
            .on_conflict_do_update(
                constraint="uq_contact_relationship_pair",
                set_={"strength": strength},
            )
            .returning(ContactRelationship)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, relationship: ContactRelationship) -> None:
        await self.session.delete(relationship)
        await self.session.commit()
