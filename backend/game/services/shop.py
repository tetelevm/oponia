from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import Item, ItemLocation, ItemType, Location


def get_shop_item_types(location: Location) -> list[ItemType] | None:
    if location.sell_multiplier is None:
        return None
    return list(ItemType)


def get_shop_items(
    session: Session, location_id: UUID, item_type: ItemType,
) -> list[Item]:
    statement = (
        select(Item)
        .where(ItemLocation.location_id == location_id, Item.type == item_type)
        .join(ItemLocation, ItemLocation.item_id == Item.id)
        .options(joinedload(Item.icon))
        .order_by(ItemLocation.order, Item.slug)
    )
    return list(session.scalars(statement).all())


def get_shop_item(
    session: Session, location_id: UUID, item_type: ItemType, slug: str,
) -> Item | None:
    statement = (
        select(Item)
        .where(
            ItemLocation.location_id == location_id,
            Item.type == item_type,
            Item.slug == slug,
        )
        .join(ItemLocation, ItemLocation.item_id == Item.id)
        .options(joinedload(Item.icon), joinedload(Item.image))
    )
    return session.scalar(statement)
