from itertools import combinations

from redis.asyncio import Redis
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.contact_relationships.models import ContactRelationship
from src.meetings.models import MeetingParticipant


class ContactRelationshipService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis

    async def recompute_strength_for_contacts(self, user_id: str, contact_ids: list[int]) -> None:
        """Recompute relationship strength for all pairs among the given contacts."""
        if len(contact_ids) < 2:
            return

        pairs = list(combinations(sorted(set(contact_ids)), 2))

        for c1, c2 in pairs:
            shared_count = await self._count_shared_meetings(c1, c2)
            if shared_count > 0:
                await self._upsert_relationship(user_id, c1, c2, float(shared_count))
            else:
                await self._delete_relationship(user_id, c1, c2)

        await self.session.commit()
        await self._invalidate_globe_cache(user_id)

    async def _count_shared_meetings(self, contact_id_1: int, contact_id_2: int) -> int:
        """Count meetings that both contacts participate in."""
        mp1 = MeetingParticipant.__table__.alias("mp1")
        mp2 = MeetingParticipant.__table__.alias("mp2")

        stmt = (
            select(func.count())
            .select_from(mp1)
            .join(mp2, mp1.c.meeting_id == mp2.c.meeting_id)
            .where(mp1.c.contact_id == contact_id_1)
            .where(mp2.c.contact_id == contact_id_2)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _upsert_relationship(self, user_id: str, contact_id_1: int, contact_id_2: int, strength: float) -> None:
        """Insert or update a contact relationship."""
        stmt = (
            insert(ContactRelationship)
            .values(
                user_id=user_id,
                contact_id_1=contact_id_1,
                contact_id_2=contact_id_2,
                strength=strength,
            )
            .on_conflict_do_update(
                constraint="uq_contact_relationship_pair",
                set_={"strength": strength},
            )
        )
        await self.session.execute(stmt)

    async def _delete_relationship(self, user_id: str, contact_id_1: int, contact_id_2: int) -> None:
        """Delete a contact relationship (strength became 0)."""
        stmt = delete(ContactRelationship).where(
            ContactRelationship.user_id == user_id,
            ContactRelationship.contact_id_1 == contact_id_1,
            ContactRelationship.contact_id_2 == contact_id_2,
        )
        await self.session.execute(stmt)

    async def _invalidate_globe_cache(self, user_id: str) -> None:
        """Invalidate globe arc cache for the user."""
        await self.redis.delete(f"globe:user:{user_id}:arcs")
