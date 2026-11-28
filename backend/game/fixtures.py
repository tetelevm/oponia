import argparse
from datetime import timedelta
import json
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import yaml

from database import get_engine
from models import (
    Enemy, EnemyLocation, Image, Item, ItemLocation, ItemType,
    Location, LocationConnection,
)
from services.images import create_image, save_image_file
from settings import REPO_ROOT, get_settings

ASCII_SIZES = {"locations": (80, 20), "enemies": (25, 10), "items": (8, 4)}


def _read_yaml(path: Path) -> list[dict]:
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    if rows is None:
        return []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"Expected a list of records in {path}")
    return rows


def _read_ascii(path: Path, stem: str) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data[stem]
    width, height = ASCII_SIZES[path.parent.name]
    if (
        not isinstance(rows, list)
        or len(rows) != height
        or any(not isinstance(row, str) or len(row) != width for row in rows)
        or any(ord(char) < 32 or ord(char) > 126 for row in rows for char in row)
    ):
        raise ValueError(f"{path}: {stem} must contain {width} x {height} ASCII cells")
    return "\n".join(rows)


class FixtureLoader:
    def __init__(
        self, session: Session, directory: Path, media_root: Path,
    ) -> None:
        self.session = session
        self.directory = directory.resolve()
        self.media_root = media_root
        self._images: dict[str, Image] = {}
        self._locations: dict[str, Location] = {}
        self._written_files: list[Path] = []
        self._retired_urls: set[str] = set()
        self._seen_keys: set[tuple[type, str]] = set()

    def load(self) -> dict[str, int]:
        """Load all stages in one transaction and remove new files on failure."""
        self._images.clear()
        self._locations.clear()
        self._written_files.clear()
        self._retired_urls.clear()
        self._seen_keys.clear()
        try:
            with self.session.begin():
                counts = {
                    "images": self._load_images(),
                    "locations": self._load_locations(),
                    "enemies": self._load_enemies(),
                    "items": self._load_items(),
                }
                files = self._unreferenced_files(self._retired_urls)
        except Exception:
            for path in self._written_files:
                path.unlink(missing_ok=True)
            raise
        finally:
            self._written_files.clear()
            self._retired_urls.clear()
        for path in files:
            path.unlink(missing_ok=True)
        return counts

    def remove(self) -> dict[str, int]:
        """Delete matching records, then remove their local image files."""
        image_rows = _read_yaml(self.directory / "images.yaml")
        location_rows = _read_yaml(self.directory / "locations.yaml")
        enemy_rows = _read_yaml(self.directory / "enemies.yaml")
        item_rows = [
            row for path in sorted((self.directory / "items").glob("*.yaml"))
            for row in _read_yaml(path)
        ]
        with self.session.begin():
            counts = {
                "items": self._remove_records(Item, item_rows),
                "enemies": self._remove_records(Enemy, enemy_rows),
                "locations": self._remove_records(Location, location_rows),
            }
            counts["images"], files = self._remove_images(image_rows)
        for path in files:
            path.unlink(missing_ok=True)
        return counts

    def _remove_records(self, model: type, rows: list[dict]) -> int:
        slugs = [row["slug"] for row in rows]
        deleted = self.session.scalars(
            delete(model).where(model.slug.in_(slugs)).returning(model.id),
        ).all()
        return len(deleted)

    def _remove_images(self, rows: list[dict]) -> tuple[int, set[Path]]:
        labels = [row["label"] for row in rows]
        deleted_urls = self.session.scalars(
            delete(Image).where(Image.label.in_(labels)).returning(Image.image),
        ).all()
        return len(deleted_urls), self._unreferenced_files(set(deleted_urls))

    def _media_file(self, url: str) -> Path | None:
        if not url.startswith("/media/"):
            return None
        path = self.media_root / url.removeprefix("/media/")
        root = self.media_root.resolve()
        if not path.resolve().is_relative_to(root) or path.is_dir():
            raise ValueError(f"Image path must be a file inside media: {url}")
        return path

    def _unreferenced_files(self, urls: set[str]) -> set[Path]:
        retained = set(self.session.scalars(
            select(Image.image).where(Image.image.in_(urls)),
        ))
        files = set()
        for url in urls - retained:
            path = self._media_file(url)
            if path is not None:
                files.add(path)
        return files

    @staticmethod
    def _update_fields(record, values: dict) -> None:
        for field, value in values.items():
            if getattr(record, field) != value:
                setattr(record, field, value)

    def _upsert(self, model: type, row: dict):
        key = (model, row["slug"])
        if key in self._seen_keys:
            raise ValueError(f"Duplicate {model.__name__} slug: {row['slug']}")
        self._seen_keys.add(key)
        record = self.session.scalar(select(model).where(model.slug == row["slug"]))
        if record is None:
            record = model(**row)
            self.session.add(record)
        else:
            self._update_fields(record, row)
        return record

    def _sync_links(
        self, owner, relationship: str, model: type, target_field: str,
        rows: list[dict],
    ) -> None:
        collection = getattr(owner, relationship)
        existing = {getattr(link, target_field + "_id"): link for link in collection}
        desired = set()
        for row in rows:
            row = row.copy()
            target = self._locations[row.pop(target_field)]
            if target.id in desired:
                raise ValueError(f"Duplicate {target_field} link: {target.slug}")
            desired.add(target.id)
            row.setdefault("order", 0)
            row.setdefault("conditions", [])
            if target.id in existing:
                self._update_fields(existing[target.id], row)
            else:
                collection.append(model(**{target_field: target}, **row))
        for target_id, link in existing.items():
            if target_id not in desired:
                collection.remove(link)

    def _resolve_images(self, row: dict) -> dict:
        row = row.copy()
        for field in ("image", "icon"):
            reference = row.get(field)
            if reference is not None:
                if reference not in self._images:
                    raise ValueError(f"Unknown image reference: {reference}")
                row[field] = self._images[reference]
        return row

    def _load_images(self) -> int:
        labels = set()
        for row in _read_yaml(self.directory / "images.yaml"):
            source = (self.directory / row["image"]).resolve()
            if not source.is_relative_to(self.directory):
                raise ValueError("Image paths must stay inside the fixture set")
            if source.stem in self._images or row["label"] in labels:
                raise ValueError(f"Duplicate image key or label: {source.stem}")
            labels.add(row["label"])
            ascii_art = _read_ascii(source.parent / "ascii.json", source.stem)
            matches = self.session.scalars(
                select(Image).where(Image.label == row["label"]).limit(2),
            ).all()
            if len(matches) > 1:
                raise ValueError(f"Multiple images have label: {row['label']}")
            image = matches[0] if matches else None
            if image is None:
                with source.open("rb") as file:
                    image = create_image(
                        self.session, file, label=row["label"], ascii_art=ascii_art,
                        media_root=self.media_root,
                    )
                self._written_files.append(
                    self.media_root / image.image.removeprefix("/media/"),
                )
            else:
                path = self._media_file(image.image)
                if path is None or not path.is_file() or (
                    path.read_bytes() != source.read_bytes()
                ):
                    with source.open("rb") as file:
                        url = save_image_file(
                            file, label=row["label"], media_root=self.media_root,
                        )
                    self._written_files.append(
                        self.media_root / url.removeprefix("/media/"),
                    )
                    self._retired_urls.add(image.image)
                    image.image = url
                self._update_fields(image, {"ascii_art": ascii_art})
            self._images[source.stem] = image
        return len(self._images)

    def _load_locations(self) -> int:
        connections = []
        for row in _read_yaml(self.directory / "locations.yaml"):
            row = self._resolve_images(row)
            links = row.pop("outgoing_connections", [])
            location = self._upsert(Location, row)
            self._locations[location.slug] = location
            connections.append((location, links))
        self.session.flush()
        for source, links in connections:
            self._sync_links(
                source, "outgoing_connections", LocationConnection, "target", links,
            )
        self.session.flush()
        return len(self._locations)

    def _load_enemies(self) -> int:
        rows = _read_yaml(self.directory / "enemies.yaml")
        for row in rows:
            row = self._resolve_images(row)
            links = row.pop("location_links", [])
            enemy = self._upsert(Enemy, row)
            self._sync_links(enemy, "location_links", EnemyLocation, "location", links)
        self.session.flush()
        return len(rows)

    def _load_items(self) -> int:
        count = 0
        for path in sorted((self.directory / "items").glob("*.yaml")):
            for row in _read_yaml(path):
                row = self._resolve_images(row)
                links = row.pop("location_links", [])
                row["type"] = ItemType(row["type"])
                if row.get("lifetime") is not None:
                    row["lifetime"] = timedelta(seconds=row["lifetime"])
                item = self._upsert(Item, row)
                self._sync_links(
                    item, "location_links", ItemLocation, "location", links,
                )
                count += 1
        self.session.flush()
        return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Load or remove a game fixture set")
    parser.add_argument("action", choices=("load", "remove"))
    parser.add_argument("fixture_set", help="Directory name under fixtures/")
    args = parser.parse_args()
    directory = REPO_ROOT / "fixtures" / args.fixture_set
    try:
        with Session(get_engine()) as session:
            loader = FixtureLoader(session, directory, get_settings().media_root)
            counts = loader.load() if args.action == "load" else loader.remove()
    except (ValueError, KeyError, OSError, yaml.YAMLError, SQLAlchemyError) as exc:
        parser.exit(1, f"Fixture {args.action} failed: {exc}\n")
    action = "Loaded" if args.action == "load" else "Removed"
    print(action + " " + ", ".join(f"{value} {key}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
