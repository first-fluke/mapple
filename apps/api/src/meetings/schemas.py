import datetime

from pydantic import BaseModel, Field, model_validator


class MeetingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
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


class MeetingUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    location: str | None = Field(default=None, max_length=255)
    attendee_contact_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_times(self) -> "MeetingUpdate":
        if self.start_time >= self.end_time:
            msg = "end_time must be after start_time"
            raise ValueError(msg)
        return self


class MeetingOut(BaseModel):
    id: int
    title: str
    description: str | None
    start_time: datetime.datetime
    end_time: datetime.datetime
    location: str | None
    attendee_contact_ids: list[int]
    created_at: datetime.datetime
    updated_at: datetime.datetime
