import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.meetings.models import Meeting, MeetingAttendee


class MeetingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_paginated(
        self,
        *,
        user_id: str,
        cursor: int | None = None,
        per_page: int = 20,
        date_from: datetime.datetime | None = None,
        date_to: datetime.datetime | None = None,
        contact_id: int | None = None,
    ) -> tuple[list[Meeting], bool]:
        stmt = select(Meeting).where(Meeting.user_id == user_id)
        if date_from:
            stmt = stmt.where(Meeting.starts_at >= date_from)
        if date_to:
            stmt = stmt.where(Meeting.starts_at <= date_to)
        if contact_id:
            stmt = stmt.where(
                Meeting.id.in_(
                    select(MeetingAttendee.meeting_id).where(
                        MeetingAttendee.contact_id == contact_id
                    )
                )
            )
        if cursor:
            stmt = stmt.where(Meeting.id < cursor)
        stmt = stmt.order_by(Meeting.id.desc()).limit(per_page + 1)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        has_more = len(items) > per_page
        if has_more:
            items = items[:per_page]
        return items, has_more

    async def find_by_id(self, meeting_id: int, user_id: str) -> Meeting | None:
        stmt = select(Meeting).where(Meeting.id == meeting_id, Meeting.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: str,
        title: str,
        description: str | None,
        starts_at: datetime.datetime,
        ends_at: datetime.datetime | None,
        location: str | None,
    ) -> Meeting:
        meeting = Meeting(
            user_id=user_id,
            title=title,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            location=location,
        )
        self.session.add(meeting)
        await self.session.flush()
        await self.session.refresh(meeting)
        return meeting

    async def update(
        self,
        meeting: Meeting,
        *,
        title: str | None = None,
        description: str | None = None,
        starts_at: datetime.datetime | None = None,
        ends_at: datetime.datetime | None = None,
        location: str | None = None,
    ) -> Meeting:
        if title is not None:
            meeting.title = title
        if description is not None:
            meeting.description = description
        if starts_at is not None:
            meeting.starts_at = starts_at
        if ends_at is not None:
            meeting.ends_at = ends_at
        if location is not None:
            meeting.location = location
        await self.session.flush()
        await self.session.refresh(meeting)
        return meeting

    async def delete(self, meeting: Meeting) -> None:
        await self.session.delete(meeting)
        await self.session.flush()

    async def get_attendee_contact_ids(self, meeting_id: int) -> list[int]:
        stmt = (
            select(MeetingAttendee.contact_id)
            .where(MeetingAttendee.meeting_id == meeting_id)
            .order_by(MeetingAttendee.contact_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_attendees(self, meeting_id: int, contact_ids: list[int]) -> None:
        await self.session.execute(
            delete(MeetingAttendee).where(MeetingAttendee.meeting_id == meeting_id)
        )
        for cid in contact_ids:
            self.session.add(MeetingAttendee(meeting_id=meeting_id, contact_id=cid))
        await self.session.flush()

    async def find_by_contact(
        self,
        *,
        user_id: str,
        contact_id: int,
        cursor: int | None = None,
        per_page: int = 20,
    ) -> tuple[list[Meeting], bool]:
        stmt = (
            select(Meeting)
            .where(
                Meeting.user_id == user_id,
                Meeting.id.in_(
                    select(MeetingAttendee.meeting_id).where(
                        MeetingAttendee.contact_id == contact_id
                    )
                ),
            )
        )
        if cursor:
            stmt = stmt.where(Meeting.id < cursor)
        stmt = stmt.order_by(Meeting.id.desc()).limit(per_page + 1)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        has_more = len(items) > per_page
        if has_more:
            items = items[:per_page]
        return items, has_more
