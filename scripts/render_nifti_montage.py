#!/usr/bin/env python3
"""Render a quick radiology-oriented orthogonal slice montage for local QC."""

from __future__ import annotations

import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def normalize_slice(data: np.ndarray) -> np.ndarray:
    finite = data[np.isfinite(data)]
    if finite.size == 0:
        return np.zeros(data.shape, dtype=np.uint8)

    low, high = np.percentile(finite, [1, 99.5])
    if high <= low:
        high = float(finite.max())
        low = float(finite.min())
    if high <= low:
        return np.zeros(data.shape, dtype=np.uint8)

    scaled = np.clip((data - low) / (high - low), 0, 1)
    return (scaled * 255).astype(np.uint8)


def pad_to_size(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("L", size, 0)
    x = (size[0] - image.width) // 2
    y = (size[1] - image.height) // 2
    canvas.paste(image, (x, y))
    return canvas


def labeled_panel(label: str, array: np.ndarray, size: tuple[int, int]) -> Image.Image:
    image = Image.fromarray(normalize_slice(array))
    image = image.resize(
        (
            max(1, int(image.width * min(size[0] / image.width, size[1] / image.height))),
            max(1, int(image.height * min(size[0] / image.width, size[1] / image.height))),
        ),
        Image.Resampling.BILINEAR,
    )
    panel = pad_to_size(image, size).convert("RGB")
    draw = ImageDraw.Draw(panel)
    font = ImageFont.load_default()
    draw.rectangle((8, 8, 8 + 8 * len(label), 26), fill=(0, 0, 0))
    draw.text((12, 12), label, fill=(255, 255, 255), font=font)
    return panel


def render_montage(input_path: Path, output_path: Path, size: int = 360) -> dict[str, object]:
    original_image = nib.load(str(input_path))
    image = nib.as_closest_canonical(original_image)
    data = np.asanyarray(image.dataobj)
    if data.ndim != 3:
        raise ValueError(f"Expected 3D image, got shape {data.shape}")

    cx, cy, cz = [dim // 2 for dim in data.shape]
    # nib.as_closest_canonical gives RAS+ voxel axes. The display below uses
    # radiology-style views: patient right on image left for axial/coronal,
    # anterior at the top for axial, and superior at the top for coronal/sagittal.
    panels = [
        labeled_panel("Sagittal", np.flipud(np.fliplr(data[cx, :, :].T)), (size, size)),
        labeled_panel("Coronal", np.flipud(np.fliplr(data[:, cy, :].T)), (size, size)),
        labeled_panel("Axial", np.flipud(np.fliplr(data[:, :, cz].T)), (size, size)),
    ]

    montage = Image.new("RGB", (size * 3, size), (10, 11, 12))
    for index, panel in enumerate(panels):
        montage.paste(panel, (index * size, 0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    montage.save(output_path)
    return {
        "shape": tuple(int(dim) for dim in data.shape),
        "zooms": tuple(float(value) for value in image.header.get_zooms()[:3]),
        "input_orientation": nib.aff2axcodes(original_image.affine),
        "display_orientation": nib.aff2axcodes(image.affine),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input NIfTI file.")
    parser.add_argument("output", type=Path, help="Output PNG montage.")
    parser.add_argument("--size", type=int, default=360, help="Panel size in pixels.")
    args = parser.parse_args()

    metadata = render_montage(args.input, args.output, args.size)
    print(f"Wrote {args.output}")
    print(f"shape={metadata['shape']}")
    print(f"zooms={metadata['zooms']}")
    print(f"input_orientation={metadata['input_orientation']}")
    print(f"display_orientation={metadata['display_orientation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
