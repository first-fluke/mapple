import datetime

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    latitude: float | None = None
    longitude: float | None = None
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=255)
    tag_ids: list[int] = Field(default_factory=list)
    experiences: list["ExperienceInput"] = Field(default_factory=list)


class ExperienceInput(BaseModel):
    organization_id: int
    role: str | None = Field(default=None, max_length=255)
    major: str | None = Field(default=None, max_length=255)


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    latitude: float | None = None
    longitude: float | None = None
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=255)


class ContactPatch(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    tag_ids: list[int] | None = None


class ContactOut(BaseModel):
    id: int
    user_id: int
    name: str
    email: str | None
    phone: str | None
    latitude: float | None
    longitude: float | None
    country: str | None
    city: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    tags: list["TagOut"] = []
    experiences: list["ExperienceOut"] = []

    model_config = {"from_attributes": True}


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ExperienceOut(BaseModel):
    id: int
    organization_id: int
    role: str | None
    major: str | None

    model_config = {"from_attributes": True}


class ContactListFilter(BaseModel):
    tag: str | None = None
    country: str | None = None
    city: str | None = None
    q: str | None = None
    per_page: int = Field(default=20, ge=1, le=100)
    cursor: str | None = None
