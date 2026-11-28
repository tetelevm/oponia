from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from PIL import Image as PillowImage
from PIL import UnidentifiedImageError
from sqlalchemy.orm import Session

from models import Image
from settings import get_settings

MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 20_000_000
IMAGE_EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def _validate_image(source: BinaryIO, label: str) -> tuple[bytes, str]:
    if not label.strip() or len(label) > 64:
        raise ValueError("Image label must contain 1 to 64 characters")

    data = source.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("Image file must not exceed 10 MiB")

    try:
        with PillowImage.open(BytesIO(data), formats=list(IMAGE_EXTENSIONS)) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError("Image must not exceed 20 million pixels")
            if getattr(image, "is_animated", False):
                raise ValueError("Animated images are not supported")
            extension = IMAGE_EXTENSIONS[image.format]
            image.verify()
        with PillowImage.open(BytesIO(data)) as image:
            image.load()
    except (
        UnidentifiedImageError, OSError, SyntaxError,
        PillowImage.DecompressionBombError,
    ) as exc:
        raise ValueError("File must be a valid JPEG, PNG or WebP image") from exc

    return data, extension


def save_image_file(
    source: BinaryIO,
    *,
    label: str,
    media_root: Path | None = None,
) -> str:
    data, extension = _validate_image(source, label)

    root = media_root if media_root is not None else get_settings().media_root
    directory = root / "uploads"
    directory.mkdir(parents=True, exist_ok=True)
    filename = uuid4().hex + extension
    path = directory / filename
    target = path.open("xb")
    try:
        with target:
            target.write(data)
        path.chmod(0o644)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return f"/media/uploads/{filename}"


def create_image(
    session: Session,
    source: BinaryIO,
    *,
    label: str,
    ascii_art: str | None = None,
    media_root: Path | None = None,
) -> Image:
    url = save_image_file(source, label=label, media_root=media_root)
    record = Image(image=url, label=label, ascii_art=ascii_art)
    try:
        session.add(record)
        session.flush()
    except Exception:
        root = media_root if media_root is not None else get_settings().media_root
        (root / url.removeprefix("/media/")).unlink(missing_ok=True)
        raise
    return record
