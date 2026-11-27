from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character
from models import Character, Location
from schemas import (
    CurrentLocationSchema,
    ImageFormat,
    ImageRepresentationSchema,
    LocationSummarySchema,
)
from services import locations

router = APIRouter(tags=["locations"])


def _get_location_image(
    location: Location, image_format: ImageFormat,
) -> ImageRepresentationSchema | None:
    if location.image is None:
        return None

    image = (
        location.image.ascii_art
        if image_format == ImageFormat.ASCII else
        location.image.image
    )
    if image is None:
        return None

    return ImageRepresentationSchema(format=image_format, value=image)


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
        slug=location.slug,
        name=location.name,
        image=_get_location_image(location, image_format),
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
