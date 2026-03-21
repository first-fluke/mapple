import datetime

from pydantic import BaseModel, Field


class BboxQuery(BaseModel):
    west: float = Field(ge=-180, le=180)
    south: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)

    @classmethod
    def from_string(cls, bbox: str) -> "BboxQuery":
        parts = bbox.split(",")
        if len(parts) != 4:
            msg = "bbox must have 4 comma-separated values: west,south,east,north"
            raise ValueError(msg)
        return cls(
            west=float(parts[0]),
            south=float(parts[1]),
            east=float(parts[2]),
            north=float(parts[3]),
        )


class GlobeContactOut(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    latitude: float
    longitude: float
    created_at: datetime.datetime


class GlobeRelationshipOut(BaseModel):
    source_contact_id: int
    target_contact_id: int
    organization_id: int
    organization_name: str


class GlobeClusterOut(BaseModel):
    latitude: float
    longitude: float
    count: int
    contact_ids: list[int]


class GlobeDataOut(BaseModel):
    contacts: list[GlobeContactOut]
    relationships: list[GlobeRelationshipOut]
    clusters: list[GlobeClusterOut]
from pydantic import BaseModel
class GlobePinOut(BaseModel):
    id: str
    avatar_url: str
    lat: float
    lng: float
    model_config = {"from_attributes": True}
    sw_lat: float
    sw_lng: float
    ne_lat: float
    ne_lng: float
    avatar_url: str | None
class GlobeArcOut(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    type: str
    frequency: int
    contact_ids: list[str]
    pins: list[GlobePinOut]
    arcs: list[GlobeArcOut]
