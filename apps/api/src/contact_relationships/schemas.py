import datetime

from pydantic import BaseModel, Field


class ContactRelationshipCreate(BaseModel):
    contact_id_1: int = Field(gt=0)
    contact_id_2: int = Field(gt=0)
    strength: float = Field(gt=0)


class ContactRelationshipOut(BaseModel):
    id: int
    user_id: str
    contact_id_1: int
    contact_id_2: int
    strength: float
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
