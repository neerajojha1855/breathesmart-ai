import uuid

from pydantic import BaseModel


class LocationCreate(BaseModel):
    city: str
    region: str | None = None
    country: str
    latitude: float
    longitude: float
    is_primary: bool = False


class SavedLocationResponse(BaseModel):
    id: uuid.UUID
    city: str
    region: str | None
    country: str
    latitude: float
    longitude: float
    is_primary: bool

    class Config:
        from_attributes = True
