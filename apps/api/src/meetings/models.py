import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.lib.database import Base


class Meeting(Base):
    __tablename__ = "meeting"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_auth.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    scheduled_at: Mapped[datetime.datetime] = mapped_column()
    location: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    start_time: Mapped[datetime.datetime]
    end_time: Mapped[datetime.datetime]
    location: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )


class MeetingParticipant(Base):
    __tablename__ = "meeting_participant"
    __table_args__ = (UniqueConstraint("meeting_id", "contact_id", name="uq_meeting_participant"),)

    id: Mapped[int] = mapped_column(primary_key=True)
class MeetingAttendee(Base):
    __tablename__ = "meeting_attendee"
    __table_args__ = (PrimaryKeyConstraint("meeting_id", "contact_id"),)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meeting.id", ondelete="CASCADE"),
    )
    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contact.id", ondelete="CASCADE"),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
