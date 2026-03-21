import datetime

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)


class ContactOut(BaseModel):
    id: int
    user_id: int
    name: str
    email: str | None
    phone: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = {"from_attributes": True}
