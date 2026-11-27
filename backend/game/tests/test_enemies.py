import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from main import app
from models import Character, Enemy, Image, Location


class EnemyListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=Session)
        app.dependency_overrides[get_session] = lambda: self.session
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)
        self.session.scalar.return_value = Character(
            id=uuid4(), nickname="Hero", level=3, coins=120, platinum=0,
            location=Location(id=uuid4(), slug="forest", name="Forest"),
        )
        self.enemy = Enemy(
            slug="wolf", name="Wolf", description="Not part of the summary.",
            image=Image(image="/images/wolf.png", label="Wolf"),
            icon=Image(
                image="/icons/wolf.png", label="Wolf icon", ascii_art=" /\\\n oo",
            ),
        )
        self.session.scalars.return_value.all.return_value = [self.enemy]

    def test_enemies_include_base_data_and_only_summary_fields(self) -> None:
        response = self.client.get("/enemies")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "character": {
                "level": 3, "nickname": "Hero", "coins": 120, "platinum": 0,
            },
            "location": {"slug": "forest", "name": "Forest", "image": None},
            "enemies": [{
                "name": "Wolf", "slug": "wolf",
                "icon": {"format": "url", "value": "/icons/wolf.png"},
            }],
        })
