from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import Character


def get_current_character(session: Session) -> Character | None:
    # Temporary character selection until authentication is implemented.
    return session.scalar(
        select(Character).options(joinedload(Character.image)).limit(1)
    )
