from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .location import Location
from ..mixins import DisplayMixin, StatsMixin


class Enemy(DisplayMixin, StatsMixin, Base):
    __tablename__ = "game_enemies"
    __table_args__ = (
        CheckConstraint(
            "slug ~ '^[a-z0-9]+([-_][a-z0-9]+)*$'", name="ck_enemies_slug_format"
        ),
        CheckConstraint("btrim(name) <> ''", name="ck_enemies_name_not_blank"),
    )

    location_links: Mapped[list["EnemyLocation"]] = relationship(
        back_populates="enemy", cascade="all, delete-orphan", passive_deletes=True
    )


class EnemyLocation(Base):
    __tablename__ = "game_enemy_locations"
    __table_args__ = (
        UniqueConstraint("enemy_id", "location_id", name="uq_enemy_locations_pair"),
    )

    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    enemy_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_enemies.id", ondelete="CASCADE")
    )
    location_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_locations.id", ondelete="CASCADE"), index=True
    )
    conditions: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(String(64))), default=list, server_default="{}"
    )

    enemy: Mapped[Enemy] = relationship(back_populates="location_links")
    location: Mapped[Location] = relationship(back_populates="enemy_links")
