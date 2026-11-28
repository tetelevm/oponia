import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text

from admin import setup_admin
from database_case import DatabaseTestCase
from models import Character, Image, Item, Location, LocationConnection
from settings import Settings


def admin_settings() -> Settings:
    return Settings(
        _env_file=None,
        postgres_db="test",
        postgres_user="test",
        postgres_password="test",
        admin_username="editor",
        admin_password="test-password",
        admin_secret_key="test-session-secret",
    )


class AdminAuthTests(unittest.TestCase):
    def test_login_protects_writes_and_logout_revokes_access(self) -> None:
        app = FastAPI()
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        setup_admin(app, engine, admin_settings())
        with TestClient(app, root_path="/api", follow_redirects=False) as client:
            for method, path in (
                ("GET", "/api/admin/"),
                ("GET", "/api/admin/image/create"),
                ("POST", "/api/admin/image/create"),
                ("DELETE", "/api/admin/image/delete?pks=missing"),
            ):
                response = client.request(method, path)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.headers["location"].endswith(
                    "/api/admin/login",
                ))
            response = client.post("/api/admin/login", data={
                "username": "editor", "password": "wrong",
            })
            self.assertEqual(response.status_code, 400)
            response = client.post("/api/admin/login", data={
                "username": "editor", "password": "test-password",
            })
            self.assertEqual(response.status_code, 302)
            self.assertEqual(client.get("/api/admin/").status_code, 200)
            client.get("/api/admin/logout")
            self.assertEqual(client.get("/api/admin/").status_code, 302)


class AdminDatabaseTests(DatabaseTestCase):
    def test_forms_create_and_edit_related_game_records(self) -> None:
        schema = self.session.scalar(text("SELECT current_schema()"))
        engine = create_engine(
            self.session.bind.engine.url,
            connect_args={"options": f"-csearch_path={schema}"},
        )
        self.addCleanup(engine.dispose)
        app = FastAPI()
        setup_admin(app, engine, admin_settings())
        with TestClient(app, root_path="/api", follow_redirects=False) as client:
            client.post("/api/admin/login", data={
                "username": "editor", "password": "test-password",
            })
            def create(identity: str, data: dict) -> None:
                response = client.post(f"/api/admin/{identity}/create", data=data)
                self.assertEqual(response.status_code, 302, response.text)

            create("image", {
                "label": "City", "image": "/media/city.png", "ascii_art": " /\\",
            })
            image = self.session.scalar(select(Image))
            create("location", {
                "slug": "city", "name": "City", "image": str(image.id),
                "sell_multiplier": "0",
            })
            location = self.session.scalar(select(Location))
            self.assertEqual(location.sell_multiplier, 0)
            self.assertEqual(location.image_id, image.id)
            create("character", {
                "nickname": "Hero", "location": str(location.id),
                "special_effects": '{"poison": {"damage": 2}}',
            })
            character = self.session.scalar(select(Character))
            self.assertEqual(character.location_id, location.id)
            self.assertEqual(character.special_effects, {"poison": {"damage": 2}})
            create("item", {
                "slug": "sword", "name": "Sword", "type": "weapon",
                "lifetime": "1 day", "special_effects": "{}",
            })
            item = self.session.scalar(select(Item))
            self.assertEqual(item.lifetime.total_seconds(), 86400)
            create("location-connection", {
                "source": str(location.id), "target": str(location.id),
                "conditions": ["level_2", "quest_done"], "order": "0",
            })
            connection = self.session.scalar(select(LocationConnection))
            self.assertEqual(connection.conditions, ["level_2", "quest_done"])
