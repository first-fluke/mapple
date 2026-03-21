from pydantic import BaseModel


class GlobePinOut(BaseModel):
    id: str
    name: str
    avatar_url: str
    lat: float
    lng: float

    model_config = {"from_attributes": True}


class GlobeArcOut(BaseModel):
    id: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    type: str
    frequency: int

    model_config = {"from_attributes": True}


class GlobeDataOut(BaseModel):
    pins: list[GlobePinOut]
    arcs: list[GlobeArcOut]
