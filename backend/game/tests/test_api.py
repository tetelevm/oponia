import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character, get_current_location
from main import app
from models import Character, Image, Location


class GameApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.location = Location(
            id=uuid4(), slug="village", name="Village", sell_multiplier=0,
            image=Image(label="Village", image="/media/village.webp", ascii_art=" /\\"),
        )
        self.character = Character(
            id=uuid4(), nickname="Hero", level=1, coins=0, platinum=0,
            experience=0, fame=0, health=10, damage=1, armor=0,
            special_effects={}, location=self.location,
            image=Image(label="Hero", image="/media/hero.webp", ascii_art=" O\n/|\\"),
        )
        self.session = Mock(spec=Session)
        self.session.scalar.return_value = self.character
        app.dependency_overrides[get_session] = lambda: self.session
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)

    def test_no_current_character(self) -> None:
        self.session.scalar.return_value = None
        response = self.client.get("/location")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Character not found")

    def test_shop_exists_for_zero_multiplier_but_not_null(self) -> None:
        for multiplier, status in ((0.5, 200), (0, 200), (None, 404)):
            with self.subTest(multiplier=multiplier):
                self.location.sell_multiplier = multiplier
                response = self.client.get("/shop")
                self.assertEqual(response.status_code, status)
                if status == 404:
                    self.assertEqual(response.json()["detail"], "Shop not found")

    def test_missing_enemy_and_item(self) -> None:
        app.dependency_overrides[get_current_character] = lambda: self.character
        app.dependency_overrides[get_current_location] = lambda: self.location
        self.session.scalar.return_value = None
        for path, detail in (
            ("/enemies/missing", "Enemy not found"),
            ("/shop/weapon/missing", "Item not found"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json()["detail"], detail)

    def test_image_formats_preserve_ascii_without_url_fallback(self) -> None:
        for image_format in ("url", "ascii"):
            with self.subTest(image_format=image_format):
                response = self.client.get(
                    "/character", params={"image_format": image_format},
                )
                self.assertEqual(response.status_code, 200)
                body = response.json()
                for field, image in (
                    (body["image"], self.character.image),
                    (body["location"]["image"], self.location.image),
                ):
                    value = image.image if image_format == "url" else image.ascii_art
                    self.assertEqual(field, {"format": image_format, "value": value})
        self.location.image.ascii_art = None
        response = self.client.get("/character", params={"image_format": "ascii"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["location"]["image"])
