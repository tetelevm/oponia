from database_case import DatabaseTestCase
from models import Image, Item, ItemLocation, ItemType, Location
from services.shop import get_shop_item, get_shop_items


class ShopItemServiceTests(DatabaseTestCase):
    def test_location_type_filter_order_conditions_and_icons(self) -> None:
        village = Location(slug="village", name="Village")
        cave = Location(slug="cave", name="Cave")
        icon = Image(image="weapon.png", label="Weapon", ascii_art="ASCII")
        for slug, item_type, order, location in (
            ("sword", ItemType.WEAPON, 2, village),
            ("bow", ItemType.WEAPON, -1, village),
            ("axe", ItemType.WEAPON, 2, village),
            ("potion", ItemType.POTION, -2, village),
            ("spear", ItemType.WEAPON, -3, cave),
        ):
            self.session.add(
                ItemLocation(
                    item=Item(slug=slug, name=slug.title(), type=item_type, icon=icon),
                    location=location,
                    order=order,
                    conditions=["requires-key"],
                )
            )
        self.session.commit()
        location_id = village.id
        self.session.expunge_all()

        items = get_shop_items(self.session, location_id, ItemType.WEAPON)
        self.assertEqual([item.slug for item in items], ["bow", "axe", "sword"])
        self.assertEqual(get_shop_items(self.session, location_id, ItemType.RING), [])
        sword = get_shop_item(self.session, location_id, ItemType.WEAPON, "sword")
        self.assertIsNotNone(sword)
        self.assertEqual(sword.slug, "sword")
        for item_type, slug in (
            (ItemType.WEAPON, "spear"),
            (ItemType.POTION, "sword"),
            (ItemType.WEAPON, "missing"),
        ):
            self.assertIsNone(get_shop_item(self.session, location_id, item_type, slug))
        self.session.close()
        self.assertTrue(all(item.icon.image == "weapon.png" for item in items))
        self.assertEqual(sword.icon.image, "weapon.png")
        self.assertIsNone(sword.image)
