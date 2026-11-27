from pydantic import BaseModel

from .components import (
    CharacterSummarySchema,
    ImageRepresentationSchema,
    LocationSchema,
    LocationSummarySchema,
    StatsSchema,
)


class BaseResponseSchema(BaseModel):
    character: CharacterSummarySchema
    location: LocationSchema


class CurrentLocationSchema(BaseResponseSchema):
    description: str | None
    sell_multiplier: float | None
    available_locations: list[LocationSummarySchema]


class CurrentCharacterSchema(BaseResponseSchema):
    stats: StatsSchema
    experience: int
    fame: int
    image: ImageRepresentationSchema | None
