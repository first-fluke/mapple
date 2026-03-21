from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.pagination import decode_cursor, encode_cursor, paginate_cursor
from src.meetings.schemas import MeetingOut
from src.meetings.service import MeetingService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/{contact_id}/meetings")
async def list_contact_meetings(
    contact_id: int,
    cursor: str | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    _user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[MeetingOut]]:
    """List meetings for a specific contact."""
    decoded_cursor = decode_cursor(cursor) if cursor else None
    service = MeetingService(session)
    meetings, attendees_map, has_more = await service.list(
        cursor=decoded_cursor,
        per_page=per_page,
        contact_id=contact_id,
    )
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
