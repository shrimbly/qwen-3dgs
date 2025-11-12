# Easy 3DGS - Multi-Angle Image Generation Tool

Generate multiple angle views of product images using FAL.ai's Qwen Image Edit Plus LoRA model. This tool takes a single image and automatically generates 72 different camera views at 5-degree rotation increments (full 360-degree rotation).

## Features

- 🎯 **Full 360° Coverage**: Generates 72 images (0° to 355° in 5° increments)
- 📸 **High-Quality Output**: Uses FAL.ai's advanced Qwen model with LoRA precision control
- 🚀 **Rate Limit Protection**: Built-in exponential backoff retry logic and throttling
- 🔧 **Flexible Parameters**: Customize guidance scale, zoom, vertical angle, and more
- 🖼️ **Auto Montage**: Creates a preview montage of all generated views
- 💾 **Organized Output**: Saves images with angle-based naming for easy reference
- 🔐 **Safe & Reliable**: Comprehensive error handling and validation

## Requirements

- Python 3.8+
- FAL.ai API key

## Installation

1. **Clone or download this project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your FAL.ai API key**

   Get your API key from [fal.ai](https://www.fal.ai)

   Then set the environment variable:

   **Linux/Mac:**
   ```bash
   export FAL_KEY='your_api_key_here'
   ```

   **Windows (CMD):**
   ```cmd
   set FAL_KEY=your_api_key_here
   ```

   **Windows (PowerShell):**
   ```powershell
   $env:FAL_KEY='your_api_key_here'
   ```

## Usage

### Basic Usage

```bash
python main.py path/to/image.jpg
```

### Advanced Usage with Custom Parameters

```bash
python main.py image.jpg \
  --guidance-scale 1.5 \
  --num-steps 10 \
  --lora-scale 1.2 \
  --move-forward 2 \
  --vertical-angle 0.2 \
  --wide-angle
```

### Command-Line Options

| Option | Default | Range | Description |
|--------|---------|-------|-------------|
| `--guidance-scale` | 1.0 | 0-20 | CFG scale controlling how closely the model follows the prompt |
| `--num-steps` | 6 | 2-50 | Number of inference steps (more = higher quality but slower) |
| `--lora-scale` | 1.0 | 0-4 | LoRA scale for camera control strength |
| `--move-forward` | 0 | 0-10 | Camera zoom/forward movement (0=no movement, 10=close-up) |
| `--vertical-angle` | 0 | -1 to 1 | Vertical camera angle (-1=bird's-eye, 0=neutral, 1=worm's-eye) |
| `--wide-angle` | False | - | Enable wide-angle lens effect |
| `--no-montage` | False | - | Skip creating the montage preview image |
| `--quiet` | False | - | Suppress verbose output |

## Example Workflow

```bash
# Activate your Python environment (optional)
# python -m venv venv
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Set API key
export FAL_KEY='your_key_here'

# Generate views with custom parameters
python main.py product.jpg --guidance-scale 1.5 --lora-scale 1.2

# Generated images will be in ./generated_views/product/
```

## Output Structure

```
generated_views/
└── image_name/
    ├── view_000deg.png    # 0° view
    ├── view_005deg.png    # 5° view
    ├── view_010deg.png    # 10° view
    ├── ...
    ├── view_355deg.png    # 355° view
    └── image_name_montage.png  # Preview of all views
```

## How It Works

1. **Image Validation**: Checks that the input image exists and is in a supported format
2. **Upload**: Prepares the image for the FAL.ai API
3. **Generation Loop**: For each 5° increment (0° to 355°):
   - Calls the FAL.ai Qwen model with the rotation parameter
   - Applies exponential backoff retry logic if rate limited
   - Downloads the generated image
4. **Organization**: Saves all images with consistent naming
5. **Montage**: Creates a grid preview of all 72 views (optional)

## Rate Limiting & Throttling

The tool handles FAL.ai's rate limits gracefully:

- **Throttle Delay**: 1.5 seconds between API calls (configurable in `config.py`)
- **Retry Logic**: Automatic retry with exponential backoff (2s → 4s → 8s → etc.)
- **Max Retries**: Up to 5 attempts per image (configurable)
- **Max Retry Delay**: Capped at 60 seconds

If you hit persistent rate limits:
- Increase `THROTTLE_DELAY` in `config.py`
- Increase `INITIAL_RETRY_DELAY` in `config.py`
- Contact FAL.ai support for higher tier API key

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- BMP (.bmp)
- GIF (.gif)

## Performance Tips

- **Faster Generation**: Lower `--num-steps` (default 6 is good)
- **Better Quality**: Increase `--num-steps` or `--guidance-scale`
- **Closer Views**: Use `--move-forward 5-10` for zoom effect
- **Different Angles**: Experiment with `--vertical-angle` for tilted perspectives

## Configuration

Edit `config.py` to customize:

- `THROTTLE_DELAY`: Seconds between API calls
- `MAX_RETRIES`: Number of retry attempts
- `INITIAL_RETRY_DELAY`: Starting delay for retries
- `RETRY_BACKOFF_MULTIPLIER`: How much retry delay increases each attempt
- `OUTPUT_BASE_DIR`: Where to save generated images
- `VERBOSE`: Enable/disable detailed logging

## Troubleshooting

### "FAL_KEY environment variable not set"
Make sure you've set your API key:
```bash
export FAL_KEY='your_api_key_here'
```

### "Unsupported image format"
Check that your image is in one of the supported formats: JPG, PNG, WebP, BMP, or GIF

### "Rate limit exceeded"
The tool retries automatically, but if you keep hitting limits:
1. Increase `THROTTLE_DELAY` in `config.py`
2. Try with fewer images at a time
3. Contact FAL.ai support for API tier upgrade

### "Invalid image file"
Ensure:
- The image file is not corrupted
- The file extension matches the actual format
- The image is at least 256x256 pixels

### Generation is very slow
This is expected since:
- Each image takes 5-30 seconds depending on `num_steps`
- The tool intentionally throttles to avoid rate limits
- 72 images × throttle delay = significant total time
- Consider using `--num-steps 4` or `--no-montage` to speed up

## Project Structure

```
easy-3dgs/
├── main.py              # Entry point and CLI
├── api_client.py        # FAL.ai API wrapper with rate limiting
├── image_processor.py   # Image validation and processing
├── config.py            # Configuration constants
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## API Parameters Explained

### `guidance_scale` (CFG Scale)
Controls how strongly the model follows the prompt. Higher values make it stick more closely to the rotation instruction but may reduce quality.
- Default: 1.0
- Lower (0.5-1.0): More creative, less precise rotation
- Higher (2.0-5.0): More precise but may look artifacts

### `num_inference_steps`
How many refinement iterations the model runs. More steps = higher quality but slower.
- Minimum: 2 (fastest, lower quality)
- Default: 6 (good balance)
- Maximum: 50 (best quality, very slow)

### `lora_scale`
Controls the strength of the camera control LoRA model. This determines how well the rotation is applied.
- Lower (0.5): Subtle rotation
- Default: 1.0 (standard rotation)
- Higher (2.0-4.0): Very pronounced rotation

### `move_forward`
Simulates moving the camera closer to the object (zoom effect).
- 0: No zoom (object at standard distance)
- 5: Medium zoom
- 10: Close-up

### `vertical_angle`
Tilts the camera up or down.
- -1: Bird's eye view (looking down from above)
- 0: Neutral (looking straight ahead)
- 1: Worm's eye view (looking up from below)

## License

MIT License - feel free to use this tool for your projects!

## Support

For issues or questions:
- Check the Troubleshooting section above
- Review FAL.ai documentation: https://docs.fal.ai
- Create an issue in the project repository

## Acknowledgments

- Built with [FAL.ai](https://fal.ai) - Fast AI Inference Service
- Uses Qwen Image Edit Plus LoRA model for precise camera control
- Inspired by 3D Gaussian Splatting techniques

---

**Happy generating! 🚀**
