from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=50)


class OrganizationOut(BaseModel):
    id: int
    name: str
    type: str

    model_config = {"from_attributes": True}
