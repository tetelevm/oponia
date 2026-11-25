from datetime import timedelta
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    Interval,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .location import Location
from ..mixins import DisplayMixin, StatsMixin

if TYPE_CHECKING:
    from .character import CharacterItem


class ItemType(StrEnum):
    WEAPON = "weapon"
    SECONDARY_WEAPON = "secondary_weapon"
    HELMET = "helmet"
    ARMOR = "armor"
    GLOVES = "gloves"
    PANTS = "pants"
    BOOTS = "boots"
    AMULET = "amulet"
    RING = "ring"
    POTION = "potion"
    SCROLL = "scroll"
    ENHANCEMENT = "enhancement"


class Item(DisplayMixin, StatsMixin, Base):
    __tablename__ = "game_items"
    __table_args__ = (
        CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="ck_items_slug_format"
        ),
        CheckConstraint("btrim(name) <> ''", name="ck_items_name_not_blank"),
        CheckConstraint("price_coins >= 0", name="ck_items_price_coins"),
        CheckConstraint("price_platinum >= 0", name="ck_items_price_platinum"),
        CheckConstraint("quantity >= 1", name="ck_items_quantity"),
        CheckConstraint("durability >= 0", name="ck_items_durability"),
        CheckConstraint(
            "lifetime > INTERVAL '0 seconds'", name="ck_items_lifetime"
        ),
    )

    type: Mapped[ItemType] = mapped_column(
        Enum(
            ItemType,
            name="game_item_type",
            values_callable=lambda enum: [member.value for member in enum],
            validate_strings=True,
        )
    )
    price_coins: Mapped[int | None] = mapped_column(BigInteger)
    price_platinum: Mapped[int | None] = mapped_column(BigInteger)
    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    lifetime: Mapped[timedelta | None] = mapped_column(Interval)
    durability: Mapped[int | None] = mapped_column(Integer)
    character_links: Mapped[list["CharacterItem"]] = relationship(
        back_populates="item", cascade="all, delete-orphan", passive_deletes=True
    )
    location_links: Mapped[list["ItemLocation"]] = relationship(
        back_populates="item", cascade="all, delete-orphan", passive_deletes=True
    )


class ItemLocation(Base):
    __tablename__ = "game_item_locations"
    __table_args__ = (
        UniqueConstraint("item_id", "location_id", name="uq_item_locations_pair"),
    )

    item_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_items.id", ondelete="CASCADE")
    )
    location_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_locations.id", ondelete="CASCADE"), index=True
    )
    conditions: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(String(64))), default=list, server_default="{}"
    )

    item: Mapped[Item] = relationship(back_populates="location_links")
    location: Mapped[Location] = relationship(back_populates="item_links")
