from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from PIL import Image as PillowImage
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Image
from services.images import MAX_FILE_BYTES, create_image


def image_bytes(image_format: str, *, animated: bool = False) -> bytes:
    result = BytesIO()
    with PillowImage.new("RGB", (8, 4), "red") as image:
        options = {}
        if animated:
            options = {
                "save_all": True,
                "append_images": [PillowImage.new("RGB", (8, 4), "blue")],
            }
        image.save(result, format=image_format, **options)
    return result.getvalue()


class ImageStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        Image.__table__.create(engine)
        self.session = Session(engine)
        self.addCleanup(self.session.close)

    def create(self, data: bytes, **kwargs) -> Image:
        return create_image(
            self.session, BytesIO(data), label="Test image",
            media_root=self.root, **kwargs,
        )

    def test_saves_original_bytes_unique_urls_and_model_record(self) -> None:
        for image_format, extension in (("JPEG", "jpg"), ("PNG", "png"),
                                        ("WEBP", "webp")):
            with self.subTest(image_format=image_format):
                data = image_bytes(image_format)
                first = self.create(data, ascii_art=" /\\\n/__\\")
                second = self.create(data)
                self.assertNotEqual(first.image, second.image)
                self.assertTrue(first.image.endswith("." + extension))
                path = self.root / first.image.removeprefix("/media/")
                self.assertEqual(path.read_bytes(), data)
                self.assertEqual(path.stat().st_mode & 0o777, 0o644)
                self.session.commit()
                self.session.expire_all()
                record = self.session.get(Image, first.id)
                self.assertEqual(record.ascii_art, " /\\\n/__\\")

    def test_rejects_invalid_oversized_and_animated_files_without_saving(self) -> None:
        for data in (
            b"", b"<svg></svg>", image_bytes("PNG")[:40],
            b"x" * (MAX_FILE_BYTES + 1), image_bytes("WEBP", animated=True),
        ):
            with self.subTest(size=len(data)):
                with self.assertRaises(ValueError):
                    self.create(data)
        with patch("services.images.MAX_PIXELS", 16):
            with self.assertRaisesRegex(ValueError, "pixels"):
                self.create(image_bytes("PNG"))
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertIsNone(self.session.scalar(select(Image)))

    def test_removes_file_if_database_flush_fails(self) -> None:
        session = Mock(spec=Session)
        session.flush.side_effect = RuntimeError("Database unavailable")
        with self.assertRaisesRegex(RuntimeError, "Database unavailable"):
            create_image(
                session, BytesIO(image_bytes("PNG")), label="Test",
                media_root=self.root,
            )
        self.assertEqual(list((self.root / "uploads").iterdir()), [])
