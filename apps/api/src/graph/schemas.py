from enum import StrEnum

from pydantic import BaseModel


class EdgeType(StrEnum):
    COMPANY = "company"
    SCHOOL = "school"
    TAG = "tag"
    REGION = "region"
    MEETING = "meeting"


class EdgeOut(BaseModel):
    source_contact_id: int
    target_contact_id: int
    type: EdgeType
    label: str


class ClusterOut(BaseModel):
    id: int
    type: EdgeType
    label: str
    contact_ids: list[int]
