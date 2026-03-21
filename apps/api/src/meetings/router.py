from fastapi import APIRouter, Depends
from redis.asyncio import Redis
import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.redis import get_redis
from src.lib.pagination import decode_cursor, encode_cursor, paginate_cursor
from src.meetings.schemas import MeetingCreate, MeetingOut, MeetingUpdate
from src.meetings.service import MeetingService

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("")
async def list_meetings(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[list[MeetingOut]]:
    """List all meetings for the current user."""
    service = MeetingService(session, redis)
    meetings = await service.list_by_user(user_id)
    return ApiResponse(data=meetings)


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[MeetingOut]:
    """Get a meeting by ID."""
    service = MeetingService(session, redis)
    meeting = await service.get(user_id=user_id, meeting_id=meeting_id)
    return ApiResponse(data=meeting)
def _to_out(meeting, attendee_contact_ids: list[int]) -> MeetingOut:
    return MeetingOut(
        id=meeting.id,
        title=meeting.title,
        description=meeting.description,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        location=meeting.location,
        attendee_contact_ids=attendee_contact_ids,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )
    cursor: str | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    date_from: datetime.datetime | None = Query(default=None),
    date_to: datetime.datetime | None = Query(default=None),
    contact_id: int | None = Query(default=None),
    _user_id: int = Depends(get_current_user_id),
    """List meetings with cursor pagination and optional filters."""
    decoded_cursor = decode_cursor(cursor) if cursor else None
    service = MeetingService(session)
    meetings, attendees_map, has_more = await service.list(
        cursor=decoded_cursor,
        per_page=per_page,
        date_from=date_from,
        date_to=date_to,
        contact_id=contact_id,
    data = [_to_out(m, attendees_map.get(m.id, [])) for m in meetings]
    next_cursor = encode_cursor(meetings[-1].id) if has_more and meetings else None
    return paginate_cursor(data, per_page=per_page, next_cursor=next_cursor, has_more=has_more)


@router.post("", status_code=201)
async def create_meeting(
    body: MeetingCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[MeetingOut]:
    """Create a new meeting with participants."""
    service = MeetingService(session, redis)
    meeting = await service.create(
        user_id=user_id,
        title=body.title,
        scheduled_at=body.scheduled_at,
        location=body.location,
        notes=body.notes,
        participant_ids=body.participant_ids,
    )
    return ApiResponse(data=meeting)
    _user_id: int = Depends(get_current_user_id),
    """Create a meeting with optional attendee contact IDs."""
    service = MeetingService(session)
    meeting, attendee_ids = await service.create(
        description=body.description,
        start_time=body.start_time,
        end_time=body.end_time,
        attendee_contact_ids=body.attendee_contact_ids,
    return ApiResponse(data=_to_out(meeting, attendee_ids))

@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    """Get a meeting by ID."""
    meeting, attendee_ids = await service.get(meeting_id)


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    body: MeetingUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[MeetingOut]:
    """Update a meeting."""
    service = MeetingService(session, redis)
    meeting = await service.update(
        user_id=user_id,
        meeting_id=meeting_id,
        title=body.title,
        scheduled_at=body.scheduled_at,
        location=body.location,
        notes=body.notes,
        participant_ids=body.participant_ids,
    )
    return ApiResponse(data=meeting)
    _user_id: int = Depends(get_current_user_id),
    """Update a meeting (full replacement)."""
    service = MeetingService(session)
    meeting, attendee_ids = await service.update(
        meeting_id,
        description=body.description,
        start_time=body.start_time,
        end_time=body.end_time,
        attendee_contact_ids=body.attendee_contact_ids,
    return ApiResponse(data=_to_out(meeting, attendee_ids))


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> None:
    """Delete a meeting."""
    service = MeetingService(session, redis)
    await service.delete(user_id=user_id, meeting_id=meeting_id)
    _user_id: int = Depends(get_current_user_id),
    service = MeetingService(session)
    await service.delete(meeting_id)
