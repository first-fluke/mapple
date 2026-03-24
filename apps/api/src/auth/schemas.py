from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    image: str | None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
