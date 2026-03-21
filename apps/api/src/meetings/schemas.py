import datetime

from pydantic import BaseModel, Field
from pydantic import BaseModel, Field, model_validator


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
    description: str | None = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    location: str | None = Field(default=None, max_length=255)
    attendee_contact_ids: list[int] = Field(default_factory=list)
    @model_validator(mode="after")
    def validate_times(self) -> "MeetingCreate":
        if self.start_time >= self.end_time:
            msg = "end_time must be after start_time"
            raise ValueError(msg)
        return self
    title: str = Field(min_length=1, max_length=255)
    def validate_times(self) -> "MeetingUpdate":


class MeetingOut(BaseModel):
    id: int
    user_id: int
    title: str
    scheduled_at: datetime.datetime
    location: str | None
    notes: str | None
    participants: list[ParticipantOut]
    description: str | None
    start_time: datetime.datetime
    end_time: datetime.datetime
    attendee_contact_ids: list[int]
    created_at: datetime.datetime
    updated_at: datetime.datetime
