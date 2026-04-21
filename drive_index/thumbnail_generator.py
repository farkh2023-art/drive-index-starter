"""Thumbnail generation implementation."""

from pathlib import Path
from typing import Optional
from .exceptions import ThumbnailGenerationError


class ThumbnailGenerator:
    """Generator for creating image thumbnails."""

    def __init__(self, size: tuple = (260, 180), format: str = "JPEG"):
        """Initialize thumbnail generator.

        Args:
            size: Thumbnail size as (width, height) tuple
            format: Output image format (default: JPEG)
        """
        self.size = size
        self.format = format

    def generate(self, image_path: str, output_folder: Path) -> Optional[str]:
        """Generate thumbnail for an image.

        Args:
            image_path: Path to the source image
            output_folder: Directory to save thumbnail in

        Returns:
            Path to generated thumbnail, or None if generation fails

        Raises:
            ThumbnailGenerationError: If thumbnail generation fails
        """
        try:
            from PIL import Image

            # Ensure output folder exists
            output_folder.mkdir(parents=True, exist_ok=True)

            # Generate thumbnail
            with Image.open(image_path) as img:
                img.thumbnail(self.size)
                thumb_path = output_folder / (Path(image_path).stem + "_thumb.jpg")
                img.save(thumb_path, self.format)

            return str(thumb_path)
        except Exception as e:
            raise ThumbnailGenerationError(
                f"Failed to generate thumbnail for {image_path}: {e}"
            )
