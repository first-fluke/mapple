import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.exceptions import NotFoundException
from src.meetings.models import Meeting
from src.meetings.repository import MeetingRepository


class MeetingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = MeetingRepository(session)

    async def list_meetings(
        self,
        *,
        user_id: str,
        cursor: int | None = None,
        per_page: int = 20,
        date_from: datetime.datetime | None = None,
        date_to: datetime.datetime | None = None,
        contact_id: int | None = None,
    ) -> tuple[list[dict], bool]:
        meetings, has_more = await self.repo.find_paginated(
            user_id=user_id,
            cursor=cursor,
            per_page=per_page,
            date_from=date_from,
            date_to=date_to,
            contact_id=contact_id,
        )
        enriched = []
        for m in meetings:
            ids = await self.repo.get_attendee_contact_ids(m.id)
            enriched.append(_meeting_with_attendees(m, ids))
        return enriched, has_more

    async def get_meeting(self, *, user_id: str, meeting_id: int) -> dict:
        meeting = await self._find_or_raise(meeting_id, user_id)
        ids = await self.repo.get_attendee_contact_ids(meeting.id)
        return _meeting_with_attendees(meeting, ids)

    async def create(
        self,
        *,
        user_id: str,
        title: str,
        description: str | None,
        starts_at: datetime.datetime,
        ends_at: datetime.datetime | None,
        location: str | None,
        attendee_contact_ids: list[int],
    ) -> dict:
        meeting = await self.repo.create(
            user_id=user_id,
            title=title,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            location=location,
        )
        if attendee_contact_ids:
            await self.repo.set_attendees(meeting.id, attendee_contact_ids)
        await self.session.commit()
        await self.session.refresh(meeting)
        ids = await self.repo.get_attendee_contact_ids(meeting.id)
        return _meeting_with_attendees(meeting, ids)

    async def update(
        self,
        *,
        user_id: str,
        meeting_id: int,
        title: str | None = None,
        description: str | None = None,
        starts_at: datetime.datetime | None = None,
        ends_at: datetime.datetime | None = None,
        location: str | None = None,
        attendee_contact_ids: list[int] | None = None,
    ) -> dict:
        meeting = await self._find_or_raise(meeting_id, user_id)
        meeting = await self.repo.update(
            meeting,
            title=title,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            location=location,
        )
        if attendee_contact_ids is not None:
            await self.repo.set_attendees(meeting.id, attendee_contact_ids)
        await self.session.commit()
        await self.session.refresh(meeting)
        ids = await self.repo.get_attendee_contact_ids(meeting.id)
        return _meeting_with_attendees(meeting, ids)

    async def delete(self, *, user_id: str, meeting_id: int) -> None:
        meeting = await self._find_or_raise(meeting_id, user_id)
        await self.repo.delete(meeting)
        await self.session.commit()

    async def list_by_contact(
        self,
        *,
        user_id: str,
        contact_id: int,
        cursor: int | None = None,
        per_page: int = 20,
    ) -> tuple[list[dict], bool]:
        meetings, has_more = await self.repo.find_by_contact(
            user_id=user_id,
            contact_id=contact_id,
            cursor=cursor,
            per_page=per_page,
        )
        enriched = []
        for m in meetings:
            ids = await self.repo.get_attendee_contact_ids(m.id)
            enriched.append(_meeting_with_attendees(m, ids))
        return enriched, has_more

    async def _find_or_raise(self, meeting_id: int, user_id: str) -> Meeting:
        meeting = await self.repo.find_by_id(meeting_id, user_id)
        if not meeting:
            raise NotFoundException(message=f"Meeting {meeting_id} not found")
        return meeting


def _meeting_with_attendees(meeting: Meeting, contact_ids: list[int]) -> dict:
    return {
        "id": meeting.id,
        "user_id": meeting.user_id,
        "title": meeting.title,
        "description": meeting.description,
        "starts_at": meeting.starts_at,
        "ends_at": meeting.ends_at,
        "location": meeting.location,
        "attendee_contact_ids": contact_ids,
        "created_at": meeting.created_at,
        "updated_at": meeting.updated_at,
    }
