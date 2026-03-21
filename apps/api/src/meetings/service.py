from __future__ import annotations

import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.exceptions import NotFoundException
from src.meetings.models import Meeting
from src.meetings.repository import MeetingRepository


class MeetingService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MeetingRepository(session)

    async def list(
        self,
        *,
        cursor: int | None = None,
        per_page: int = 20,
        date_from: datetime.datetime | None = None,
        date_to: datetime.datetime | None = None,
        contact_id: int | None = None,
    ) -> tuple[list[Meeting], dict[int, list[int]], bool]:
        meetings, has_more = await self.repo.list(
            cursor=cursor,
            per_page=per_page,
            date_from=date_from,
            date_to=date_to,
            contact_id=contact_id,
        )
        meeting_ids = [m.id for m in meetings]
        attendees_map = await self.repo.get_attendee_contact_ids_bulk(meeting_ids) if meeting_ids else {}
        return meetings, attendees_map, has_more

    async def get(self, meeting_id: int) -> tuple[Meeting, list[int]]:
        meeting = await self.repo.get(meeting_id)
        if not meeting:
            raise NotFoundException("Meeting not found")
        attendee_ids = await self.repo.get_attendee_contact_ids(meeting_id)
        return meeting, attendee_ids

    async def create(
        self,
        *,
        title: str,
        description: str | None,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        location: str | None,
        attendee_contact_ids: list[int],
    ) -> tuple[Meeting, list[int]]:
        meeting = await self.repo.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            attendee_contact_ids=attendee_contact_ids,
        )
        return meeting, attendee_contact_ids

    async def update(
        self,
        meeting_id: int,
        *,
        title: str,
        description: str | None,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        location: str | None,
        attendee_contact_ids: list[int],
    ) -> tuple[Meeting, list[int]]:
        meeting = await self.repo.get(meeting_id)
        if not meeting:
            raise NotFoundException("Meeting not found")
        meeting = await self.repo.update(
            meeting,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            attendee_contact_ids=attendee_contact_ids,
        )
        return meeting, attendee_contact_ids

    async def delete(self, meeting_id: int) -> None:
        meeting = await self.repo.get(meeting_id)
        if not meeting:
            raise NotFoundException("Meeting not found")
        await self.repo.delete(meeting)
