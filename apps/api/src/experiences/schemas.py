import datetime

from pydantic import BaseModel, Field


class ExperienceCreate(BaseModel):
    organization_id: int
    role: str | None = Field(default=None, max_length=255)
    major: str | None = Field(default=None, max_length=255)


class ExperienceUpdate(BaseModel):
    organization_id: int | None = None
    role: str | None = Field(default=None, max_length=255)
    major: str | None = Field(default=None, max_length=255)


class ExperienceOut(BaseModel):
    id: int
    contact_id: int
    organization_id: int
    role: str | None
    major: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
