import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from main import app
from models import Character, Image, Location


class CurrentLocationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=Session)
        self.session.scalars.return_value.all.return_value = []
        app.dependency_overrides[get_session] = lambda: self.session
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)

    def test_location_includes_available_destinations(self) -> None:
        location = Location(
            id=uuid4(), slug="village", name="Village", description="A quiet place.",
            image=Image(image="/images/village.png", label="Village"),
            sell_multiplier=0.5,
        )
        destination = Location(
            id=uuid4(), slug="forest", name="Forest", description="Tall trees.",
            image=Image(image="/images/forest.png", label="Forest"),
        )
        character = Character(
            id=uuid4(), nickname="Hero", level=3, coins=120, platinum=0,
            location=location,
        )
        self.session.scalar.return_value = character
        self.session.scalars.return_value.all.return_value = [destination]

        response = self.client.get("/location")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "character": {
                "level": 3, "nickname": "Hero", "coins": 120,
                "platinum": 0,
            },
            "location": {
                "slug": "village",
                "name": "Village",
                "image": {"format": "url", "value": "/images/village.png"},
            },
            "description": "A quiet place.",
            "sell_multiplier": 0.5,
            "available_locations": [{
                "slug": "forest", "name": "Forest",
            }],
        })

    def test_no_current_character(self) -> None:
        self.session.scalar.return_value = None

        response = self.client.get("/location")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Character not found"})
