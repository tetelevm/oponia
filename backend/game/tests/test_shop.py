import unittest

from fastapi.testclient import TestClient

from dependencies import get_current_character, get_current_location
from main import app
from models import Character, Image, Location


class ShopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.character = Character(nickname="Hero", level=3, coins=120, platinum=0)
        self.location = Location(
            slug="village", name="Village", sell_multiplier=0.5,
            image=Image(image="village.png", label="Village", ascii_art=" /\\\n/__\\"),
        )
        app.dependency_overrides[get_current_character] = lambda: self.character
        app.dependency_overrides[get_current_location] = lambda: self.location
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)

    def test_shop_returns_all_item_types_including_zero_multiplier(self) -> None:
        for multiplier in (0.5, 0.0):
            with self.subTest(multiplier=multiplier):
                self.location.sell_multiplier = multiplier
                response = self.client.get("/shop")

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {
                    "character": {
                        "level": 3, "nickname": "Hero", "coins": 120, "platinum": 0,
                    },
                    "location": {
                        "slug": "village", "name": "Village",
                        "image": {"format": "url", "value": "village.png"},
                    },
                    "item_types": [
                        "weapon", "secondary_weapon", "helmet", "armor", "gloves",
                        "pants", "boots", "amulet", "ring", "potion", "scroll",
                        "enhancement",
                    ],
                })

    def test_no_shop_when_multiplier_is_null(self) -> None:
        self.location.sell_multiplier = None

        response = self.client.get("/shop")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Shop not found"})
