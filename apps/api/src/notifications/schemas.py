import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DeviceTokenRegister(BaseModel):
    token: str = Field(min_length=1, max_length=4096)
    platform: Literal["ios", "android", "web"]


class DeviceTokenOut(BaseModel):
    id: int
    user_id: str
    token: str
    platform: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
