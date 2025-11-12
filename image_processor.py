"""Image processing and validation utilities."""

import os
import base64
from pathlib import Path
from typing import Optional
from PIL import Image
import requests
from config import SUPPORTED_FORMATS, OUTPUT_BASE_DIR, VERBOSE


class ImageProcessor:
    """Handle image validation and processing."""

    def __init__(self):
        """Initialize the image processor."""
        self._log("Image processor initialized")

    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if VERBOSE:
            print(f"[IMAGE] {message}")

    def validate_local_image(self, image_path: str) -> Path:
        """
        Validate that a local image file exists and is in a supported format.

        Args:
            image_path: Path to the image file

        Returns:
            Path object pointing to the image

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")

        file_ext = path.suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            supported = ", ".join(SUPPORTED_FORMATS)
            raise ValueError(
                f"Unsupported image format: {file_ext}. Supported formats: {supported}"
            )

        # Try to open the image to ensure it's valid
        try:
            with Image.open(path) as img:
                self._log(f"✓ Image validated: {path.name} ({img.width}x{img.height})")
                return path
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")

    def upload_image_to_fal(self, image_path: Path) -> str:
        """
        Convert a local image to base64 data URI for FAL.ai API.

        FAL.ai accepts base64-encoded images as data URIs.

        Args:
            image_path: Path to the local image

        Returns:
            Base64 data URI of the image

        Raises:
            IOError: If unable to read or encode the image
        """
        try:
            # Read the image file
            with open(image_path, "rb") as f:
                image_data = f.read()

            self._log(f"Read image file: {len(image_data)} bytes")

            # Determine the image format for the data URI
            suffix = image_path.suffix.lower()
            mime_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
                ".gif": "image/gif",
            }
            mime_type = mime_types.get(suffix, "image/jpeg")

            # Convert to base64 data URI
            b64_data = base64.b64encode(image_data).decode("utf-8")
            data_uri = f"data:{mime_type};base64,{b64_data}"

            self._log(f"Image converted to base64 data URI ({len(data_uri)} chars)")
            return data_uri

        except Exception as e:
            raise IOError(f"Failed to prepare image for upload: {e}")

    def create_output_directory(self, image_name: str) -> Path:
        """
        Create and return an output directory for generated images.

        Args:
            image_name: Name of the input image (without extension)

        Returns:
            Path to the output directory
        """
        output_dir = OUTPUT_BASE_DIR / image_name
        output_dir.mkdir(parents=True, exist_ok=True)
        self._log(f"Output directory: {output_dir}")
        return output_dir

    def save_generated_images(
        self,
        results: list,
        output_dir: Path,
        image_format: str = "png",
    ) -> list:
        """
        Download and save generated images with angle-based naming.

        Args:
            results: List of dicts with 'angle' and 'url' keys
            output_dir: Directory to save images
            image_format: Image format (png, jpeg, webp)

        Returns:
            List of saved file paths
        """
        saved_files = []

        for result in results:
            angle = result["angle"]
            url = result["url"]

            # Create filename with angle
            filename = f"view_{angle:03d}deg.{image_format}"
            output_path = output_dir / filename

            try:
                # Download the image
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Save to file
                with open(output_path, "wb") as f:
                    f.write(response.content)

                saved_files.append(output_path)
                self._log(f"✓ Saved: {filename}")

            except Exception as e:
                self._log(f"✗ Failed to save {filename}: {e}")

        return saved_files

    def get_image_info(self, image_path: Path) -> dict:
        """
        Get information about an image.

        Args:
            image_path: Path to the image

        Returns:
            Dictionary with image info
        """
        try:
            with Image.open(image_path) as img:
                return {
                    "filename": image_path.name,
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "size_bytes": image_path.stat().st_size,
                }
        except Exception as e:
            self._log(f"Error getting image info: {e}")
            return {}

    def create_montage(self, image_paths: list, output_path: Path, cols: int = 12) -> bool:
        """
        Create a montage of generated images for quick preview.

        Args:
            image_paths: List of image file paths
            output_path: Path to save the montage
            cols: Number of columns in montage

        Returns:
            True if successful, False otherwise
        """
        if not image_paths:
            self._log("No images to create montage from")
            return False

        try:
            images = []
            for path in sorted(image_paths):
                img = Image.open(path)
                images.append(img)

            # Calculate grid dimensions
            rows = (len(images) + cols - 1) // cols
            img_width, img_height = images[0].size

            # Create montage
            montage_width = img_width * cols
            montage_height = img_height * rows
            montage = Image.new("RGB", (montage_width, montage_height))

            for idx, img in enumerate(images):
                row = idx // cols
                col = idx % cols
                x = col * img_width
                y = row * img_height
                montage.paste(img, (x, y))

            montage.save(output_path)
            self._log(f"✓ Created montage: {output_path}")
            return True

        except Exception as e:
            self._log(f"Failed to create montage: {e}")
            return False
