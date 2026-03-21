from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.contacts.repository import ContactRepository


class ContactService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ContactRepository(session)

    async def list_contacts(
        self,
        user_id: int,
        *,
        cursor: str | None = None,
        per_page: int = 20,
        search: str | None = None,
        sort: str = "created_at_desc",
        has_email: bool | None = None,
        has_phone: bool | None = None,
    ) -> tuple[list[Contact], str | None, bool]:
        return await self.repo.find_by_user_paginated(
            user_id,
            cursor=cursor,
            per_page=per_page,
            search=search,
            sort=sort,
            has_email=has_email,
            has_phone=has_phone,
        )
