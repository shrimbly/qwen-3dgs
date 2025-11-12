#!/usr/bin/env python3
"""
Multi-Angle Image Generation Tool using FAL.ai's Qwen Model

This script takes an input image and generates 72 different views of the product
at 5-degree rotation increments (full 360-degree rotation) using FAL.ai's
Qwen Image Edit Plus LoRA model.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from api_client import APIClient
from image_processor import ImageProcessor
from config import (
    DEFAULT_GUIDANCE_SCALE,
    DEFAULT_NUM_INFERENCE_STEPS,
    DEFAULT_LORA_SCALE,
    VERBOSE,
)


def setup_environment():
    """Ensure FAL_KEY environment variable is set."""
    if not os.getenv("FAL_KEY"):
        print("ERROR: FAL_KEY environment variable not set")
        print("Please set your FAL.ai API key:")
        print("  export FAL_KEY='your_api_key_here'  # Unix/Linux/Mac")
        print("  set FAL_KEY=your_api_key_here        # Windows CMD")
        print("  $env:FAL_KEY='your_api_key_here'     # Windows PowerShell")
        sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate multiple angle views of a product image using FAL.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py image.jpg
  python main.py product.png --guidance-scale 1.5 --lora-scale 1.2
  python main.py photo.jpg --guidance-scale 2.0 --num-steps 10
        """,
    )

    parser.add_argument(
        "image",
        type=str,
        help="Path to the input image file",
    )

    parser.add_argument(
        "--guidance-scale",
        type=float,
        default=DEFAULT_GUIDANCE_SCALE,
        help=f"CFG guidance scale (0-20, default: {DEFAULT_GUIDANCE_SCALE})",
    )

    parser.add_argument(
        "--num-steps",
        type=int,
        default=DEFAULT_NUM_INFERENCE_STEPS,
        help=f"Number of inference steps (2-50, default: {DEFAULT_NUM_INFERENCE_STEPS})",
    )

    parser.add_argument(
        "--lora-scale",
        type=float,
        default=DEFAULT_LORA_SCALE,
        help=f"LoRA scale for camera control (0-4, default: {DEFAULT_LORA_SCALE})",
    )

    parser.add_argument(
        "--move-forward",
        type=float,
        default=0,
        help="Camera zoom/forward movement (0-10, default: 0)",
    )

    parser.add_argument(
        "--vertical-angle",
        type=float,
        default=0,
        help="Vertical camera angle (-1 to 1, default: 0)",
    )

    parser.add_argument(
        "--wide-angle",
        action="store_true",
        help="Enable wide-angle lens effect",
    )

    parser.add_argument(
        "--no-montage",
        action="store_true",
        help="Skip creating a montage of generated images",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )

    return parser.parse_args()


def validate_arguments(args):
    """Validate command-line arguments."""
    errors = []

    # Validate guidance scale
    if not 0 <= args.guidance_scale <= 20:
        errors.append(f"guidance_scale must be between 0 and 20, got {args.guidance_scale}")

    # Validate num steps
    if not 2 <= args.num_steps <= 50:
        errors.append(f"num_steps must be between 2 and 50, got {args.num_steps}")

    # Validate lora scale
    if not 0 <= args.lora_scale <= 4:
        errors.append(f"lora_scale must be between 0 and 4, got {args.lora_scale}")

    # Validate move forward
    if not 0 <= args.move_forward <= 10:
        errors.append(f"move_forward must be between 0 and 10, got {args.move_forward}")

    # Validate vertical angle
    if not -1 <= args.vertical_angle <= 1:
        errors.append(f"vertical_angle must be between -1 and 1, got {args.vertical_angle}")

    if errors:
        print("Argument Validation Errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 60)
    print("Multi-Angle Image Generation Tool")
    print("Powered by FAL.ai Qwen Image Edit Plus LoRA")
    print("=" * 60 + "\n")


def print_summary(args, image_path, saved_files):
    """Print generation summary."""
    print("\n" + "=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    print(f"Input Image: {image_path}")
    print(f"Total Views Generated: {len(saved_files)}")
    print(f"Rotation Range: 0° - 355° (5° increments)")
    if saved_files:
        output_dir = saved_files[0].parent
        print(f"Output Directory: {output_dir}")
        print(f"Disk Space Used: {sum(f.stat().st_size for f in saved_files) / 1024 / 1024:.2f} MB")
    print("\nParameters Used:")
    print(f"  Guidance Scale: {args.guidance_scale}")
    print(f"  Inference Steps: {args.num_steps}")
    print(f"  LoRA Scale: {args.lora_scale}")
    if args.move_forward > 0:
        print(f"  Camera Zoom: {args.move_forward}")
    if args.vertical_angle != 0:
        print(f"  Vertical Angle: {args.vertical_angle}")
    if args.wide_angle:
        print(f"  Wide-Angle Lens: Enabled")
    print("=" * 60 + "\n")


def main():
    """Main execution function."""
    print_banner()

    # Setup and validation
    setup_environment()
    args = parse_arguments()
    validate_arguments(args)

    # Suppress verbose output if quiet flag is set
    if args.quiet:
        import config
        config.VERBOSE = False

    # Initialize components
    try:
        image_processor = ImageProcessor()
        api_client = APIClient()
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Process input image
    try:
        print(f"Processing input image: {args.image}")
        image_path = image_processor.validate_local_image(args.image)
        image_name = image_path.stem
        image_info = image_processor.get_image_info(image_path)

        print(f"✓ Image validated: {image_info['filename']}")
        print(f"  Dimensions: {image_info['width']}x{image_info['height']}")
        print(f"  Size: {image_info['size_bytes'] / 1024:.1f} KB\n")

    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Upload image to FAL.ai
    try:
        print("Uploading image to FAL.ai...")
        image_url = image_processor.upload_image_to_fal(image_path)
        print(f"✓ Image uploaded\n")
    except IOError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Generate multi-angle views
    try:
        print("Generating multi-angle views...")
        print(f"This will generate 72 images (5° increments) - please be patient...\n")

        start_time = datetime.now()

        results = api_client.generate_multi_angle_views(
            image_url=image_url,
            guidance_scale=args.guidance_scale,
            num_inference_steps=args.num_steps,
            lora_scale=args.lora_scale,
            move_forward=args.move_forward,
            vertical_angle=args.vertical_angle,
            wide_angle_lens=args.wide_angle,
        )

        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"\n✓ Generation complete in {elapsed_time:.1f} seconds\n")

    except Exception as e:
        print(f"ERROR during generation: {e}")
        sys.exit(1)

    # Save generated images
    try:
        print("Saving generated images...")
        output_dir = image_processor.create_output_directory(image_name)
        saved_files = image_processor.save_generated_images(results, output_dir, "png")
        print(f"✓ Saved {len(saved_files)} images\n")

    except Exception as e:
        print(f"ERROR while saving images: {e}")
        sys.exit(1)

    # Create montage if requested
    if not args.no_montage and saved_files:
        try:
            print("Creating montage preview...")
            montage_path = output_dir / f"{image_name}_montage.png"
            if image_processor.create_montage(saved_files, montage_path):
                print(f"✓ Montage created: {montage_path}\n")
        except Exception as e:
            print(f"Note: Could not create montage: {e}\n")

    # Print summary
    print_summary(args, args.image, saved_files)

    return 0


if __name__ == "__main__":
    sys.exit(main())
