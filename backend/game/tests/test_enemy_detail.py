import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_character, get_current_location
from main import app
from models import Character, Enemy, Image, Location


class EnemyDetailTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=Session)
        self.location = Location(id=uuid4(), slug="forest", name="Forest")
        character = Character(
            nickname="Hero", level=3, coins=120, platinum=0,
        )
        app.dependency_overrides[get_session] = lambda: self.session
        app.dependency_overrides[get_current_character] = lambda: character
        app.dependency_overrides[get_current_location] = lambda: self.location
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)
        self.enemy = Enemy(
            name="Wolf", slug="wolf", health=40, damage=10, armor=0,
            special_effects={"bleeding": 2},
            icon=Image(image="/icons/wolf.png", label="Icon", ascii_art="oo"),
            image=Image(image="/images/wolf.png", label="Wolf", ascii_art=" /\\\n oo"),
        )
        self.session.scalar.return_value = self.enemy

    def test_detail_includes_base_summary_image_and_stats(self) -> None:
        response = self.client.get("/enemies/wolf")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "character": {
                "level": 3, "nickname": "Hero", "coins": 120, "platinum": 0,
            },
            "location": {"slug": "forest", "name": "Forest", "image": None},
            "name": "Wolf", "slug": "wolf",
            "icon": {"format": "url", "value": "/icons/wolf.png"},
            "image": {"format": "url", "value": "/images/wolf.png"},
            "stats": {
                "health": 40, "damage": 10, "armor": 0,
                "special_effects": {"bleeding": 2},
            },
        })

    def test_missing_enemy(self) -> None:
        self.session.scalar.return_value = None

        response = self.client.get("/enemies/missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Enemy not found"})
