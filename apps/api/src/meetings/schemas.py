import datetime
import uuid

from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    starts_at: datetime.datetime
    ends_at: datetime.datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    attendee_contact_ids: list[int] = Field(default_factory=list)


class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    starts_at: datetime.datetime | None = None
    ends_at: datetime.datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    attendee_contact_ids: list[int] | None = None


class MeetingOut(BaseModel):
    id: int
    user_id: uuid.UUID
    title: str
    description: str | None
    starts_at: datetime.datetime
    ends_at: datetime.datetime | None
    location: str | None
    attendee_contact_ids: list[int]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = {"from_attributes": True}
