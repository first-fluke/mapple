from __future__ import annotations

import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.meetings.models import Meeting, MeetingAttendee


class MeetingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        *,
        cursor: int | None = None,
        per_page: int = 20,
        date_from: datetime.datetime | None = None,
        date_to: datetime.datetime | None = None,
        contact_id: int | None = None,
    ) -> tuple[list[Meeting], bool]:
        stmt = select(Meeting)

        if contact_id is not None:
            stmt = stmt.join(MeetingAttendee, Meeting.id == MeetingAttendee.meeting_id).where(
                MeetingAttendee.contact_id == contact_id
            )

        if date_from is not None:
            stmt = stmt.where(Meeting.start_time >= date_from)

        if date_to is not None:
            stmt = stmt.where(Meeting.start_time <= date_to)

        if cursor is not None:
            stmt = stmt.where(Meeting.id < cursor)

        stmt = stmt.order_by(Meeting.id.desc()).limit(per_page + 1)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        has_more = len(items) > per_page
        if has_more:
            items = items[:per_page]

        return items, has_more

    async def get(self, meeting_id: int) -> Meeting | None:
        stmt = select(Meeting).where(Meeting.id == meeting_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        title: str,
        description: str | None,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        location: str | None,
        attendee_contact_ids: list[int],
    ) -> Meeting:
        meeting = Meeting(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
        )
        self.session.add(meeting)
        await self.session.flush()

        for cid in attendee_contact_ids:
            self.session.add(MeetingAttendee(meeting_id=meeting.id, contact_id=cid))

        await self.session.commit()
        await self.session.refresh(meeting)
        return meeting

    async def update(
        self,
        meeting: Meeting,
        *,
        title: str,
        description: str | None,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        location: str | None,
        attendee_contact_ids: list[int],
    ) -> Meeting:
        meeting.title = title
        meeting.description = description
        meeting.start_time = start_time
        meeting.end_time = end_time
        meeting.location = location

        await self.session.execute(delete(MeetingAttendee).where(MeetingAttendee.meeting_id == meeting.id))
        for cid in attendee_contact_ids:
            self.session.add(MeetingAttendee(meeting_id=meeting.id, contact_id=cid))

        await self.session.commit()
        await self.session.refresh(meeting)
        return meeting

    async def delete(self, meeting: Meeting) -> None:
        await self.session.delete(meeting)
        await self.session.commit()

    async def get_attendee_contact_ids(self, meeting_id: int) -> list[int]:
        stmt = (
            select(MeetingAttendee.contact_id)
            .where(MeetingAttendee.meeting_id == meeting_id)
            .order_by(MeetingAttendee.contact_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_attendee_contact_ids_bulk(self, meeting_ids: list[int]) -> dict[int, list[int]]:
        stmt = (
            select(MeetingAttendee.meeting_id, MeetingAttendee.contact_id)
            .where(MeetingAttendee.meeting_id.in_(meeting_ids))
            .order_by(MeetingAttendee.meeting_id, MeetingAttendee.contact_id)
        )
        result = await self.session.execute(stmt)
        mapping: dict[int, list[int]] = {}
        for row in result.all():
            mapping.setdefault(row.meeting_id, []).append(row.contact_id)
        return mapping
