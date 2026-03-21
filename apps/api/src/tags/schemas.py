import datetime

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagOut(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
