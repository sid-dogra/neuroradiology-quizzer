#!/usr/bin/env python3
"""Build a visual QC review set for downloaded NKI Rockland T1w candidates."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

import nibabel as nib
from PIL import Image, ImageDraw, ImageFont

from render_nifti_montage import render_montage


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_ROOT = REPO_ROOT / "data/working/nki_t1_candidates"
DEFAULT_BASELINE = REPO_ROOT / "data/raw/t1_mprage.nii.gz"
DEFAULT_BASELINE_JSON = REPO_ROOT / "data/raw/t1_mprage.json"


def subject_id_from_path(path: Path) -> str:
    match = re.search(r"(sub-A\d+)", str(path))
    if match:
        return match.group(1)
    return path.stem.replace(".nii", "")


def sidecar_path_for(image_path: Path) -> Path | None:
    candidate = image_path.with_name(image_path.name.replace(".nii.gz", ".json"))
    return candidate if candidate.exists() else None


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    with path.open() as handle:
        return json.load(handle)


def compact_json_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value)


def fmt_tuple(values: tuple[int, ...] | tuple[float, ...], precision: int | None = None) -> str:
    if precision is None:
        return " x ".join(str(value) for value in values)
    return " x ".join(f"{value:.{precision}f}".rstrip("0").rstrip(".") for value in values)


def build_record(
    label: str,
    image_path: Path,
    json_path: Path | None,
    montage_path: Path,
    size: int,
) -> dict[str, str]:
    metadata = render_montage(image_path, montage_path, size=size)
    sidecar = read_json(json_path)

    original_image = nib.load(str(image_path))
    original_shape = tuple(int(dim) for dim in original_image.shape[:3])
    original_zooms = tuple(float(value) for value in original_image.header.get_zooms()[:3])

    return {
        "candidate": label,
        "image_path": str(image_path.resolve()),
        "json_path": str(json_path.resolve()) if json_path else "",
        "montage_path": str(montage_path.resolve()),
        "file_size_mb": f"{image_path.stat().st_size / (1024 * 1024):.1f}",
        "original_shape": fmt_tuple(original_shape),
        "original_voxel_mm": fmt_tuple(original_zooms, precision=4),
        "canonical_shape": fmt_tuple(metadata["shape"]),
        "canonical_voxel_mm": fmt_tuple(metadata["zooms"], precision=4),
        "input_orientation": "".join(metadata["input_orientation"]),
        "scanner": compact_json_value(sidecar.get("ManufacturersModelName") or sidecar.get("Manufacturer")),
        "field_strength": compact_json_value(sidecar.get("MagneticFieldStrength")),
        "mr_acquisition_type": compact_json_value(sidecar.get("MRAcquisitionType")),
        "sequence": compact_json_value(sidecar.get("PulseSequenceType") or sidecar.get("SequenceName")),
        "protocol": compact_json_value(sidecar.get("ProtocolName")),
        "tr": compact_json_value(sidecar.get("RepetitionTime")),
        "te": compact_json_value(sidecar.get("EchoTime")),
        "ti": compact_json_value(sidecar.get("InversionTime")),
        "flip_angle": compact_json_value(sidecar.get("FlipAngle")),
    }


def discover_images(candidate_root: Path, baseline: Path | None, baseline_json: Path | None) -> list[tuple[str, Path, Path | None]]:
    images: list[tuple[str, Path, Path | None]] = []
    if baseline and baseline.exists():
        images.append(("baseline_current_raw_t1", baseline, baseline_json if baseline_json and baseline_json.exists() else None))

    for image_path in sorted(candidate_root.glob("sub-A*/ses-BAS1/anat/*_T1w.nii.gz")):
        subject_id = subject_id_from_path(image_path)
        images.append((subject_id, image_path, sidecar_path_for(image_path)))
    return images


def write_tsv(records: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(records)


def write_markdown(records: list[dict[str, str]], output_path: Path, contact_sheet: Path, tsv_path: Path) -> None:
    lines = [
        "# NKI T1 Candidate Review",
        "",
        "Screening set for choosing a cleaner T1w base image before rerunning FreeSurfer.",
        "",
        f"- Contact sheet: `{contact_sheet.resolve()}`",
        f"- TSV summary: `{tsv_path.resolve()}`",
        "",
        "| Candidate | Size MB | Shape | Voxel mm | Orientation | Scanner | TR | TE | TI | Flip |",
        "| --- | ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for record in records:
        lines.append(
            "| {candidate} | {file_size_mb} | {original_shape} | {original_voxel_mm} | "
            "{input_orientation} | {scanner} | {tr} | {te} | {ti} | {flip_angle} |".format(**record)
        )

    lines.extend(["", "## Montages", ""])
    for record in records:
        lines.append(f"### {record['candidate']}")
        lines.append("")
        lines.append(f"![{record['candidate']}]({record['montage_path']})")
        lines.append("")

    output_path.write_text("\n".join(lines) + "\n")


def draw_contact_sheet(records: list[dict[str, str]], output_path: Path, columns: int = 2) -> None:
    font = ImageFont.load_default()
    label_height = 44
    gutter = 24
    montages = [Image.open(record["montage_path"]).convert("RGB") for record in records]
    tile_width = max(image.width for image in montages)
    tile_height = max(image.height for image in montages) + label_height
    rows = (len(records) + columns - 1) // columns
    width = columns * tile_width + (columns + 1) * gutter
    height = rows * tile_height + (rows + 1) * gutter
    sheet = Image.new("RGB", (width, height), (248, 248, 248))
    draw = ImageDraw.Draw(sheet)

    for index, (record, montage) in enumerate(zip(records, montages)):
        row = index // columns
        col = index % columns
        x = gutter + col * (tile_width + gutter)
        y = gutter + row * (tile_height + gutter)
        draw.rectangle((x, y, x + tile_width, y + label_height), fill=(32, 34, 36))
        label = (
            f"{record['candidate']} | {record['original_shape']} | "
            f"{record['original_voxel_mm']} mm | {record['file_size_mb']} MB"
        )
        draw.text((x + 12, y + 14), label, fill=(255, 255, 255), font=font)
        sheet.paste(montage, (x, y + label_height))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--baseline-json", type=Path, default=DEFAULT_BASELINE_JSON)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_CANDIDATE_ROOT / "review")
    parser.add_argument("--size", type=int, default=360, help="Panel size passed to the montage renderer.")
    args = parser.parse_args()

    images = discover_images(args.candidate_root, args.baseline, args.baseline_json)
    if not images:
        raise SystemExit(f"No T1w images found under {args.candidate_root}")

    montage_root = args.output_root / "montages"
    records = []
    for label, image_path, json_path in images:
        montage_path = montage_root / f"{label}_montage.png"
        records.append(build_record(label, image_path, json_path, montage_path, args.size))

    tsv_path = args.output_root / "nki_t1_candidate_summary.tsv"
    markdown_path = args.output_root / "nki_t1_candidate_review.md"
    contact_sheet = args.output_root / "nki_t1_candidate_contact_sheet.png"
    write_tsv(records, tsv_path)
    draw_contact_sheet(records, contact_sheet)
    write_markdown(records, markdown_path, contact_sheet, tsv_path)

    print(f"Wrote {len(records)} candidate records")
    print(f"Contact sheet: {contact_sheet}")
    print(f"Review markdown: {markdown_path}")
    print(f"TSV summary: {tsv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
