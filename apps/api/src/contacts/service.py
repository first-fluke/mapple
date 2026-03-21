from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.contacts.repository import ContactRepository
from src.lib.exceptions import NotFoundException


class ContactService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ContactRepository(session)

    async def list_contacts(
        self,
        *,
        user_id: int,
        cursor: int | None = None,
        per_page: int = 20,
        search: str | None = None,
        sort: str = "created_at_desc",
    ) -> tuple[list[Contact], bool]:
        return await self.repo.find_paginated(
            user_id=user_id, cursor=cursor, per_page=per_page, search=search, sort=sort,
        )

    async def get_contact(self, *, user_id: int, contact_id: int) -> Contact:
        contact = await self.repo.find_by_id(contact_id, user_id)
        if not contact:
            raise NotFoundException(message=f"Contact {contact_id} not found")
        return contact

    async def create(self, *, user_id: int, name: str, email: str | None, phone: str | None) -> Contact:
        return await self.repo.create(user_id=user_id, name=name, email=email, phone=phone)

    async def update(
        self, *, user_id: int, contact_id: int, name: str | None = None, email: str | None = None, phone: str | None = None,
    ) -> Contact:
        contact = await self.repo.find_by_id(contact_id, user_id)
        if not contact:
            raise NotFoundException(message=f"Contact {contact_id} not found")
        return await self.repo.update(contact, name=name, email=email, phone=phone)

    async def delete(self, *, user_id: int, contact_id: int) -> None:
        contact = await self.repo.find_by_id(contact_id, user_id)
        if not contact:
            raise NotFoundException(message=f"Contact {contact_id} not found")
        await self.repo.delete(contact)
