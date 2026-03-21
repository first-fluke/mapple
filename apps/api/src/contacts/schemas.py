import datetime

from pydantic import BaseModel


class ContactOut(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
