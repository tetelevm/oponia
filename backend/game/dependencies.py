from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from models import Character
from services import characters


def get_current_character(
    session: Annotated[Session, Depends(get_session)],
) -> Character:
    character = characters.get_current_character(session)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character
