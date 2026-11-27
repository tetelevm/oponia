import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character, get_current_location
from main import app
from models import Character, Image, Item, Location


class ShopItemTests(unittest.TestCase):
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
        self.session.scalars.return_value.all.return_value = [Item(
            name="Sword", slug="sword",
            price_coins=120, price_platinum=0, quantity=5,
            icon=Image(image="sword.png", label="Sword", ascii_art=" /\n/"),
        )]

    def test_category_returns_base_and_item_summaries(self) -> None:
        for image_format, value in (("url", "sword.png"), ("ascii", " /\n/")):
            with self.subTest(image_format=image_format):
                response = self.client.get(
                    "/shop/weapon", params={"image_format": image_format},
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {
                    "character": {
                        "level": 3, "nickname": "Hero", "coins": 120, "platinum": 0,
                    },
                    "location": {"slug": "village", "name": "Village", "image": None},
                    "items": [{
                        "name": "Sword", "slug": "sword",
                        "icon": {"format": image_format, "value": value},
                        "price_coins": 120, "price_platinum": 0,
                        "quantity": 5,
                    }],
                })

    def test_invalid_category(self) -> None:
        response = self.client.get("/shop/unknown")

        self.assertEqual(response.status_code, 422)
        self.session.scalars.assert_not_called()
