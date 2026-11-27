from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character, get_current_location
from models import Character, ItemType, Location
from schemas.components import (
    CharacterSummarySchema,
    ImageFormat,
    ItemSummarySchema,
    LocationSchema,
    StatsSchema,
)
from schemas.responses import (
    ItemResponseSchema,
    ShopItemsResponseSchema,
    ShopResponseSchema,
)
from services import shop

from .images import get_image_representation

router = APIRouter(tags=["shop"])


@router.get(
    "/shop",
    response_model=ShopResponseSchema,
    responses={404: {"description": "Character or shop not found"}},
)
def read_shop(
    character: Annotated[Character, Depends(get_current_character)],
    location: Annotated[Location, Depends(get_current_location)],
    image_format: ImageFormat = ImageFormat.URL,
) -> ShopResponseSchema:
    item_types = shop.get_shop_item_types(location)
    if item_types is None:
        raise HTTPException(status_code=404, detail="Shop not found")

    return ShopResponseSchema(
        character=CharacterSummarySchema.model_validate(character),
        location=LocationSchema(
            slug=location.slug,
            name=location.name,
            image=get_image_representation(location.image, image_format),
        ),
        item_types=item_types,
    )


@router.get(
    "/shop/{item_type}",
    response_model=ShopItemsResponseSchema,
    responses={404: {"description": "Character or shop not found"}},
)
def read_shop_items(
    item_type: ItemType,
    session: Annotated[Session, Depends(get_session)],
    character: Annotated[Character, Depends(get_current_character)],
    location: Annotated[Location, Depends(get_current_location)],
    image_format: ImageFormat = ImageFormat.URL,
) -> ShopItemsResponseSchema:
    if shop.get_shop_item_types(location) is None:
        raise HTTPException(status_code=404, detail="Shop not found")

    items = shop.get_shop_items(session, location.id, item_type)
    return ShopItemsResponseSchema(
        character=CharacterSummarySchema.model_validate(character),
        location=LocationSchema(
            slug=location.slug,
            name=location.name,
            image=get_image_representation(location.image, image_format),
        ),
        items=[
            ItemSummarySchema(
                name=item.name,
                slug=item.slug,
                icon=get_image_representation(item.icon, image_format),
                price_coins=item.price_coins,
                price_platinum=item.price_platinum,
                quantity=item.quantity,
            )
            for item in items
        ],
    )


@router.get(
    "/shop/{item_type}/{slug}",
    response_model=ItemResponseSchema,
    responses={404: {"description": "Character, shop or item not found"}},
)
def read_shop_item(
    item_type: ItemType,
    slug: str,
    session: Annotated[Session, Depends(get_session)],
    character: Annotated[Character, Depends(get_current_character)],
    location: Annotated[Location, Depends(get_current_location)],
    image_format: ImageFormat = ImageFormat.URL,
) -> ItemResponseSchema:
    if shop.get_shop_item_types(location) is None:
        raise HTTPException(status_code=404, detail="Shop not found")

    item = shop.get_shop_item(session, location.id, item_type, slug)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponseSchema(
        character=CharacterSummarySchema.model_validate(character),
        location=LocationSchema(
            slug=location.slug,
            name=location.name,
            image=get_image_representation(location.image, image_format),
        ),
        name=item.name,
        slug=item.slug,
        icon=get_image_representation(item.icon, image_format),
        price_coins=item.price_coins,
        price_platinum=item.price_platinum,
        quantity=item.quantity,
        image=get_image_representation(item.image, image_format),
        stats=StatsSchema.model_validate(item),
        lifetime=item.lifetime,
        durability=item.durability,
    )
