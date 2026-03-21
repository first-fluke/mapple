from pydantic import BaseModel


class GlobePinOut(BaseModel):
    id: str
    name: str
    avatar_url: str
    lat: float
    lng: float

    model_config = {"from_attributes": True}

class BboxQuery(BaseModel):
    sw_lat: float
    sw_lng: float
    ne_lat: float
    ne_lng: float
    avatar_url: str | None

class GlobeArcOut(BaseModel):
    id: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    type: str
    frequency: int

    model_config = {"from_attributes": True}

class GlobeClusterOut(BaseModel):
    lat: float
    lng: float
    count: int
    contact_ids: list[str]


class GlobeDataOut(BaseModel):
    pins: list[GlobePinOut]
    arcs: list[GlobeArcOut]
    clusters: list[GlobeClusterOut]

    model_config = {"from_attributes": True}
