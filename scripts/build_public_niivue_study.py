#!/usr/bin/env python3
"""Build the static NiiVue study bundle served by GitHub Pages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np
from scipy import ndimage


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FINALIZED_DIR = REPO_ROOT / "data" / "finalized"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "public" / "studies" / "nki_a00039636_t1"
DEFAULT_STRUCTURE_JSON = (
    DEFAULT_FINALIZED_DIR / "curation" / "target-structures.json"
)
# The public bundle is built from the finalized review area, not data/working.
DEFAULT_DISPLAY_IMAGE = (
    REPO_ROOT
    / "data"
    / "processed"
    / "freesurfer_subjects"
    / "annotated_t1_nki_A00039636"
    / "mri"
    / "orig.mgz"
)
AXIAL_FOREGROUND_THRESHOLD = 20
AXIAL_FOREGROUND_MIN_VOXELS = 100
EDITED_MASK_MIN_ISLAND_VOXELS = 12
EDITED_MASK_SMOOTH_SIGMA = 0.75
EDITED_MASK_SMOOTH_THRESHOLD = 0.5
EDITED_MASK_CLOSE_ITERATIONS = 1


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def slug(value: str) -> str:
    output = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    output = re.sub(r"_+", "_", output)
    return output.strip("_")


def nifti_stem(path: Path) -> str:
    name = path.name
    if name.endswith(".nii.gz"):
        return name[:-7]
    return path.stem


def normalize_mask_key(value: str) -> str:
    value = nifti_stem(Path(value))
    value = re.sub(r"^\d+_", "", value)
    value = re.sub(r"([._-]edited|[._-]accepted)$", "", value, flags=re.IGNORECASE)
    return slug(value)


def relative_path(path: Path, base: Path) -> str:
    return path.resolve().relative_to(base.resolve()).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def color_hex(row: dict[str, str]) -> str:
    red = int(row.get("red") or 242)
    green = int(row.get("green") or 89)
    blue = int(row.get("blue") or 78)
    return f"#{red:02x}{green:02x}{blue:02x}"


def clean_output(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    (path / "annotations").mkdir(parents=True, exist_ok=True)


def make_binary_nifti(
    reference: nib.spatialimages.SpatialImage,
    mask: np.ndarray,
) -> nib.Nifti1Image:
    image = nib.Nifti1Image(mask.astype(np.uint8), reference.affine, reference.header)
    image.header.set_data_dtype(np.uint8)
    image.header["cal_min"] = 0
    image.header["cal_max"] = 1
    return image


def crop_affine(
    affine: np.ndarray,
    crop_slices: tuple[slice, slice, slice],
) -> np.ndarray:
    starts = np.array([axis_slice.start or 0 for axis_slice in crop_slices], dtype=float)
    output = np.array(affine, copy=True)
    output[:3, 3] = affine[:3, :3] @ starts + affine[:3, 3]
    return output


def cropped_image(
    image: nib.spatialimages.SpatialImage,
    crop_slices: tuple[slice, slice, slice],
) -> nib.Nifti1Image:
    data = np.asarray(image.dataobj)
    cropped = data[crop_slices]
    output = nib.Nifti1Image(cropped, crop_affine(image.affine, crop_slices))
    output.header.set_zooms(image.header.get_zooms()[:3])
    output.header.set_data_dtype(image.get_data_dtype())
    return output


def display_crop_slices(
    image: nib.spatialimages.SpatialImage,
) -> tuple[tuple[slice, slice, slice], dict[str, Any]]:
    data = np.asarray(image.dataobj)
    if data.ndim != 3:
        raise ValueError(f"Expected 3D display image, got shape {data.shape}")

    foreground = data > AXIAL_FOREGROUND_THRESHOLD
    axial_counts = foreground.sum(axis=(0, 1))
    useful_slices = np.where(axial_counts >= AXIAL_FOREGROUND_MIN_VOXELS)[0]
    if useful_slices.size == 0:
        crop_slices = (slice(None), slice(None), slice(None))
        start = 0
        stop = data.shape[2]
    else:
        start = int(useful_slices[0])
        stop = int(useful_slices[-1]) + 1
        crop_slices = (slice(None), slice(None), slice(start, stop))

    info = {
        "coordinateSpace": "canonical_RAS_voxel",
        "axis": "axial",
        "startInclusive": start,
        "stopExclusive": stop,
        "removedBefore": start,
        "removedAfter": int(data.shape[2] - stop),
        "foregroundThreshold": AXIAL_FOREGROUND_THRESHOLD,
        "minimumForegroundVoxels": AXIAL_FOREGROUND_MIN_VOXELS,
        "originalShape": [int(value) for value in data.shape],
    }
    return crop_slices, info


def save_display_image(
    source: Path,
    destination: Path,
) -> tuple[dict[str, Any], tuple[slice, slice, slice], dict[str, Any]]:
    image = nib.as_closest_canonical(nib.load(str(source)))
    data = np.asarray(image.dataobj)
    if data.ndim != 3:
        raise ValueError(f"Expected 3D display image, got shape {data.shape} from {source}")

    crop_slices, crop_info = display_crop_slices(image)
    output = cropped_image(image, crop_slices)
    destination.parent.mkdir(parents=True, exist_ok=True)
    nib.save(output, str(destination))
    output_data = np.asarray(output.dataobj)
    return {
        "bytes": destination.stat().st_size,
        "sha256": sha256(destination),
        "shape": [int(value) for value in output_data.shape],
        "voxelSizeMm": [float(value) for value in output.header.get_zooms()[:3]],
        "orientation": "".join(nib.aff2axcodes(output.affine)),
        "crop": crop_info,
    }, crop_slices, crop_info


def best_slices(mask: np.ndarray) -> dict[str, Any]:
    coords = np.argwhere(mask)
    if coords.size == 0:
        return {
            "coordinateSpace": "viewer_ras_voxel",
            "shape": [int(value) for value in mask.shape],
            "centroidVoxel": None,
            "axial": None,
            "coronal": None,
            "sagittal": None,
        }

    centroid = np.rint(coords.mean(axis=0)).astype(int)
    views = {
        "sagittal": 0,
        "coronal": 1,
        "axial": 2,
    }
    output: dict[str, Any] = {
        "coordinateSpace": "viewer_ras_voxel",
        "shape": [int(value) for value in mask.shape],
        "centroidVoxel": {
            "i": int(centroid[0]),
            "j": int(centroid[1]),
            "k": int(centroid[2]),
        },
    }

    for view, axis in views.items():
        reduce_axes = tuple(index for index in range(mask.ndim) if index != axis)
        slice_counts = mask.sum(axis=reduce_axes)
        best_index = int(np.argmax(slice_counts))
        voxel_count = int(slice_counts[best_index])
        if voxel_count == 0:
            output[view] = None
            continue
        slice_coords = coords[coords[:, axis] == best_index]
        center = np.rint(slice_coords.mean(axis=0)).astype(int)
        output[view] = {
            "axis": axis,
            "sliceIndex": best_index,
            "areaVoxelCount": voxel_count,
            "voxel": {
                "i": int(center[0]),
                "j": int(center[1]),
                "k": int(center[2]),
            },
        }

    return output


def mask_stats(path: Path) -> dict[str, Any]:
    image = nib.load(str(path))
    canonical = nib.as_closest_canonical(image)
    mask = np.asarray(canonical.dataobj) != 0
    return {
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "voxelCount": int(np.count_nonzero(mask)),
        "bestSlices": best_slices(mask),
    }


def edited_mask_cleanup(mask: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    original = mask.astype(bool)
    if not np.any(original):
        return original, {
            "enabled": True,
            "minIslandVoxels": EDITED_MASK_MIN_ISLAND_VOXELS,
            "smoothSigma": EDITED_MASK_SMOOTH_SIGMA,
            "smoothThreshold": EDITED_MASK_SMOOTH_THRESHOLD,
            "closeIterations": EDITED_MASK_CLOSE_ITERATIONS,
            "removedIslandCount": 0,
            "removedIslandVoxelCount": 0,
            "removedVoxelCount": 0,
            "addedVoxelCount": 0,
            "filledVoxelCount": 0,
            "netVoxelChange": 0,
        }

    connectivity = ndimage.generate_binary_structure(rank=3, connectivity=1)
    labels, component_count = ndimage.label(original, structure=connectivity)
    component_sizes = np.bincount(labels.ravel())
    keep_labels = np.where(component_sizes >= EDITED_MASK_MIN_ISLAND_VOXELS)[0]
    keep_labels = keep_labels[keep_labels != 0]
    cleaned = np.isin(labels, keep_labels)
    smoothed = (
        ndimage.gaussian_filter(cleaned.astype(np.float32), sigma=EDITED_MASK_SMOOTH_SIGMA)
        >= EDITED_MASK_SMOOTH_THRESHOLD
    )

    if EDITED_MASK_CLOSE_ITERATIONS:
        closed = ndimage.binary_closing(
            smoothed,
            structure=connectivity,
            iterations=EDITED_MASK_CLOSE_ITERATIONS,
        )
        smoothed = np.logical_or(smoothed, closed)

    filled = ndimage.binary_fill_holes(smoothed, structure=connectivity)
    cleaned = filled.astype(bool)

    removed_components = [
        int(label)
        for label in range(1, component_count + 1)
        if component_sizes[label] < EDITED_MASK_MIN_ISLAND_VOXELS
    ]

    return cleaned, {
        "enabled": True,
        "minIslandVoxels": EDITED_MASK_MIN_ISLAND_VOXELS,
        "smoothSigma": EDITED_MASK_SMOOTH_SIGMA,
        "smoothThreshold": EDITED_MASK_SMOOTH_THRESHOLD,
        "closeIterations": EDITED_MASK_CLOSE_ITERATIONS,
        "removedIslandCount": len(removed_components),
        "removedIslandVoxelCount": int(
            sum(component_sizes[label] for label in removed_components)
        ),
        "removedVoxelCount": int(np.count_nonzero(original & ~cleaned)),
        "addedVoxelCount": int(np.count_nonzero(cleaned & ~original)),
        "filledVoxelCount": int(np.count_nonzero(filled & ~original)),
        "netVoxelChange": int(np.count_nonzero(cleaned) - np.count_nonzero(original)),
    }


def build_mask_index(paths: list[Path]) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for directory in paths:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.nii*")):
            if path.name.endswith((".nii", ".nii.gz")):
                key = normalize_mask_key(path.name)
                index.setdefault(key, path)
    return index


def choose_existing_mask(
    target_id: str,
    label_value: int,
    display_name: str,
    accepted_index: dict[str, Path],
    full_gyrus_index: dict[str, Path],
    rough_index: dict[str, Path],
) -> tuple[str, Path] | None:
    candidates = [
        target_id,
        slug(display_name),
        f"{label_value:03d}_{target_id}",
        f"{label_value:03d}_{slug(display_name)}",
    ]

    for source_kind, index in (
        ("accepted_annotation", accepted_index),
        ("full_gyrus_composite", full_gyrus_index),
        ("rough_support", rough_index),
    ):
        for candidate in candidates:
            path = index.get(normalize_mask_key(candidate))
            if path:
                return source_kind, path
    return None


def crop_mask_to_reference(
    source: Path,
    reference: nib.spatialimages.SpatialImage,
    crop_slices: tuple[slice, slice, slice],
) -> np.ndarray:
    image = nib.as_closest_canonical(nib.load(str(source)))
    data = np.asarray(image.dataobj) != 0
    if data.shape == reference.shape:
        return data

    cropped = data[crop_slices]
    if cropped.shape != reference.shape:
        raise ValueError(
            f"Mask shape {data.shape} from {source} does not match reference "
            f"shape {reference.shape} after crop {cropped.shape}"
        )
    return cropped


def copy_mask(
    source: Path,
    destination: Path,
    reference: nib.spatialimages.SpatialImage,
    crop_slices: tuple[slice, slice, slice],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    mask = crop_mask_to_reference(source, reference, crop_slices)
    cleanup: dict[str, Any] | None = None
    if source.name.endswith(".edited.nii.gz") or source.name.endswith(".edited.nii"):
        mask, cleanup = edited_mask_cleanup(mask)
    nib.save(make_binary_nifti(reference, mask), str(destination))
    return mask_stats(destination), cleanup


def split_label_mask(
    segmentation_data: np.ndarray,
    reference: nib.spatialimages.SpatialImage,
    label_value: int,
    destination: Path,
    crop_slices: tuple[slice, slice, slice],
) -> dict[str, Any] | None:
    mask = (segmentation_data == label_value)[crop_slices]
    if not np.any(mask):
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    nib.save(make_binary_nifti(reference, mask), str(destination))
    return mask_stats(destination)


def target_by_id(targets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {target["id"]: target for target in targets}


def labels_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["id"]: row for row in rows}


def points_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["id"]: row for row in rows}


def viewer_difficulty(source_difficulty: str) -> str:
    return "beginner" if source_difficulty == "beginner" else "advanced"


def structure_entry(
    target: dict[str, Any],
    label_row: dict[str, str],
    point_row: dict[str, str] | None,
    overlay: dict[str, Any] | None,
) -> dict[str, Any]:
    source_difficulty = target.get("difficulty", label_row.get("difficulty", "advanced"))
    entry = {
        "id": target["id"],
        "displayName": target.get("preferredName") or label_row["preferredName"],
        "targetName": target.get("targetName") or label_row.get("targetName"),
        "laterality": target.get("laterality", "unspecified"),
        "difficulty": source_difficulty,
        "audienceLevel": viewer_difficulty(source_difficulty),
        "systems": target.get("systems", []),
        "description": target.get("description", ""),
        "relationships": target.get("relationships", {}),
        "clinicalNotes": target.get("clinicalNotes", []),
        "acceptedAnswers": target.get("acceptedAnswers", []),
        "aliases": target.get("aliases", []),
        "references": target.get("references", []),
        "quizQuestions": target.get("quizQuestions", []),
        "includeInViewer": target.get("includeInViewer", True),
        "sourceLabels": target.get("sourceLabels", []),
        "sourceStrategy": label_row.get("sourceStrategy", ""),
        "userAction": label_row.get("userAction", ""),
        "localizationStatus": label_row.get("localizationStatus", ""),
        "labelValue": int(label_row["labelValue"]),
        "color": color_hex(label_row),
        "hasOverlay": overlay is not None,
        "overlay": overlay,
        "quizTargets": target.get("quizTargets", []),
    }

    if point_row and point_row.get("notes"):
        entry["reviewNote"] = point_row["notes"]

    return entry


def write_readme(path: Path, structure_count: int, overlay_count: int) -> None:
    text = f"""# NKI A00039636 T1 Static NiiVue Study

