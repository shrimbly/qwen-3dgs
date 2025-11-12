"""Configuration and constants for the multi-angle image generation tool."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
FAL_API_ENDPOINT = "fal-ai/qwen-image-edit-plus-lora-gallery/multiple-angles"
FAL_API_KEY = os.getenv("FAL_KEY", "")

# Default Model Parameters
DEFAULT_GUIDANCE_SCALE = 1.0
DEFAULT_NUM_INFERENCE_STEPS = 6
DEFAULT_ACCELERATION = "regular"
DEFAULT_NEGATIVE_PROMPT = " "
DEFAULT_LORA_SCALE = 1.0
DEFAULT_OUTPUT_FORMAT = "png"

# Image Generation Settings
ROTATION_INCREMENT = 5  # degrees
FULL_ROTATION = 360  # degrees
TOTAL_IMAGES = FULL_ROTATION // ROTATION_INCREMENT  # 72 images

# Camera Control Defaults
DEFAULT_MOVE_FORWARD = 0  # 0-10, 0 = no movement
DEFAULT_VERTICAL_ANGLE = 0  # -1 to 1, 0 = neutral
DEFAULT_WIDE_ANGLE_LENS = False

# Rate Limiting and Retry Configuration
THROTTLE_DELAY = 1.5  # seconds between API calls
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 2  # seconds
MAX_RETRY_DELAY = 60  # seconds
RETRY_BACKOFF_MULTIPLIER = 2
TIMEOUT = 300  # seconds

# Supported Image Formats
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}

# Output Directory
OUTPUT_BASE_DIR = Path("generated_views")
OUTPUT_BASE_DIR.mkdir(exist_ok=True)

# Logging
VERBOSE = True
