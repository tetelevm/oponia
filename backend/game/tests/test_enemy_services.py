from uuid import uuid4

from database_case import DatabaseTestCase
from models import Enemy, EnemyLocation, Image, Location
from services.enemies import get_available_enemies, get_enemy


class AvailableEnemyTests(DatabaseTestCase):
    def test_location_filter_order_conditions_and_icon_loading(self) -> None:
        forest = Location(slug="forest", name="Forest")
        cave = Location(slug="cave", name="Cave")
        icon = Image(image="/icons/enemy.png", label="Icon", ascii_art="ASCII icon")
        for slug, order, location in (
            ("wolf", 2, forest),
            ("bear", -1, forest),
            ("spider", 2, forest),
            ("dragon", -2, cave),
        ):
            self.session.add(
                EnemyLocation(
                    enemy=Enemy(slug=slug, name=slug.title(), icon=icon),
                    location=location,
                    order=order,
                    conditions=["requires-key"],
                )
            )
        self.session.commit()
        location_id = forest.id
        self.session.expunge_all()

        enemies = get_available_enemies(self.session, location_id)
        self.assertEqual(
            [enemy.slug for enemy in enemies],
            ["bear", "spider", "wolf"],
        )
        self.assertEqual(get_available_enemies(self.session, uuid4()), [])
        wolf = get_enemy(self.session, location_id, "wolf")
        self.assertIsNotNone(wolf)
        self.assertEqual(wolf.slug, "wolf")
        self.assertIsNone(get_enemy(self.session, location_id, "dragon"))
        self.assertIsNone(get_enemy(self.session, location_id, "missing"))
        self.session.close()
        self.assertEqual(wolf.icon.image, "/icons/enemy.png")
        self.assertIsNone(wolf.image)
        self.assertTrue(
            all(enemy.icon.image == "/icons/enemy.png" for enemy in enemies)
        )