Generated by `scripts/build_public_niivue_study.py`.

This bundle is intended for GitHub Pages review of the Neuroradiology Quizzer project.
It contains the FreeSurfer-conformed T1 image and per-structure NIfTI overlays in the
same 1 mm conformed coordinate space. The display image is exported from
FreeSurfer `orig.mgz` for more raw-MPRAGE-like contrast while preserving overlay
alignment. The public NIfTI files are cropped in the axial direction to remove
blank padding while keeping overlay and display-image grids identical.

- Structures in manifest: {structure_count}
- Structures with overlays: {overlay_count}

The current overlays are a generated review set unless `overlay.sourceKind` is
`accepted_annotation`. They still need visual QC before being treated as final
educational annotations.
"""
    path.write_text(text, encoding="utf-8")


def build_public_study(
    finalized_dir: Path,
    output_dir: Path,
    structure_json: Path,
    display_image: Path,
) -> dict[str, Any]:
    generated_dir = finalized_dir / "generated_review"
    processing_t1 = finalized_dir / "source" / "t1_conformed_freesurfer.nii.gz"
    label_table = generated_dir / "labels.tsv"
    point_table = generated_dir / "points.tsv"
    segmentation_path = generated_dir / "candidate_auto_seed_segmentation.nii.gz"

    clean_output(output_dir)

    t1_destination = output_dir / "t1_display_freesurfer_orig.nii.gz"
    display_stats, crop_slices, crop_info = save_display_image(display_image, t1_destination)

    target_data = load_json(structure_json)
    labels = labels_by_id(load_tsv(label_table))
    points = points_by_id(load_tsv(point_table))
    targets = target_by_id(target_data["structures"])

    accepted_index = build_mask_index([finalized_dir / "accepted_annotations"])
    full_gyrus_index = build_mask_index([generated_dir / "full_gyrus_masks"])
    rough_index = build_mask_index([generated_dir / "rough_support_masks"])

    reference = nib.load(str(t1_destination))
    segmentation = nib.as_closest_canonical(nib.load(str(segmentation_path)))
    segmentation_data = np.asarray(segmentation.dataobj)

    structures: list[dict[str, Any]] = []
    overlay_count = 0

    for target_id, label_row in labels.items():
        target = targets.get(target_id)
        if not target:
            continue
        if target.get("includeInViewer") is False:
            continue

        label_value = int(label_row["labelValue"])
        display_name = target.get("preferredName") or label_row["preferredName"]
        mask_name = f"{label_value:03d}_{slug(display_name)}.nii.gz"
        mask_destination = output_dir / "annotations" / mask_name

        overlay: dict[str, Any] | None = None
        chosen = choose_existing_mask(
            target_id,
            label_value,
            display_name,
            accepted_index,
            full_gyrus_index,
            rough_index,
        )

        if chosen:
            source_kind, source_mask = chosen
            stats, cleanup = copy_mask(
                source_mask,
                mask_destination,
                reference,
                crop_slices,
            )
            overlay = {
                "url": relative_path(mask_destination, output_dir),
                "sourceKind": source_kind,
                "reviewStatus": (
                    "accepted" if source_kind == "accepted_annotation" else "needs_review"
                ),
                **stats,
            }
            if cleanup:
                overlay["maskCleanup"] = cleanup
        else:
            stats = split_label_mask(
                segmentation_data,
                reference,
                label_value,
                mask_destination,
                crop_slices,
            )
            if stats:
                overlay = {
                    "url": relative_path(mask_destination, output_dir),
                    "sourceKind": "freesurfer_seed_split",
                    "reviewStatus": "needs_review",
                    **stats,
                }

        if not overlay:
            continue

        overlay_count += 1
        structures.append(structure_entry(target, label_row, points.get(target_id), overlay))

    manifest = {
        "version": "0.1.0",
        "kind": "niivue_static_study",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "study": {
            **target_data.get("study", {}),
            "id": "nki_a00039636_t1",
            "title": "Neuroradiology Quizzer Review Build",
            "sourceDataset": "NKI Rockland Sample",
            "sourceSubject": "sub-A00039636 / ses-BAS1",
        },
        "image": {
            "url": relative_path(t1_destination, output_dir),
            "name": "T1 MPRAGE, FreeSurfer conformed orig",
            "space": "FreeSurfer conformed orig.mgz space; same grid as overlays",
            "shape": display_stats["shape"],
            "voxelSizeMm": display_stats["voxelSizeMm"],
            "orientation": display_stats["orientation"],
            "bytes": display_stats["bytes"],
            "sha256": display_stats["sha256"],
            "crop": crop_info,
        },
        "audienceLevels": [
            {
                "id": "beginner",
                "label": "Beginner",
                "description": "High-yield first- and second-year resident anatomy.",
            },
            {
                "id": "advanced",
                "label": "Advanced",
                "description": "Intermediate and advanced targets for the full teaching set.",
            },
        ],
        "structures": structures,
        "summary": {
            "structureCount": len(structures),
            "overlayCount": overlay_count,
            "missingOverlayCount": 0,
            "targetStructureCount": len(
                [
                    target
                    for target in target_data["structures"]
                    if target.get("includeInViewer") is not False
                ]
            ),
            "acceptedOverlayCount": sum(
                1
                for structure in structures
                if (structure.get("overlay") or {}).get("sourceKind")
                == "accepted_annotation"
            ),
        },
        "sourceFiles": {
            "finalizedDir": relative_path(finalized_dir, REPO_ROOT),
            "structureJson": relative_path(structure_json, REPO_ROOT),
            "labels": relative_path(label_table, REPO_ROOT),
            "points": relative_path(point_table, REPO_ROOT),
            "displayImage": relative_path(display_image, REPO_ROOT),
            "processingImage": relative_path(processing_t1, REPO_ROOT),
        },
    }

    write_json(output_dir / "study.json", manifest)
    write_readme(output_dir / "README.md", len(structures), overlay_count)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finalized-dir", type=Path, default=DEFAULT_FINALIZED_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--structure-json", type=Path, default=DEFAULT_STRUCTURE_JSON)
    parser.add_argument("--display-image", type=Path, default=DEFAULT_DISPLAY_IMAGE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_public_study(
        finalized_dir=args.finalized_dir.resolve(),
        output_dir=args.output_dir.resolve(),
        structure_json=args.structure_json.resolve(),
        display_image=args.display_image.resolve(),
    )
    summary = manifest["summary"]
    print(
        "Built public NiiVue study: "
        f"{summary['overlayCount']}/{summary['structureCount']} structures have overlays "
        f"at {relative_path(args.output_dir.resolve(), REPO_ROOT)}"
    )


if __name__ == "__main__":
    main()
