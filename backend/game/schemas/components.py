from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


class CharacterSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: int
    nickname: str
    coins: int
    platinum: int


class StatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    health: int
    damage: int
    armor: int
    special_effects: dict[str, Any]


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


class EnemySummarySchema(BaseModel):
    name: str
    slug: str
    icon: ImageRepresentationSchema | None
