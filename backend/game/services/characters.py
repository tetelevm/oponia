from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Character


def get_current_character(session: Session) -> Character | None:
    # Temporary character selection until authentication is implemented.
    return session.scalar(select(Character).limit(1))
