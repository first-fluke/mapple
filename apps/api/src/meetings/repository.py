import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.meetings.models import Meeting, MeetingParticipant


class MeetingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_user(self, user_id: int) -> list[Meeting]:
        stmt = select(Meeting).where(Meeting.user_id == user_id).order_by(Meeting.scheduled_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, meeting_id: int, user_id: int) -> Meeting | None:
        stmt = select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: int,
        title: str,
        scheduled_at: datetime.datetime,
        location: str | None,
        notes: str | None,
    ) -> Meeting:
        meeting = Meeting(
            user_id=user_id,
            title=title,
            scheduled_at=scheduled_at,
            location=location,
            notes=notes,
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
        scheduled_at: datetime.datetime | None = None,
        location: str | None = None,
        notes: str | None = None,
    ) -> Meeting:
        if title is not None:
            meeting.title = title
        if scheduled_at is not None:
            meeting.scheduled_at = scheduled_at
        if location is not None:
            meeting.location = location
        if notes is not None:
            meeting.notes = notes
        await self.session.flush()
        await self.session.refresh(meeting)
        return meeting

    async def delete(self, meeting: Meeting) -> None:
        await self.session.delete(meeting)
        await self.session.flush()

    async def get_participants(self, meeting_id: int) -> list[MeetingParticipant]:
        stmt = select(MeetingParticipant).where(
            MeetingParticipant.meeting_id == meeting_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_participants(self, meeting_id: int, contact_ids: list[int]) -> list[MeetingParticipant]:
        await self.session.execute(
            delete(MeetingParticipant).where(
                MeetingParticipant.meeting_id == meeting_id,
            )
        )
        participants = []
        for contact_id in contact_ids:
            p = MeetingParticipant(meeting_id=meeting_id, contact_id=contact_id)
            self.session.add(p)
            participants.append(p)
        await self.session.flush()
        for p in participants:
            await self.session.refresh(p)
        return participants

    async def get_participant_contact_ids(self, meeting_id: int) -> list[int]:
        stmt = select(MeetingParticipant.contact_id).where(
            MeetingParticipant.meeting_id == meeting_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
