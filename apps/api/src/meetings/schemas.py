import datetime

from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    scheduled_at: datetime.datetime
    location: str | None = Field(default=None, max_length=500)
    notes: str | None = None
    participant_ids: list[int] = Field(min_length=1)


class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    scheduled_at: datetime.datetime | None = None
    location: str | None = Field(default=None, max_length=500)
    notes: str | None = None
    participant_ids: list[int] | None = Field(default=None, min_length=1)


class ParticipantOut(BaseModel):
    id: int
    contact_id: int

    model_config = {"from_attributes": True}


class MeetingOut(BaseModel):
    id: int
    user_id: int
    title: str
    scheduled_at: datetime.datetime
    location: str | None
    notes: str | None
    participants: list[ParticipantOut]
    created_at: datetime.datetime
    updated_at: datetime.datetime
