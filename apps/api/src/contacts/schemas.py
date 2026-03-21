import datetime

from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field
class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
class TagOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}
    name: str = Field(max_length=255)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    tag_ids: list[int] = Field(default_factory=list)
class ContactPatch(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    tag_ids: list[int] | None = None


class ContactOut(BaseModel):
    id: int
    user_id: int
    name: str
    email: str | None
    phone: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
    country: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    notes: str | None
    tags: list[TagOut]
    created_at: datetime
    updated_at: datetime
class ContactListFilter(BaseModel):
    tag: str | None = None
    country: str | None = None
    city: str | None = None
    q: str | None = None
    per_page: int = Field(default=20, ge=1, le=100)
    cursor: str | None = None
