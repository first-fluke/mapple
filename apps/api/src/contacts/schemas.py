import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

# E.164-ish pattern: optional leading +, then digits, spaces, hyphens, parens.
# Allows common formats like +1-800-555-0100 or +82 10 1234 5678.
_PHONE_PATTERN = r"^\+?[\d\s\-().]{7,30}$"


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: Annotated[EmailStr | None, Field(default=None)]
    phone: str | None = Field(default=None, pattern=_PHONE_PATTERN, max_length=30)
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
    email: Annotated[EmailStr | None, Field(default=None)]
    phone: str | None = Field(default=None, pattern=_PHONE_PATTERN, max_length=30)
    latitude: float | None = None
    longitude: float | None = None
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=512)
    tag_ids: list[int] | None = None


class ContactAvatarPresignOut(BaseModel):
    """Response for a contact-scoped avatar presign request.

    upload_url is a presigned PUT URL the client uploads the file to;
    avatar_url is the public URL to persist on the contact afterwards.
    """

    upload_url: str
    avatar_url: str


class ContactPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    tag_ids: list[int] | None = None


class ContactOut(BaseModel):
    id: int
    user_id: str
    name: str
    email: str | None
    phone: str | None
    latitude: float | None
    longitude: float | None
    country: str | None
    city: str | None
    avatar_url: str | None = None
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
