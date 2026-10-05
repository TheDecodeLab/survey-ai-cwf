#!/usr/bin/env python3
"""Shared export utilities for manuscript figures.

Each figure is written as:
- FigureN.png: local/manuscript preview
- FigN.tif: PLOS submission file

TIFF export follows the current PLOS ONE technical specifications used for this
revision: RGB, flattened, LZW-compressed, 300 dpi, <=2250 px wide, <=2625 px
high, and <=10 MB.
"""
from pathlib import Path

from PIL import Image


PLOS_DPI = 300
PLOS_MIN_WIDTH_PX = 789
PLOS_MAX_WIDTH_PX = 2250
PLOS_MAX_HEIGHT_PX = 2625
PLOS_MAX_FILE_BYTES = 10 * 1024 * 1024


def _flatten_to_rgb(image):
    """Flatten transparency against white and return an RGB image."""
    if image.mode == "RGBA":
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        return background

    if image.mode == "LA":
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background

    if image.mode == "P" and "transparency" in image.info:
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background

    return image.convert("RGB")


def _fit_plos_dimensions(size):
    """Scale down proportionally only when PLOS maximum dimensions are exceeded."""
    width, height = size
    scale = min(
        1.0,
        PLOS_MAX_WIDTH_PX / width,
        PLOS_MAX_HEIGHT_PX / height,
    )
    if scale >= 1.0:
        return width, height
    return (
        max(1, int(round(width * scale))),
        max(1, int(round(height * scale))),
    )


def _validate_plos_tiff(path):
    """Fail fast if a generated TIFF violates the technical export constraints."""
    path = Path(path)
    with Image.open(path) as image:
        width, height = image.size
        dpi = image.info.get("dpi", (0, 0))
        compression = image.info.get("compression")

        if image.mode != "RGB":
            raise RuntimeError(f"{path}: expected RGB TIFF, found {image.mode}")
        if width < PLOS_MIN_WIDTH_PX:
            raise RuntimeError(
                f"{path}: width {width}px is below PLOS minimum {PLOS_MIN_WIDTH_PX}px"
            )
        if width > PLOS_MAX_WIDTH_PX or height > PLOS_MAX_HEIGHT_PX:
            raise RuntimeError(
                f"{path}: dimensions {width}x{height}px exceed PLOS limits "
                f"{PLOS_MAX_WIDTH_PX}x{PLOS_MAX_HEIGHT_PX}px"
            )
        if min(dpi) < 299:
            raise RuntimeError(f"{path}: expected 300 dpi, found {dpi}")
        if compression != "tiff_lzw":
            raise RuntimeError(
                f"{path}: expected LZW compression, found {compression!r}"
            )

    if path.stat().st_size > PLOS_MAX_FILE_BYTES:
        raise RuntimeError(
            f"{path}: file size exceeds the PLOS 10 MB limit"
        )


def png_to_plos_tiff(png_path, tiff_path):
    """Convert a generated PNG to a PLOS-ready TIFF without changing content."""
    png_path = Path(png_path)
    tiff_path = Path(tiff_path)

    with Image.open(png_path) as image:
        image.load()
        rgb = _flatten_to_rgb(image)
        target_size = _fit_plos_dimensions(rgb.size)
        if target_size != rgb.size:
            rgb = rgb.resize(target_size, Image.Resampling.LANCZOS)
        rgb.save(
            tiff_path,
            format="TIFF",
            compression="tiff_lzw",
            dpi=(PLOS_DPI, PLOS_DPI),
        )

    _validate_plos_tiff(tiff_path)


def export_figure(
    fig,
    png_path,
    figure_number,
    *,
    transparent_png=False,
    bbox_inches="tight",
    pad_inches=0.08,
):
    """Write the preview PNG and the PLOS TIFF for one Matplotlib figure."""
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        png_path,
        dpi=PLOS_DPI,
        bbox_inches=bbox_inches,
        pad_inches=pad_inches,
        transparent=transparent_png,
    )

    tiff_path = png_path.with_name(f"Fig{figure_number}.tif")
    png_to_plos_tiff(png_path, tiff_path)
    return png_path, tiff_path
