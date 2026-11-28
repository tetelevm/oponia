import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from sqlalchemy import delete, event, func, select
from sqlalchemy.exc import IntegrityError
import yaml

from database_case import DatabaseTestCase
from fixtures import FixtureLoader
from models import (
    Character, CharacterItem, Enemy, Image, Item, ItemLocation, Location,
    LocationConnection,
)
from settings import REPO_ROOT


class FixtureTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.media = self.root / "media"
        self.source = REPO_ROOT / "fixtures" / "v-test"

    def test_repeated_load_keeps_records_files_and_database_unchanged(self) -> None:
        loader = FixtureLoader(self.session, self.source, self.media)
        counts = loader.load()
        self.assertEqual(counts, {
            "images": 29, "locations": 5, "enemies": 4, "items": 20,
        })
        city = self.session.scalar(select(Location).where(Location.slug == "city_0001"))
        self.assertEqual(city.image.label, "City")
        self.assertEqual(city.sell_multiplier, 0.5)
        rows = json.loads(
            (self.source / "images/locations/ascii.json").read_text(),
        )["loc_city"]
        self.assertEqual(city.image.ascii_art, "\n".join(rows))
        saved = self.media / city.image.image.removeprefix("/media/")
        original = self.source / "images/locations/loc_city.webp"
        self.assertEqual(saved.read_bytes(), original.read_bytes())
        wolf = self.session.scalar(select(Enemy).where(Enemy.slug == "wolf_0001"))
        self.assertEqual(wolf.image_id, wolf.icon_id)
        self.assertIn("`", wolf.image.ascii_art)
        sword = self.session.scalar(select(Item).where(Item.slug == "sword_0003"))
        self.assertEqual(sword.image.label, "Sword")
        self.assertEqual(sword.type.value, "weapon")
        self.assertEqual(sword.price_coins, 50)
        self.assertEqual({link.location.slug for link in sword.location_links}, {
            "city_0001", "village_0003",
        })
        self.assertEqual(self.session.scalar(
            select(func.count()).select_from(LocationConnection),
        ), 9)
        self.assertGreater(self.session.scalar(
            select(func.count()).select_from(ItemLocation),
        ), 20)
        image_id = city.image.id
        city_id = city.id
        file_times = {path: path.stat().st_mtime_ns
                      for path in (self.media / "uploads").iterdir()}
        self.session.rollback()
        writes = []

        def capture(connection, cursor, statement, parameters, context, many):
            if statement.lstrip().split()[0].upper() in {"INSERT", "UPDATE", "DELETE"}:
                writes.append(statement)

        event.listen(self.session.bind, "before_cursor_execute", capture)
        try:
            self.assertEqual(loader.load(), counts)
        finally:
            event.remove(self.session.bind, "before_cursor_execute", capture)
        self.assertEqual(writes, [])
        self.assertEqual(self.session.get(Location, city_id).image_id, image_id)
        self.assertEqual(
            {path: path.stat().st_mtime_ns for path in file_times}, file_times,
        )
        self.assertEqual(len(list((self.media / "uploads").iterdir())), 29)

    def test_load_updates_records_images_and_links(self) -> None:
        source = self.root / "fixtures"
        shutil.copytree(self.source, source)
        loader = FixtureLoader(self.session, source, self.media)
        loader.load()
        city = self.session.scalar(select(Location).where(Location.slug == "city_0001"))
        sword = self.session.scalar(select(Item).where(Item.slug == "sword_0003"))
        wolf = self.session.scalar(select(Enemy).where(Enemy.slug == "wolf_0001"))
        ids = (city.id, city.image.id, sword.id, sword.image.id, wolf.id)
        old_city_file = self.media / city.image.image.removeprefix("/media/")
        old_sword_url = sword.image.image
        (self.media / old_sword_url.removeprefix("/media/")).unlink()
        hero = Character(nickname="Hero", location=city)
        inventory = CharacterItem(character=hero, item=sword)
        self.session.add_all([hero, inventory])
        self.session.commit()

        def edit_yaml(relative, edit):
            path = source / relative
            rows = yaml.safe_load(path.read_text())
            edit(rows)
            path.write_text(yaml.safe_dump(rows))

        def edit_locations(rows):
            city = next(row for row in rows if row["slug"] == "city_0001")
            city["name"] = "Updated City"
            city["outgoing_connections"] = [
                {"target": "road_0002", "order": 7, "conditions": ["test"]},
                {"target": "new_place", "order": 8, "conditions": []},
            ]
            rows.append({"slug": "new_place", "name": "New place"})

        def edit_enemies(rows):
            wolf = next(row for row in rows if row["slug"] == "wolf_0001")
            wolf["health"] = 42
            wolf["location_links"] = [{"location": "forest_0004", "order": 5}]

        def edit_items(rows):
            sword = next(row for row in rows if row["slug"] == "sword_0003")
            sword.update(damage=99, lifetime=3600)
            sword["location_links"] = [{"location": "village_0003", "order": 8}]
            rows[:] = [row for row in rows if row["slug"] != "club_0001"]
            rows.append({"slug": "new_item", "name": "New item", "type": "weapon"})

        edit_yaml("locations.yaml", edit_locations)
        edit_yaml("enemies.yaml", edit_enemies)
        edit_yaml("items/weapon.yaml", edit_items)
        shutil.copyfile(source / "images/locations/loc_road.webp",
                        source / "images/locations/loc_city.webp")
        ascii_path = source / "images/enemies/ascii.json"
        ascii_rows = json.loads(ascii_path.read_text())
        ascii_rows["enem_wolf"][0] = "!" * 25
        ascii_path.write_text(json.dumps(ascii_rows))

        loader.load()
        city = self.session.get(Location, ids[0])
        sword = self.session.get(Item, ids[2])
        wolf = self.session.get(Enemy, ids[4])
        self.assertEqual(city.name, "Updated City")
        self.assertEqual(city.image_id, ids[1])
        self.assertFalse(old_city_file.exists())
        self.assertEqual(sword.image_id, ids[3])
        self.assertNotEqual(sword.image.image, old_sword_url)
        self.assertEqual(sword.damage, 99)
        self.assertEqual(sword.lifetime.total_seconds(), 3600)
        self.assertEqual(wolf.health, 42)
        self.assertEqual(wolf.image.ascii_art.splitlines()[0], "!" * 25)
        self.assertEqual({link.target.slug: link.order
                          for link in city.outgoing_connections}, {
            "road_0002": 7, "new_place": 8,
        })
        self.assertEqual([(link.location.slug, link.order)
                          for link in wolf.location_links], [("forest_0004", 5)])
        self.assertEqual([(link.location.slug, link.order)
                          for link in sword.location_links], [("village_0003", 8)])
        self.assertEqual(self.session.scalar(select(Character.location_id)), ids[0])
        self.assertEqual(self.session.scalar(select(CharacterItem.item_id)), ids[2])
        self.assertEqual(self.session.scalar(
            select(func.count()).select_from(Item),
        ), 21)
        self.assertEqual(len(list((self.media / "uploads").iterdir())), 29)

    def test_failed_update_preserves_existing_records_and_image_files(self) -> None:
        source = self.root / "fixtures"
        shutil.copytree(self.source, source)
        loader = FixtureLoader(self.session, source, self.media)
        loader.load()
        files = {path: path.read_bytes() for path in (self.media / "uploads").iterdir()}
        city = self.session.scalar(select(Location).where(Location.slug == "city_0001"))
        city_id, image_url = city.id, city.image.image
        self.session.rollback()
        shutil.copyfile(source / "images/locations/loc_road.webp",
                        source / "images/locations/loc_city.webp")
        path = source / "enemies.yaml"
        path.write_text(path.read_text().replace(
            "location: road_0002", "location: missing",
        ))
        with self.assertRaises(KeyError):
            loader.load()
        self.assertEqual(self.session.get(Location, city_id).image.image, image_url)
        self.assertEqual({path: path.read_bytes()
                          for path in (self.media / "uploads").iterdir()}, files)

    def test_invalid_input_rolls_back_records_and_files(self) -> None:
        source = self.root / "fixtures"
        loader = FixtureLoader(self.session, source, self.media)
        for failure in ("ascii", "location"):
            with self.subTest(failure=failure):
                shutil.copytree(self.source, source, dirs_exist_ok=True)
                if failure == "ascii":
                    path = source / "images/enemies/ascii.json"
                    data = json.loads(path.read_text())
                    data["enem_wolf"][0] = "too short"
                    path.write_text(json.dumps(data))
                    expected_error = ValueError
                else:
                    path = source / "enemies.yaml"
                    path.write_text(path.read_text().replace(
                        "location: road_0002", "location: missing",
                    ))
                    expected_error = KeyError
                with self.assertRaises(expected_error):
                    loader.load()
                for model in (Image, Location, Enemy, Item):
                    self.assertEqual(self.session.scalar(
                        select(func.count()).select_from(model),
                    ), 0)
                self.assertEqual(list((self.media / "uploads").iterdir()), [])
                self.session.rollback()

    def test_remove_matches_labels_and_slugs_and_preserves_unrelated_data(self) -> None:
        loader = FixtureLoader(self.session, self.source, self.media)
        loader.load()
        shared = self.session.scalar(select(Image).where(Image.label == "Sword"))
        shared_url = shared.image
        missing = self.session.scalar(select(Image).where(Image.label == "Wolf"))
        (self.media / missing.image.removeprefix("/media/")).unlink()
        uploads = self.media / "uploads"
        (uploads / "unrelated.webp").write_bytes(b"unrelated")
        (uploads / "duplicate.webp").write_bytes(b"duplicate")
        self.session.add_all([
            Image(label="Other", image="/media/uploads/unrelated.webp"),
            Image(label="Shared", image=shared_url),
            Image(label="City", image="/media/uploads/duplicate.webp"),
            Image(label="Wolf", image="https://example.test/wolf.webp"),
            Location(slug="other", name="Other"),
        ])
        for model, slug in (
            (Item, "club_0001"), (Enemy, "boar_0002"), (Location, "forest_0004"),
        ):
            self.session.execute(delete(model).where(model.slug == slug))
        self.session.commit()
        with self.assertRaisesRegex(ValueError, "Multiple images have label"):
            loader.load()
        removal_source = self.root / "remove-set"
        shutil.copytree(
            self.source, removal_source, ignore=shutil.ignore_patterns("images"),
        )
        remover = FixtureLoader(self.session, removal_source, self.media)
        self.assertEqual(remover.remove(), {
            "items": 19, "enemies": 3, "locations": 4, "images": 31,
        })
        self.assertEqual(set(self.session.scalars(select(Image.label))), {
            "Other", "Shared",
        })
        self.assertEqual(list(self.session.scalars(select(Location.slug))), ["other"])
        for model in (Item, Enemy, ItemLocation, LocationConnection):
            self.assertEqual(self.session.scalar(
                select(func.count()).select_from(model),
            ), 0)
        self.assertEqual({path.name for path in uploads.iterdir()}, {
            "unrelated.webp", Path(shared_url).name,
        })
        self.session.rollback()
        self.assertEqual(remover.remove(), {
            "items": 0, "enemies": 0, "locations": 0, "images": 0,
        })

    def test_occupied_location_rolls_back_removal_and_preserves_files(self) -> None:
        loader = FixtureLoader(self.session, self.source, self.media)
        loader.load()
        city = self.session.scalar(select(Location).where(Location.slug == "city_0001"))
        self.session.add(Character(nickname="Hero", location=city))
        self.session.commit()
        files = set((self.media / "uploads").iterdir())
        with self.assertRaises(IntegrityError):
            loader.remove()
        for model, count in ((Image, 29), (Location, 5), (Enemy, 4), (Item, 20)):
            self.assertEqual(self.session.scalar(
                select(func.count()).select_from(model),
            ), count)
        self.assertEqual(set((self.media / "uploads").iterdir()), files)
        self.assertEqual(self.session.scalar(select(Character.nickname)), "Hero")

    def test_remove_rejects_file_paths_outside_media(self) -> None:
        loader = FixtureLoader(self.session, self.source, self.media)
        loader.load()
        outside = self.root / "outside.webp"
        outside.write_bytes(b"outside")
        image = self.session.scalar(select(Image).where(Image.label == "City"))
        image.image = "/media/../outside.webp"
        self.session.commit()
        with self.assertRaisesRegex(ValueError, "inside media"):
            loader.remove()
        self.assertEqual(outside.read_bytes(), b"outside")
        self.assertEqual(self.session.scalar(
            select(func.count()).select_from(Image),
        ), 29)
        self.assertEqual(len(list((self.media / "uploads").iterdir())), 29)
