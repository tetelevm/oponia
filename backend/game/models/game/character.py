from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, Image
from .item import Item
from .location import Location
from ..mixins import StatsMixin
from .quest_item import QuestItem


class Character(StatsMixin, Base):
    __tablename__ = "game_characters"
    __table_args__ = (
        CheckConstraint(
            "btrim(nickname) <> ''", name="ck_characters_nickname_not_blank"
        ),
        CheckConstraint("level >= 1", name="ck_characters_level"),
        CheckConstraint("experience >= 0", name="ck_characters_experience"),
        CheckConstraint("fame >= 0", name="ck_characters_fame"),
        CheckConstraint("coins >= 0", name="ck_characters_coins"),
        CheckConstraint("platinum >= 0", name="ck_characters_platinum"),
        CheckConstraint("coupons >= 0", name="ck_characters_coupons"),
    )

    nickname: Mapped[str] = mapped_column(String(64))
    level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    experience: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    fame: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    coins: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    platinum: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    coupons: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    image_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("images.id", ondelete="SET NULL"), index=True
    )
    location_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_locations.id", ondelete="RESTRICT"), index=True
    )

    image: Mapped[Image | None] = relationship()
    location: Mapped[Location] = relationship(back_populates="characters")
    item_links: Mapped[list["CharacterItem"]] = relationship(
        back_populates="character", cascade="all, delete-orphan", passive_deletes=True
    )
    quest_item_links: Mapped[list["CharacterQuestItem"]] = relationship(
        back_populates="character", cascade="all, delete-orphan", passive_deletes=True
    )


class CharacterItem(Base):
    __tablename__ = "game_character_items"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_character_items_quantity"),
        CheckConstraint("durability >= 0", name="ck_character_items_durability"),
    )

    item_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_items.id", ondelete="CASCADE"), index=True
    )
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_characters.id", ondelete="CASCADE"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    durability: Mapped[int | None] = mapped_column(Integer)
    equipped: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false()
    )

    item: Mapped[Item] = relationship(back_populates="character_links")
    character: Mapped[Character] = relationship(back_populates="item_links")


class CharacterQuestItem(Base):
    __tablename__ = "game_character_quest_items"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_character_quest_items_quantity"),
    )

    quest_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_quest_items.id", ondelete="CASCADE"), index=True
    )
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_characters.id", ondelete="CASCADE"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    quest_item: Mapped[QuestItem] = relationship(back_populates="character_links")
    character: Mapped[Character] = relationship(back_populates="quest_item_links")
