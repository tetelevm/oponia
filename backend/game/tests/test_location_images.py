import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import get_session
from main import app
from models import Character, Image, Location


class LocationImageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=Session)
        self.session.scalars.return_value.all.return_value = []
        app.dependency_overrides[get_session] = lambda: self.session
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)

    def test_missing_ascii_does_not_fall_back_to_url(self) -> None:
        location = Location(
            id=uuid4(), slug="village", name="Village",
            image=Image(image="/images/village.png", label="Village"),
        )
        character = Character(
            id=uuid4(), nickname="Hero", level=3, coins=120, platinum=0,
            location=location,
        )
        self.session.scalar.return_value = character

        response = self.client.get(
            "/location", params={"image_format": "ascii"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["location"]["image"])
