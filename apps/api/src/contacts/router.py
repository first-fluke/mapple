from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.schemas import ContactCreate, ContactOut, ContactUpdate
from src.contacts.schemas import ContactCreate, ContactOut, ContactPatch, ContactUpdate
from src.contacts.service import ContactService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.pagination import paginate_cursor
from src.lib.pagination import decode_cursor, encode_cursor, paginate_cursor
from src.meetings.schemas import MeetingOut
from src.meetings.service import MeetingService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("")
async def list_contacts(
    cursor: int | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    sort: str = Query(default="created_at_desc"),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ContactOut]]:
    """List contacts with cursor-based pagination, search, and sort."""
    service = ContactService(session)
    contacts, has_more = await service.list_contacts(
        user_id=user_id, cursor=cursor, per_page=per_page, search=search, sort=sort,
    )
    items = [ContactOut.model_validate(c) for c in contacts]
    next_cursor = str(items[-1].id) if items and has_more else None
    return paginate_cursor(items, per_page=per_page, next_cursor=next_cursor, has_more=has_more)


@router.get("/{contact_id}")
async def get_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Get a single contact."""
    service = ContactService(session)
    contact = await service.get_contact(user_id=user_id, contact_id=contact_id)
    return ApiResponse(data=ContactOut.model_validate(contact))
    tag: str | None = Query(default=None),
    country: str | None = Query(default=None),
    city: str | None = Query(default=None),
    q: str | None = Query(default=None),
    cursor: str | None = Query(default=None),
    return await service.list(
        user_id=user_id,
        per_page=per_page,
        cursor=cursor,
        tag=tag,
        country=country,
        city=city,
        q=q,


@router.post("", status_code=201)
async def create_contact(
    body: ContactCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Create a new contact."""
    service = ContactService(session)
    contact = await service.create(user_id=user_id, name=body.name, email=body.email, phone=body.phone)
    return ApiResponse(data=ContactOut.model_validate(contact))
    contact = await service.create(user_id=user_id, data=body)
    await session.commit()
    return ApiResponse(data=contact)

@router.get("/{contact_id}")
async def get_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    contact = await service.get(user_id=user_id, contact_id=contact_id)


@router.put("/{contact_id}")
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Update a contact."""
    service = ContactService(session)
    contact = await service.update(
        user_id=user_id, contact_id=contact_id, name=body.name, email=body.email, phone=body.phone,
    )
    return ApiResponse(data=ContactOut.model_validate(contact))
    contact = await service.update(user_id=user_id, contact_id=contact_id, data=body)
    await session.commit()
    return ApiResponse(data=contact)

@router.patch("/{contact_id}")
async def patch_contact(
    contact_id: int,
    body: ContactPatch,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    contact = await service.patch(user_id=user_id, contact_id=contact_id, data=body)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a contact."""
    service = ContactService(session)
    await service.delete(user_id=user_id, contact_id=contact_id)
    await session.commit()
@router.get("/{contact_id}/meetings")
async def list_contact_meetings(
    _user_id: int = Depends(get_current_user_id),
) -> ApiResponse[list[MeetingOut]]:
    """List meetings for a specific contact."""
    decoded_cursor = decode_cursor(cursor) if cursor else None
    service = MeetingService(session)
    meetings, attendees_map, has_more = await service.list(
        cursor=decoded_cursor,
        contact_id=contact_id,
    data = [
        MeetingOut(
            id=m.id,
            title=m.title,
            description=m.description,
            start_time=m.start_time,
            end_time=m.end_time,
            location=m.location,
            attendee_contact_ids=attendees_map.get(m.id, []),
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in meetings
    ]
    next_cursor = encode_cursor(meetings[-1].id) if has_more and meetings else None
    return paginate_cursor(data, per_page=per_page, next_cursor=next_cursor, has_more=has_more)
