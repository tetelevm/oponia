from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import Enemy, EnemyLocation


def get_available_enemies(session: Session, location_id: UUID) -> list[Enemy]:
    statement = (
        select(Enemy)
        .join(EnemyLocation, EnemyLocation.enemy_id == Enemy.id)
        .where(EnemyLocation.location_id == location_id)
        .options(joinedload(Enemy.icon))
        .order_by(EnemyLocation.order, Enemy.slug)
    )
    return list(session.scalars(statement).all())


def get_enemy(session: Session, location_id: UUID, slug: str) -> Enemy | None:
    statement = (
        select(Enemy)
        .join(EnemyLocation, EnemyLocation.enemy_id == Enemy.id)
        .where(EnemyLocation.location_id == location_id, Enemy.slug == slug)
        .options(joinedload(Enemy.icon), joinedload(Enemy.image))
    )
    return session.scalar(statement)
