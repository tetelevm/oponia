from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from models import Character, Location
from services import characters, locations


def get_current_character(
    session: Annotated[Session, Depends(get_session)],
) -> Character:
    character = characters.get_current_character(session)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


def get_current_location(
    session: Annotated[Session, Depends(get_session)],
    character: Annotated[Character, Depends(get_current_character)],
) -> Location:
    location = locations.get_current_location(session, character.id)
    if location is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return location
