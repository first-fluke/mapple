import datetime

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.contact_relationships.service import ContactRelationshipService
from src.contacts.models import Contact
from src.lib.exceptions import NotFoundException
from src.meetings.models import Meeting, MeetingParticipant
from src.meetings.repository import MeetingRepository
from src.meetings.schemas import MeetingOut, ParticipantOut


class MeetingService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.repo = MeetingRepository(session)
        self.relationship_service = ContactRelationshipService(session, redis)

    async def _ensure_contacts_exist(self, contact_ids: list[int]) -> None:
        for contact_id in contact_ids:
            contact = await self.session.get(Contact, contact_id)
            if not contact:
                raise NotFoundException(message=f"Contact {contact_id} not found")

    async def _build_meeting_out(self, meeting: Meeting, participants: list[MeetingParticipant]) -> MeetingOut:
        return MeetingOut(
            id=meeting.id,
            user_id=meeting.user_id,
            title=meeting.title,
            scheduled_at=meeting.scheduled_at,
            location=meeting.location,
            notes=meeting.notes,
            participants=[ParticipantOut.model_validate(p) for p in participants],
            created_at=meeting.created_at,
            updated_at=meeting.updated_at,
        )

    async def list_by_user(self, user_id: int) -> list[MeetingOut]:
        meetings = await self.repo.find_by_user(user_id)
        result = []
        for meeting in meetings:
            participants = await self.repo.get_participants(meeting.id)
            result.append(await self._build_meeting_out(meeting, participants))
        return result

    async def get(self, *, user_id: int, meeting_id: int) -> MeetingOut:
        meeting = await self.repo.find_by_id(meeting_id, user_id)
        if not meeting:
            raise NotFoundException(message=f"Meeting {meeting_id} not found")
        participants = await self.repo.get_participants(meeting.id)
        return await self._build_meeting_out(meeting, participants)

    async def create(
        self,
        *,
        user_id: int,
        title: str,
        scheduled_at: datetime.datetime,
        location: str | None,
        notes: str | None,
        participant_ids: list[int],
    ) -> MeetingOut:
        await self._ensure_contacts_exist(participant_ids)
        meeting = await self.repo.create(
            user_id=user_id,
            title=title,
            scheduled_at=scheduled_at,
            location=location,
            notes=notes,
        )
        participants = await self.repo.set_participants(meeting.id, participant_ids)
        await self.relationship_service.recompute_strength_for_contacts(
            user_id,
            participant_ids,
        )
        return await self._build_meeting_out(meeting, participants)

    async def update(
        self,
        *,
        user_id: int,
        meeting_id: int,
        title: str | None = None,
        scheduled_at: datetime.datetime | None = None,
        location: str | None = None,
        notes: str | None = None,
        participant_ids: list[int] | None = None,
    ) -> MeetingOut:
        meeting = await self.repo.find_by_id(meeting_id, user_id)
        if not meeting:
            raise NotFoundException(message=f"Meeting {meeting_id} not found")

        old_contact_ids = await self.repo.get_participant_contact_ids(meeting.id)

        meeting = await self.repo.update(
            meeting,
            title=title,
            scheduled_at=scheduled_at,
            location=location,
            notes=notes,
        )

        if participant_ids is not None:
            await self._ensure_contacts_exist(participant_ids)
            participants = await self.repo.set_participants(meeting.id, participant_ids)
            all_affected = list(set(old_contact_ids) | set(participant_ids))
            await self.relationship_service.recompute_strength_for_contacts(
                user_id,
                all_affected,
            )
        else:
            participants = await self.repo.get_participants(meeting.id)

        return await self._build_meeting_out(meeting, participants)

    async def delete(self, *, user_id: int, meeting_id: int) -> None:
        meeting = await self.repo.find_by_id(meeting_id, user_id)
        if not meeting:
            raise NotFoundException(message=f"Meeting {meeting_id} not found")

        contact_ids = await self.repo.get_participant_contact_ids(meeting.id)
        await self.repo.delete(meeting)
        await self.relationship_service.recompute_strength_for_contacts(
            user_id,
            contact_ids,
        )
