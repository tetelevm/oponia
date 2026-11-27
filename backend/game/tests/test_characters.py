import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from main import app
from models import Character, Image, Location


class CurrentCharacterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=Session)
        app.dependency_overrides[get_session] = lambda: self.session
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)
        self.character = Character(
            id=uuid4(), nickname="Hero", level=3, coins=120, platinum=0,
            experience=250, fame=12, health=100, damage=15, armor=8,
            special_effects={"poison": {"damage": 2}},
            image=Image(image="/images/hero.png", label="Hero", ascii_art=" O\n/|\\"),
            location=Location(
                id=uuid4(), slug="village", name="Village",
                image=Image(
                    image="/images/village.png", label="Village",
                    ascii_art=" /\\\n/__\\",
                ),
            ),
        )
        self.session.scalar.return_value = self.character

    def test_character_includes_base_progression_stats_and_default_url_image(self):
        response = self.client.get("/character")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "character": {
                "level": 3, "nickname": "Hero", "coins": 120, "platinum": 0,
            },
            "location": {
                "slug": "village", "name": "Village",
                "image": {"format": "url", "value": "/images/village.png"},
            },
            "stats": {
                "health": 100, "damage": 15, "armor": 8,
                "special_effects": {"poison": {"damage": 2}},
            },
            "experience": 250,
            "fame": 12,
            "image": {"format": "url", "value": "/images/hero.png"},
        })
        self.session.scalars.assert_not_called()

    def test_ascii_format_applies_to_both_images(self):
        response = self.client.get("/character", params={"image_format": "ascii"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["image"], {
            "format": "ascii", "value": self.character.image.ascii_art,
        })
        self.assertEqual(response.json()["location"]["image"], {
            "format": "ascii", "value": self.character.location.image.ascii_art,
        })
