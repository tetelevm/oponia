from datetime import timedelta

from pydantic import BaseModel

from models import ItemType

from .components import (
    CharacterSummarySchema,
    EnemySummarySchema,
    ImageRepresentationSchema,
    ItemSummarySchema,
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


class EnemiesResponseSchema(BaseResponseSchema):
    enemies: list[EnemySummarySchema]


class EnemyResponseSchema(EnemySummarySchema, BaseResponseSchema):
    image: ImageRepresentationSchema | None
    stats: StatsSchema


class ShopResponseSchema(BaseResponseSchema):
    item_types: list[ItemType]


class ShopItemsResponseSchema(BaseResponseSchema):
    items: list[ItemSummarySchema]


class ItemResponseSchema(ItemSummarySchema, BaseResponseSchema):
    image: ImageRepresentationSchema | None
    stats: StatsSchema
    lifetime: timedelta | None
    durability: int | None
