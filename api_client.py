"""FAL.ai API client with rate limiting and retry logic."""

import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
import fal_client
from config import (
    FAL_API_ENDPOINT,
    FAL_API_KEY,
    THROTTLE_DELAY,
    MAX_RETRIES,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
    RETRY_BACKOFF_MULTIPLIER,
    TIMEOUT,
    DEFAULT_GUIDANCE_SCALE,
    DEFAULT_NUM_INFERENCE_STEPS,
    DEFAULT_ACCELERATION,
    DEFAULT_NEGATIVE_PROMPT,
    DEFAULT_LORA_SCALE,
    DEFAULT_OUTPUT_FORMAT,
    VERBOSE,
    ROTATION_INCREMENT,
    FULL_ROTATION,
)


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class APIClient:
    """Client for interacting with FAL.ai API with rate limiting."""

    def __init__(self, api_key: str = FAL_API_KEY):
        """
        Initialize the API client.

        Args:
            api_key: FAL.ai API key. Uses FAL_KEY environment variable if not provided.
        """
        if not api_key:
            raise ValueError(
                "FAL_KEY environment variable not set. "
                "Please set it before running the script."
            )

        self.api_key = api_key
        fal_client.api_key = api_key
        self._log("API client initialized")

    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if VERBOSE:
            print(f"[API] {message}")

    def _apply_throttle(self):
        """Apply throttle delay between API calls."""
        time.sleep(THROTTLE_DELAY)

    def generate_multi_angle_views(
        self,
        image_url: str,
        guidance_scale: float = DEFAULT_GUIDANCE_SCALE,
        num_inference_steps: int = DEFAULT_NUM_INFERENCE_STEPS,
        lora_scale: float = DEFAULT_LORA_SCALE,
        move_forward: float = 0,
        vertical_angle: float = 0,
        wide_angle_lens: bool = False,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
    ) -> List[Dict]:
        """
        Generate multi-angle views of an image by rotating the camera.

        Args:
            image_url: URL of the image to process
            guidance_scale: CFG scale (0-20)
            num_inference_steps: Number of inference steps (2-50)
            lora_scale: LoRA scale (0-4)
            move_forward: Camera zoom (0-10)
            vertical_angle: Vertical camera angle (-1 to 1)
            wide_angle_lens: Enable wide-angle lens effect
            output_format: Output image format (png, jpeg, webp)

        Returns:
            List of generated image URLs
        """
        results = []
        total_images = FULL_ROTATION // ROTATION_INCREMENT

        self._log(f"Starting generation of {total_images} multi-angle views")
        self._log(f"Rotation increment: {ROTATION_INCREMENT}°")

        for i, angle in enumerate(range(0, FULL_ROTATION, ROTATION_INCREMENT), 1):
            # Rotate left (positive) for positive angles
            rotate_right_left = angle

            self._log(f"Generating view {i}/{total_images} at rotation {angle}°")

            try:
                # Apply throttle delay before API call
                self._apply_throttle()

                # Call API with retry logic
                result = self._call_api_with_retry(
                    image_url=image_url,
                    rotate_right_left=rotate_right_left,
                    guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps,
                    lora_scale=lora_scale,
                    move_forward=move_forward,
                    vertical_angle=vertical_angle,
                    wide_angle_lens=wide_angle_lens,
                    output_format=output_format,
                )

                results.append({
                    "angle": angle,
                    "url": result["images"][0]["url"],
                    "seed": result.get("seed"),
                })

                self._log(f"✓ Successfully generated view at {angle}°")

            except RateLimitError as e:
                self._log(f"✗ Rate limit exceeded at {angle}°: {e}")
                raise
            except Exception as e:
                self._log(f"✗ Failed to generate view at {angle}°: {e}")
                raise

        self._log(f"✓ Successfully generated all {total_images} views")
        return results

    def _call_api_with_retry(
        self,
        image_url: str,
        rotate_right_left: float,
        guidance_scale: float,
        num_inference_steps: int,
        lora_scale: float,
        move_forward: float,
        vertical_angle: float,
        wide_angle_lens: bool,
        output_format: str,
    ) -> Dict:
        """
        Call the FAL.ai API with exponential backoff retry logic.

        Args:
            image_url: URL of the image
            rotate_right_left: Rotation angle
            guidance_scale: CFG scale
            num_inference_steps: Number of inference steps
            lora_scale: LoRA scale
            move_forward: Camera zoom
            vertical_angle: Vertical camera angle
            wide_angle_lens: Enable wide-angle lens
            output_format: Output format

        Returns:
            API response dictionary

        Raises:
            RateLimitError: If rate limit is exceeded after all retries
        """
        retry_delay = INITIAL_RETRY_DELAY
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = fal_client.subscribe(
                    FAL_API_ENDPOINT,
                    arguments={
                        "image_urls": [image_url],
                        "guidance_scale": guidance_scale,
                        "num_inference_steps": num_inference_steps,
                        "acceleration": DEFAULT_ACCELERATION,
                        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
                        "enable_safety_checker": True,
                        "output_format": output_format,
                        "num_images": 1,
                        "rotate_right_left": rotate_right_left,
                        "move_forward": move_forward,
                        "vertical_angle": vertical_angle,
                        "wide_angle_lens": wide_angle_lens,
                        "lora_scale": lora_scale,
                    },
                )
                return result

            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                self._log(f"Attempt {attempt}/{MAX_RETRIES}: Timeout - retrying in {retry_delay}s")

            except Exception as e:
                error_str = str(e)

                # Check for rate limit error (429)
                if "429" in error_str or "rate limit" in error_str.lower():
                    if attempt == MAX_RETRIES:
                        raise RateLimitError(
                            f"Rate limit exceeded after {MAX_RETRIES} retries: {error_str}"
                        )
                    last_error = f"Rate limit: {error_str}"
                    self._log(f"Attempt {attempt}/{MAX_RETRIES}: Rate limited - retrying in {retry_delay}s")
                else:
                    last_error = str(e)
                    self._log(f"Attempt {attempt}/{MAX_RETRIES}: {error_str}")

            # Don't sleep after the last failed attempt
            if attempt < MAX_RETRIES:
                time.sleep(retry_delay)
                # Exponential backoff with cap
                retry_delay = min(retry_delay * RETRY_BACKOFF_MULTIPLIER, MAX_RETRY_DELAY)

        # All retries exhausted
        raise Exception(f"API call failed after {MAX_RETRIES} attempts. Last error: {last_error}")

    def download_image(self, image_url: str, output_path: Path) -> bool:
        """
        Download image from URL and save to file.

        Args:
            image_url: URL of the image
            output_path: Path to save the image

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(image_url, timeout=TIMEOUT)
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            self._log(f"Downloaded image to {output_path}")
            return True

        except Exception as e:
            self._log(f"Failed to download image from {image_url}: {e}")
            return False
