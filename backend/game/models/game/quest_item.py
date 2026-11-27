from datetime import timedelta
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Interval, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..mixins import DisplayMixin

if TYPE_CHECKING:
    from .character import CharacterQuestItem


class QuestItem(DisplayMixin, Base):
    __tablename__ = "game_quest_items"
    __table_args__ = (
        CheckConstraint(
            "slug ~ '^[a-z0-9]+([-_][a-z0-9]+)*$'", name="ck_quest_items_slug_format"
        ),
        CheckConstraint("btrim(name) <> ''", name="ck_quest_items_name_not_blank"),
        CheckConstraint(
            "lifetime > INTERVAL '0 seconds'", name="ck_quest_items_lifetime"
        ),
    )

    lifetime: Mapped[timedelta | None] = mapped_column(Interval)
    visible: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false()
    )

    character_links: Mapped[list["CharacterQuestItem"]] = relationship(
        back_populates="quest_item", cascade="all, delete-orphan", passive_deletes=True
    )
