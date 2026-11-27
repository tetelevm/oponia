from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..mixins import DisplayMixin

if TYPE_CHECKING:
    from .character import Character
    from .enemy import EnemyLocation
    from .item import ItemLocation


class Location(DisplayMixin, Base):
    __tablename__ = "game_locations"
    __table_args__ = (
        CheckConstraint(
            "slug ~ '^[a-z0-9]+([-_][a-z0-9]+)*$'", name="ck_locations_slug_format"
        ),
        CheckConstraint("btrim(name) <> ''", name="ck_locations_name_not_blank"),
        CheckConstraint(
            "sell_multiplier BETWEEN 0 AND 1", name="ck_locations_sell_multiplier"
        ),
    )

    sell_multiplier: Mapped[float | None] = mapped_column(Float)

    characters: Mapped[list["Character"]] = relationship(
        back_populates="location", passive_deletes="all"
    )

    enemy_links: Mapped[list["EnemyLocation"]] = relationship(
        back_populates="location", cascade="all, delete-orphan", passive_deletes=True
    )
    item_links: Mapped[list["ItemLocation"]] = relationship(
        back_populates="location", cascade="all, delete-orphan", passive_deletes=True
    )

    outgoing_connections: Mapped[list["LocationConnection"]] = relationship(
        back_populates="source",
        foreign_keys="LocationConnection.source_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class LocationConnection(Base):
    __tablename__ = "game_location_connections"
    __table_args__ = (
        UniqueConstraint("source_id", "target_id", name="uq_location_connections_pair"),
    )

    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_locations.id", ondelete="CASCADE")
    )
    target_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_locations.id", ondelete="CASCADE"), index=True
    )
    conditions: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(String(64))), default=list, server_default="{}"
    )

    source: Mapped[Location] = relationship(
        back_populates="outgoing_connections", foreign_keys=[source_id]
    )
    target: Mapped[Location] = relationship(foreign_keys=[target_id])
