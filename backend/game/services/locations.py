from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import Character, Location, LocationConnection


def get_current_location(
    session: Session,
    character_id: UUID,
) -> Location | None:
    statement = (
        select(Character)
        .where(Character.id == character_id)
        .options(
            joinedload(Character.location).joinedload(Location.image),
        )
    )

    character = session.scalar(statement)
    if character is None:
        return None

    return character.location


def get_available_locations(
    session: Session,
    location_id: UUID,
) -> list[Location]:
    statement = (
        select(Location)
        .where(LocationConnection.source_id == location_id)
        .join(LocationConnection, LocationConnection.target_id == Location.id)
        .order_by(LocationConnection.order, Location.slug)
    )
    return list(session.scalars(statement).all())
