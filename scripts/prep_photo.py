#!/usr/bin/env python3
"""Prep a photo for ASCII conversion.

Pipeline: cut the background (rembg, optional) -> boost local contrast
(CLAHE via OpenCV, with a pure-PIL fallback) -> composite onto pure white
so the background maps to the blank end of the density ramp.

Usage:
    python scripts/prep_photo.py [path/to/photo.jpg]

Output: data/source-prepped.png (grayscale)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "source-prepped.png"
DEFAULT_INPUT = ROOT / "data" / "source-photo.jpg"


def remove_background(img: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError:
        print("rembg not installed - keeping original background")
        return img
    print("removing background with rembg ...")
    return remove(img)


def clahe(plane: Image.Image) -> Image.Image:
    try:
        import cv2
    except ImportError:
        boosted = ImageOps.autocontrast(plane, cutoff=1)
        return Image.blend(plane, ImageOps.equalize(boosted), 0.6)
    arr = np.asarray(plane)
    out = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(arr)
    return Image.fromarray(out, mode="L")


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    if not src.exists():
        sys.exit(f"input photo not found: {src}\nplace your photo at {DEFAULT_INPUT}")

    img = Image.open(src).convert("RGB")
    img.thumbnail((1024, 1024), Image.LANCZOS)

    img = remove_background(img)
    gray = clahe(img.convert("L"))

    if img.mode == "RGBA":
        alpha = np.asarray(img.getchannel("A"), dtype=np.float32) / 255.0
        base = np.asarray(gray, dtype=np.float32)
        white = 255.0 * (1.0 - alpha)
        gray = Image.fromarray((base * alpha + white).astype(np.uint8), mode="L")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    gray.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
