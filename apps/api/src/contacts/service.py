from geoalchemy2.shape import to_shape
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.contacts.repository import ContactRepository, decode_cursor
from src.contacts.schemas import ContactCreate, ContactOut, ContactPatch, ContactUpdate, TagOut
from src.lib.exceptions import ApiResponse, NotFoundException
from src.lib.pagination import paginate_cursor


class ContactService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ContactRepository(session)

    async def get(self, *, user_id: int, contact_id: int) -> ContactOut:
        contact = await self.repo.find_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise NotFoundException(message="Contact not found")
        return _to_out(contact)

    async def list(
        self,
        *,
        user_id: int,
        per_page: int = 20,
        cursor: str | None = None,
        tag: str | None = None,
        country: str | None = None,
        city: str | None = None,
        q: str | None = None,
    ) -> ApiResponse[list[ContactOut]]:
        cursor_id = decode_cursor(cursor) if cursor else None

        contacts, next_cursor, has_more = await self.repo.list_contacts(
            user_id=user_id,
            per_page=per_page,
            cursor=cursor_id,
            tag=tag,
            country=country,
            city=city,
            q=q,
        )

        items = [_to_out(c) for c in contacts]
        return paginate_cursor(items, per_page=per_page, next_cursor=next_cursor, has_more=has_more)

    async def create(self, *, user_id: int, data: ContactCreate) -> ContactOut:
        contact = await self.repo.create(user_id=user_id, **data.model_dump())
        return _to_out(contact)

    async def update(self, *, user_id: int, contact_id: int, data: ContactUpdate) -> ContactOut:
        contact = await self.repo.find_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise NotFoundException(message="Contact not found")

        contact = await self.repo.update(contact, **data.model_dump())
        return _to_out(contact)

    async def patch(self, *, user_id: int, contact_id: int, data: ContactPatch) -> ContactOut:
        contact = await self.repo.find_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise NotFoundException(message="Contact not found")

        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return _to_out(contact)

        contact = await self.repo.update(contact, **updates)
        return _to_out(contact)

    async def delete(self, *, user_id: int, contact_id: int) -> None:
        contact = await self.repo.find_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise NotFoundException(message="Contact not found")
        await self.repo.soft_delete(contact)


def _to_out(contact: Contact) -> ContactOut:
    latitude = None
    longitude = None
    if contact.location is not None:
        point = to_shape(contact.location)
        latitude = point.y
        longitude = point.x

    return ContactOut(
        id=contact.id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        country=contact.country,
        city=contact.city,
        latitude=latitude,
        longitude=longitude,
        notes=contact.notes,
        tags=[TagOut.model_validate(t) for t in contact.tags],
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )
