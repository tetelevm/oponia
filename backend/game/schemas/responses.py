from pydantic import BaseModel

from .components import (
    CharacterSummarySchema,
    LocationSchema,
    LocationSummarySchema,
)


class BaseResponseSchema(BaseModel):
    character: CharacterSummarySchema
    location: LocationSchema


class CurrentLocationSchema(BaseResponseSchema):
    description: str | None
    sell_multiplier: float | None
    available_locations: list[LocationSummarySchema]
