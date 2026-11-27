from uuid import UUID, uuid4

from sqlalchemy import String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)


class Image(Base):
    __tablename__ = "images"

    image: Mapped[str] = mapped_column(Text)
    label: Mapped[str] = mapped_column(String(64))
    ascii_art: Mapped[str | None] = mapped_column(Text)

    def __str__(self) -> str:
        return self.label
