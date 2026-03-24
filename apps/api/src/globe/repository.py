import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact


class GlobeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_contacts_with_location(
        self, user_id: str, *, limit: int = 200
    ) -> list[Contact]:
        stmt = (
            select(Contact)
            .where(
                Contact.user_id == uuid.UUID(user_id),
                Contact.latitude.is_not(None),
                Contact.longitude.is_not(None),
            )
            .order_by(Contact.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
