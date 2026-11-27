from enum import StrEnum

from pydantic import BaseModel


class ImageFormat(StrEnum):
    URL = "url"
    ASCII = "ascii"


class ImageRepresentationSchema(BaseModel):
    format: ImageFormat
    value: str


class LocationSummarySchema(BaseModel):
    slug: str
    name: str


class LocationSchema(LocationSummarySchema):
    image: ImageRepresentationSchema | None


class CurrentLocationSchema(LocationSchema):
    description: str | None
    sell_multiplier: float | None
    available_locations: list[LocationSummarySchema]
