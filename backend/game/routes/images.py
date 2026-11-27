from models import Image
from schemas.components import ImageFormat, ImageRepresentationSchema


def get_image_representation(
    image: Image | None, image_format: ImageFormat,
) -> ImageRepresentationSchema | None:
    if image is None:
        return None

    value = image.ascii_art if image_format == ImageFormat.ASCII else image.image
    if value is None:
        return None

    return ImageRepresentationSchema(format=image_format, value=value)
