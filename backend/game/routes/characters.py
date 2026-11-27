from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import get_current_character, get_current_location
from models import Character, Location
from schemas.components import (
    CharacterSummarySchema,
    ImageFormat,
    LocationSchema,
    StatsSchema,
)
from schemas.responses import CurrentCharacterSchema

from .images import get_image_representation

router = APIRouter(tags=["characters"])


@router.get(
    "/character",
    response_model=CurrentCharacterSchema,
    responses={404: {"description": "Character not found"}},
)
def read_current_character(
    character: Annotated[Character, Depends(get_current_character)],
    location: Annotated[Location, Depends(get_current_location)],
    image_format: ImageFormat = ImageFormat.URL,
) -> CurrentCharacterSchema:
    return CurrentCharacterSchema(
        character=CharacterSummarySchema.model_validate(character),
        location=LocationSchema(
            slug=location.slug,
            name=location.name,
            image=get_image_representation(location.image, image_format),
        ),
        stats=StatsSchema.model_validate(character),
        experience=character.experience,
        fame=character.fame,
        image=get_image_representation(character.image, image_format),
    )
