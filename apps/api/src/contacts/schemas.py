from datetime import datetime

from pydantic import BaseModel, Field


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ContactCreate(BaseModel):
    name: str = Field(max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    tag_ids: list[int] = Field(default_factory=list)


class ContactUpdate(BaseModel):
    name: str = Field(max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    tag_ids: list[int] = Field(default_factory=list)


class ContactPatch(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    tag_ids: list[int] | None = None


class ContactOut(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    country: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    notes: str | None
    tags: list[TagOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContactListFilter(BaseModel):
    tag: str | None = None
    country: str | None = None
    city: str | None = None
    q: str | None = None
    per_page: int = Field(default=20, ge=1, le=100)
    cursor: str | None = None
