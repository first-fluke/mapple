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


class GlobePinOut(BaseModel):
    id: str
    name: str
    avatar_url: str | None
    lat: float
    lng: float

    model_config = {"from_attributes": True}


class GlobeArcOut(BaseModel):
    id: int
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    type: str
    frequency: int
    strength: float
    contact_ids: list[str]
    source_contact_id: int
    target_contact_id: int
    source_name: str
    target_name: str


class GlobeDataOut(BaseModel):
    pins: list[GlobePinOut]
    arcs: list[GlobeArcOut]
