from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character, get_current_location
from models import Character, Location
from schemas.components import (
    CharacterSummarySchema,
    EnemySummarySchema,
    ImageFormat,
    LocationSchema,
    StatsSchema,
)
from schemas.responses import EnemiesResponseSchema, EnemyResponseSchema
from services import enemies

from .images import get_image_representation

router = APIRouter(tags=["enemies"])


@router.get(
    "/enemies",
    response_model=EnemiesResponseSchema,
    responses={404: {"description": "Character not found"}},
)
def read_enemies(
    session: Annotated[Session, Depends(get_session)],
    character: Annotated[Character, Depends(get_current_character)],
    location: Annotated[Location, Depends(get_current_location)],
    image_format: ImageFormat = ImageFormat.URL,
) -> EnemiesResponseSchema:
    available_enemies = enemies.get_available_enemies(session, location.id)
    return EnemiesResponseSchema(
        character=CharacterSummarySchema.model_validate(character),
        location=LocationSchema(
            slug=location.slug,
            name=location.name,
            image=get_image_representation(location.image, image_format),
        ),
        enemies=[
            EnemySummarySchema(
                name=enemy.name,
                slug=enemy.slug,
                icon=get_image_representation(enemy.icon, image_format),
            )
            for enemy in available_enemies
        ],
    )


@router.get(
    "/enemies/{slug}",
    response_model=EnemyResponseSchema,
    responses={404: {"description": "Character or enemy not found"}},
)
def read_enemy(
    slug: str,
    session: Annotated[Session, Depends(get_session)],
    character: Annotated[Character, Depends(get_current_character)],
    location: Annotated[Location, Depends(get_current_location)],
    image_format: ImageFormat = ImageFormat.URL,
) -> EnemyResponseSchema:
    enemy = enemies.get_enemy(session, location.id, slug)
    if enemy is None:
        raise HTTPException(status_code=404, detail="Enemy not found")

    return EnemyResponseSchema(
        character=CharacterSummarySchema.model_validate(character),
        location=LocationSchema(
            slug=location.slug,
            name=location.name,
            image=get_image_representation(location.image, image_format),
        ),
        name=enemy.name,
        slug=enemy.slug,
        icon=get_image_representation(enemy.icon, image_format),
        image=get_image_representation(enemy.image, image_format),
        stats=StatsSchema.model_validate(enemy),
    )
