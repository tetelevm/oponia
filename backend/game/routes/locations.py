from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character
from models import Character
from schemas.components import (
    CharacterSummarySchema,
    ImageFormat,
    LocationSchema,
    LocationSummarySchema,
)
from schemas.responses import CurrentLocationSchema
from services import locations

from .images import get_image_representation

router = APIRouter(tags=["locations"])


@router.get(
    "/location",
    response_model=CurrentLocationSchema,
    responses={404: {"description": "Character not found"}},
)
def get_current_location(
    session: Annotated[Session, Depends(get_session)],
    character: Annotated[Character, Depends(get_current_character)],
    image_format: ImageFormat = ImageFormat.URL,
) -> CurrentLocationSchema:
    location = locations.get_current_location(session, character.id)
    if location is None:
        raise HTTPException(status_code=404, detail="Character not found")

    available = locations.get_available_locations(session, location.id)

    return CurrentLocationSchema(
        character=CharacterSummarySchema.model_validate(character),
        location=LocationSchema(
            slug=location.slug,
            name=location.name,
            image=get_image_representation(location.image, image_format),
        ),
        description=location.description,
        sell_multiplier=location.sell_multiplier,
        available_locations=[
            LocationSummarySchema(
                slug=destination.slug,
                name=destination.name,
            )
            for destination in available
        ],
    )
