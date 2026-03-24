from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.schemas import ContactCreate, ContactOut, ContactUpdate
from src.contacts.service import ContactService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.pagination import paginate_cursor
from src.meetings.schemas import MeetingOut
from src.meetings.service import MeetingService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("")
async def list_contacts(
    cursor: int | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, max_length=255),
    tag: str | None = Query(default=None, max_length=100),
    country: str | None = Query(default=None, max_length=100),
    city: str | None = Query(default=None, max_length=100),
    sort: str = Query(default="created_at_desc"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ContactOut]]:
    """List contacts with cursor-based pagination and filters."""
    service = ContactService(session)
    contacts, has_more = await service.list_contacts(
        user_id=user_id,
        cursor=cursor,
        per_page=per_page,
        q=q,
        tag=tag,
        country=country,
        city=city,
        sort=sort,
    )
    items = [ContactOut.model_validate(c) for c in contacts]
    next_cursor = str(items[-1].id) if items and has_more else None
    return paginate_cursor(items, per_page=per_page, next_cursor=next_cursor, has_more=has_more)


@router.get("/{contact_id}")
async def get_contact(
    contact_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Get a single contact."""
    service = ContactService(session)
    contact = await service.get_contact(user_id=user_id, contact_id=contact_id)
    return ApiResponse(data=ContactOut.model_validate(contact))


@router.post("", status_code=201)
async def create_contact(
    body: ContactCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Create a new contact."""
    service = ContactService(session)
    contact = await service.create(
        user_id=user_id,
        name=body.name,
        email=body.email,
        phone=body.phone,
        country=body.country,
        city=body.city,
        tags=body.tags,
    )
    return ApiResponse(data=ContactOut.model_validate(contact))


@router.put("/{contact_id}")
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Full update of a contact."""
    service = ContactService(session)
    contact = await service.update(
        user_id=user_id,
        contact_id=contact_id,
        name=body.name,
        email=body.email,
        phone=body.phone,
        country=body.country,
        city=body.city,
        tags=body.tags,
    )
    return ApiResponse(data=ContactOut.model_validate(contact))


@router.patch("/{contact_id}")
async def patch_contact(
    contact_id: int,
    body: ContactUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Partial update of a contact."""
    service = ContactService(session)
    updates = body.model_dump(exclude_unset=True)
    contact = await service.update(
        user_id=user_id,
        contact_id=contact_id,
        **updates,
    )
    return ApiResponse(data=ContactOut.model_validate(contact))


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Soft-delete a contact."""
    service = ContactService(session)
    await service.delete(user_id=user_id, contact_id=contact_id)


@router.get("/{contact_id}/meetings")
async def list_contact_meetings(
    contact_id: int,
    cursor: int | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[MeetingOut]]:
    """List meetings for a specific contact."""
    meeting_service = MeetingService(session)
    meetings, has_more = await meeting_service.list_by_contact(
        user_id=user_id, contact_id=contact_id, cursor=cursor, per_page=per_page,
    )
    items = [MeetingOut.model_validate(m) for m in meetings]
    next_cursor = str(items[-1].id) if items and has_more else None
    return paginate_cursor(items, per_page=per_page, next_cursor=next_cursor, has_more=has_more)
