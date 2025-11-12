# Setup Guide

## Quick Start (5 minutes)

### 1. Get Your FAL.ai API Key
- Visit https://www.fal.ai
- Sign up for a free account
- Go to your account settings and copy your API key

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Your API Key

**Windows (PowerShell):**
```powershell
$env:FAL_KEY='your_api_key_here'
```

**Windows (Command Prompt):**
```cmd
set FAL_KEY=your_api_key_here
```

**Linux/macOS:**
```bash
export FAL_KEY='your_api_key_here'
```

### 4. Run the Tool

```bash
python main.py your_image.jpg
```

That's it! The tool will:
1. Validate your image
2. Generate 72 views at 5-degree increments
3. Save them to `generated_views/image_name/`
4. Create a montage preview

## Next Steps

- Read the [README.md](README.md) for detailed usage and parameter explanations
- Try different parameters to fine-tune the output
- Check [Configuration](#configuration) below if you need to adjust rate limiting

## Configuration

If you hit rate limits or want to customize behavior, edit `config.py`:

```python
# Slower API calls (helps with rate limits)
THROTTLE_DELAY = 2.0  # Increase from 1.5

# More aggressive retries
MAX_RETRIES = 7  # Increase from 5
INITIAL_RETRY_DELAY = 3  # Increase from 2

# Change where images are saved
OUTPUT_BASE_DIR = Path("my_generated_views")
```

## Typical Generation Times

With 72 images and rate limiting:

| Configuration | Estimated Time |
|---------------|-----------------|
| Default (6 steps, throttle 1.5s) | 2-4 minutes |
| Fast (4 steps, throttle 1.5s) | 1.5-2.5 minutes |
| High Quality (15 steps, throttle 1.5s) | 6-8 minutes |

Each image takes 5-30 seconds on FAL.ai depending on `num_inference_steps`.

## Common Issues

### "FAL_KEY not set"
Make sure you've set the environment variable in YOUR CURRENT terminal session. Opening a new terminal requires setting it again.

### "Rate limit exceeded"
Increase `THROTTLE_DELAY` in `config.py` from 1.5 to 2.0 or higher.

### Very slow generation
This is normal! With 72 images × throttling, expect several minutes. You can:
- Use `--num-steps 4` for faster (lower quality) generation
- Use `--quiet` to suppress the logs and feel like it's faster 😄

## File Structure

```
easy-3dgs/
├── main.py              # Run this: python main.py image.jpg
├── config.py            # Edit for rate limit tweaks
├── api_client.py        # FAL.ai API logic
├── image_processor.py   # Image validation
├── requirements.txt     # Dependencies (pip install -r)
├── README.md            # Full documentation
└── SETUP.md            # This file
```

## Tips

- **Test with a small image first** to make sure everything works
- **Use `--no-montage`** if you don't need the preview grid
- **Experiment with `--lora-scale`** (0.5-1.5) to adjust rotation intensity
- **Try `--move-forward 5`** for a zoom effect on the product

## Next: Advanced Usage

Once you're up and running, check [README.md](README.md#advanced-usage-with-custom-parameters) for advanced options like:
- Custom camera angles
- Zoom effects
- Quality vs. speed tradeoffs
- Batch processing tips

Good luck! 🚀
