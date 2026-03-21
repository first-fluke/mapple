from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.redis import get_redis
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
