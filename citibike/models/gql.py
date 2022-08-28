from pydantic import BaseModel, Field


class CitiBikeStationLocation(BaseModel):
    lat: float
    lng: float


class CitiBikeStation(BaseModel):
    station_id: str = Field(..., alias="stationId")
    station_name: str = Field(..., alias="stationName")
    site_id: str = Field(..., alias="siteId")
    bikes_available: int = Field(..., alias="bikesAvailable")
    ebikes_available: int = Field(..., alias="ebikesAvailable")
    bike_docks_available: int = Field(..., alias="bikeDocksAvailable")
    location: CitiBikeStationLocation


class CitiBikeSupply(BaseModel):
    stations: list[CitiBikeStation]


class CitiBikeData(BaseModel):
    supply: CitiBikeSupply


class CitiBikeResponse(BaseModel):
    data: CitiBikeData
