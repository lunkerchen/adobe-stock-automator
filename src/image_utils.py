"""
Image processing utilities for Adobe Stock Automator.
"""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image
from rich.console import Console

console = Console()

def upscale_image_to_mp(
    image_path: str | Path,
    target_mp: float = 6.0,
    quality: int = 95,
) -> bool:
    """
    Check if an image meets the Megapixel (MP) requirements for stock agencies (e.g. Adobe Stock).
    If it is below the target_mp, upscale it using LANCZOS filter.
    
    Args:
        image_path: Path to the image file.
        target_mp: Target Megapixels (default 6.0 MP, Adobe Stock minimum is 4.0 MP).
        quality: JPEG save quality.
        
    Returns:
        bool: True if upscaled, False if already meets the requirement.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at: {path}")

    # Read image
    img = Image.open(path)
    w, h = img.size
    current_pixels = w * h
    target_pixels = int(target_mp * 1_000_000)

    if current_pixels >= target_pixels:
        console.print(f"  [image_utils] {path.name} already meets target ({w}x{h} = {current_pixels / 1_000_000:.2f}MP)")
        # Make sure it's saved as JPEG if requested
        if path.suffix.lower() not in (".jpg", ".jpeg"):
            # Auto convert png to jpg
            _save_as_jpeg(img, path, quality)
        return False

    # Calculate scale factor
    factor = math.sqrt(target_pixels / current_pixels)
    target_w = int(w * factor)
    target_h = int(h * factor)
    
    # Ensure it's slightly above target_pixels to prevent float rounding errors
    while target_w * target_h < target_pixels:
        target_w += 1
        target_h += 1

    console.print(f"  [image_utils] Upscaling {path.name}: {w}x{h} ({current_pixels / 1_000_000:.2f}MP) -> {target_w}x{target_h} ({target_w * target_h / 1_000_000:.2f}MP)")
    
    # Resize
    img_resized = img.resize((target_w, target_h), Image.LANCZOS)
    
    # Save (replacing original or converting to jpeg)
    _save_as_jpeg(img_resized, path, quality)
    return True

def _save_as_jpeg(img: Image.Image, path: Path, quality: int):
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # If the file path is PNG, change extension to .jpg and delete the old png
    if path.suffix.lower() == ".png":
        new_path = path.with_suffix(".jpg")
        img.save(str(new_path), "JPEG", quality=quality)
        path.unlink()  # delete png
        console.print(f"  [image_utils] Converted PNG to JPEG: {new_path.name}")
    else:
        img.save(str(path), "JPEG", quality=quality)
