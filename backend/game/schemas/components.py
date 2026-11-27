from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CharacterSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: int
    nickname: str
    coins: int
    platinum: int


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

