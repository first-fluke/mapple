from pydantic import BaseModel


class BboxQuery(BaseModel):
    sw_lat: float
    sw_lng: float
    ne_lat: float
    ne_lng: float


class GlobePinOut(BaseModel):
    id: str
    name: str
    avatar_url: str | None
    lat: float
    lng: float


class GlobeArcOut(BaseModel):
    id: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    type: str
    frequency: int


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
