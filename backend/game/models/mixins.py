from typing import Any
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from .base import Image


class DisplayMixin:
    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"

    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text)
    image_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("images.id", ondelete="SET NULL"), index=True
    )
    icon_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("images.id", ondelete="SET NULL"), index=True
    )

    @declared_attr
    def image(cls) -> Mapped[Image | None]:
        return relationship(foreign_keys=[cls.image_id])

    @declared_attr
    def icon(cls) -> Mapped[Image | None]:
        return relationship(foreign_keys=[cls.icon_id])


class StatsMixin:
    health: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    damage: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    armor: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    special_effects: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict,
        server_default="{}",
    )
