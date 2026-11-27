import unittest
from datetime import timedelta
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character, get_current_location
from main import app
from models import Character, Image, Item, Location


class ShopItemDetailTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=Session)
        self.character = Character(nickname="Hero", level=3, coins=120, platinum=0)
        self.location = Location(
            id=uuid4(), slug="village", name="Village", sell_multiplier=0,
        )
        app.dependency_overrides[get_session] = lambda: self.session
        app.dependency_overrides[get_current_character] = lambda: self.character
        app.dependency_overrides[get_current_location] = lambda: self.location
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)
        self.item = Item(
            name="Sword", slug="sword", price_coins=100, price_platinum=None,
            quantity=5, health=0, damage=10, armor=2, special_effects={"fire": 3},
            lifetime=timedelta(hours=1), durability=20,
            icon=Image(image="sword.png", label="Sword", ascii_art=" /\n/"),
            image=Image(image="sword-full.png", label="Sword", ascii_art="FULL\n /"),
        )
        self.session.scalar.return_value = self.item

    def test_detail_includes_summary_stats_lifetime_and_durability(self) -> None:
        response = self.client.get("/shop/weapon/sword")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "character": {
                "level": 3, "nickname": "Hero", "coins": 120, "platinum": 0,
            },
            "location": {"slug": "village", "name": "Village", "image": None},
            "name": "Sword", "slug": "sword",
            "icon": {"format": "url", "value": "sword.png"},
            "image": {"format": "url", "value": "sword-full.png"},
            "price_coins": 100, "price_platinum": None, "quantity": 5,
            "stats": {
                "health": 0, "damage": 10, "armor": 2, "special_effects": {"fire": 3},
            },
            "lifetime": "PT1H", "durability": 20,
        })

    def test_no_shop_does_not_query_item(self) -> None:
        self.location.sell_multiplier = None

        response = self.client.get("/shop/weapon/sword")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Shop not found"})
        self.session.scalar.assert_not_called()

    def test_missing_item(self) -> None:
        self.session.scalar.return_value = None

        response = self.client.get("/shop/weapon/missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Item not found"})
