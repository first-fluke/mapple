import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.pagination import paginate_cursor
from src.meetings.schemas import MeetingCreate, MeetingOut, MeetingUpdate
from src.meetings.service import MeetingService

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("")
async def list_meetings(
    cursor: int | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    date_from: datetime.datetime | None = Query(default=None),
    date_to: datetime.datetime | None = Query(default=None),
    contact_id: int | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[MeetingOut]]:
    service = MeetingService(session)
    meetings, has_more = await service.list_meetings(
        user_id=user_id,
        cursor=cursor,
        per_page=per_page,
        date_from=date_from,
        date_to=date_to,
        contact_id=contact_id,
    )
    items = [MeetingOut.model_validate(m) for m in meetings]
    next_cursor = str(items[-1].id) if items and has_more else None
    return paginate_cursor(items, per_page=per_page, next_cursor=next_cursor, has_more=has_more)


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[MeetingOut]:
    service = MeetingService(session)
    meeting = await service.get_meeting(user_id=user_id, meeting_id=meeting_id)
    return ApiResponse(data=MeetingOut.model_validate(meeting))


@router.post("", status_code=201)
async def create_meeting(
    body: MeetingCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[MeetingOut]:
    service = MeetingService(session)
    meeting = await service.create(
        user_id=user_id,
        title=body.title,
        description=body.description,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
        location=body.location,
        attendee_contact_ids=body.attendee_contact_ids,
    )
    return ApiResponse(data=MeetingOut.model_validate(meeting))


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    body: MeetingUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[MeetingOut]:
    service = MeetingService(session)
    meeting = await service.update(
        user_id=user_id,
        meeting_id=meeting_id,
        title=body.title,
        description=body.description,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
        location=body.location,
        attendee_contact_ids=body.attendee_contact_ids,
    )
    return ApiResponse(data=MeetingOut.model_validate(meeting))


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    service = MeetingService(session)
    await service.delete(user_id=user_id, meeting_id=meeting_id)
