#!/usr/bin/env python3
"""Export an editable ITK-SNAP working set for the current T1 target queue."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = REPO_ROOT / "annotations" / "localization" / "t1-localization-queue.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "working" / "itksnap"
DEFAULT_MANIFEST = REPO_ROOT / "annotations" / "localization" / "itksnap-export-manifest.json"
DEFAULT_REVIEW = REPO_ROOT / "annotations" / "localization" / "itksnap-export-review.md"

FULL_GYRUS_COMPONENTS = {
    "cuneus": {"aparc": ["cuneus"]},
    "entorhinal_cortex": {"aparc": ["entorhinal"]},
    "fusiform_gyrus": {"aparc": ["fusiform"]},
    "lingual_gyrus": {"aparc": ["lingual"]},
    "pars_opercularis": {"aparc": ["parsopercularis"]},
    "pars_orbitalis": {"aparc": ["parsorbitalis"]},
    "pars_triangularis": {"aparc": ["parstriangularis"]},
    "postcentral_gyrus": {"aparc": ["postcentral"]},
    "posterior_cingulate_gyrus": {"aparc": ["posteriorcingulate"]},
    "precentral_gyrus": {"aparc": ["precentral"]},
    "precuneus": {"aparc": ["precuneus"]},
    "superior_frontal_gyrus": {"aparc": ["superiorfrontal"]},
    "supramarginal_gyrus": {"aparc": ["supramarginal"]},
    "temporal_pole": {"aparc": ["temporalpole"]},
    "insular_cortex": {"aparc": ["insula"]},
    "gyrus_rectus": {"aparc_a2009s": ["G_rectus"]},
    "cingulate_gyrus": {
        "aparc": [
            "caudalanteriorcingulate",
            "rostralanteriorcingulate",
            "posteriorcingulate",
            "isthmuscingulate",
        ]
    },
    "angular_gyrus": {"aparc_a2009s": ["G_pariet_inf-Angular"]},
    "superior_temporal_gyrus": {"aparc": ["superiortemporal"]},
    "middle_temporal_gyrus": {"aparc": ["middletemporal"]},
    "inferior_temporal_gyrus": {"aparc": ["inferiortemporal"]},
    "parahippocampal_gyrus": {"aparc": ["parahippocampal"]},
    "orbitofrontal_cortex": {"aparc": ["lateralorbitofrontal", "medialorbitofrontal"]},
}

WM_COMPATIBLE_ATLASES = {"aparc", "aparc_dkt"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def relative_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def slug(value: str) -> str:
    output = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in output:
        output = output.replace("__", "_")
    return output.strip("_")


def color_for_id(identifier: str) -> tuple[int, int, int]:
    digest = hashlib.md5(identifier.encode("utf-8")).hexdigest()
    hue = int(digest[:6], 16) / 0xFFFFFF
    saturation = 0.68
    value = 0.95
    i = int(hue * 6)
    f = hue * 6 - i
    p = value * (1 - saturation)
    q = value * (1 - f * saturation)
    t = value * (1 - (1 - f) * saturation)
    i %= 6
    if i == 0:
        rgb = (value, t, p)
    elif i == 1:
        rgb = (q, value, p)
    elif i == 2:
        rgb = (p, value, t)
    elif i == 3:
        rgb = (p, q, value)
    elif i == 4:
        rgb = (t, p, value)
    else:
        rgb = (value, p, q)
    return tuple(int(round(component * 255)) for component in rgb)


def make_label_table(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for value, target in enumerate(targets, start=1):
        color = color_for_id(target["id"])
        rows.append(
            {
                "labelValue": value,
                "id": target["id"],
                "preferredName": target["preferredName"],
                "targetName": target["targetName"],
                "userAction": target["userAction"],
                "localizationStatus": target["localizationStatus"],
                "sourceStrategy": target["sourceStrategy"],
                "difficulty": target["difficulty"],
                "systems": ";".join(target.get("systems", [])),
                "red": color[0],
                "green": color[1],
                "blue": color[2],
            }
        )
    return rows


def save_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_itksnap_label_description(path: Path, label_rows: list[dict[str, Any]]) -> None:
    lines = [
        "################################################",
        "# ITK-SNAP Label Description File",
        "# File format:",
        "# IDX   -R-  -G-  -B-  -A--  VIS MSH  LABEL",
        "################################################",
        '    0     0    0    0        0  0  0    "Clear Label"',
    ]
    for row in label_rows:
        lines.append(
            f"{row['labelValue']:5d}"
            f"{row['red']:6d}{row['green']:5d}{row['blue']:5d}"
            f"        1  1  1    \"{row['preferredName']}\""
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class VolumeCache:
    def __init__(self) -> None:
        self._cache: dict[Path, tuple[nib.spatialimages.SpatialImage, np.ndarray]] = {}

    def load(self, path: Path) -> tuple[nib.spatialimages.SpatialImage, np.ndarray]:
        resolved = path.resolve()
        if resolved not in self._cache:
            image = nib.load(str(resolved))
            self._cache[resolved] = (image, np.asarray(image.dataobj))
        return self._cache[resolved]


def masks_for_target(target: dict[str, Any], cache: VolumeCache) -> list[np.ndarray]:
    masks = []
    for point in target.get("sourcePoints", []):
        volume = point.get("sourceVolume")
        value = point.get("labelValue")
        if volume and value is not None:
            _, data = cache.load(REPO_ROOT / volume)
            masks.append(data == int(value))
    return masks


def combined_mask(target: dict[str, Any], cache: VolumeCache, shape: tuple[int, ...]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    for source_mask in masks_for_target(target, cache):
        mask |= source_mask
    return mask


def make_nifti_like(reference: nib.spatialimages.SpatialImage, data: np.ndarray) -> nib.Nifti1Image:
    image = nib.Nifti1Image(data, reference.affine)
    image.header.set_zooms(reference.header.get_zooms()[:3])
    return image


def clean_generated_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def source_points_by_atlas(target: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    points_by_atlas: dict[str, list[dict[str, Any]]] = {}
    for point in target.get("sourcePoints", []):
        points_by_atlas.setdefault(point.get("sourceAtlas", ""), []).append(point)
    return points_by_atlas


def wmparc_path_for(source_volume: str) -> Path:
    return REPO_ROOT / source_volume.replace("/aparc+aseg.mgz", "/wmparc.mgz").replace(
        "/aparc.DKTatlas+aseg.mgz", "/wmparc.mgz"
    )


def full_gyrus_mask(
    target: dict[str, Any],
    cache: VolumeCache,
    shape: tuple[int, ...],
) -> tuple[np.ndarray, dict[str, Any]] | None:
    rules = FULL_GYRUS_COMPONENTS.get(target["id"])
    if not rules:
        return None

    points_by_atlas = source_points_by_atlas(target)
    mask = np.zeros(shape, dtype=bool)
    components = []
    missing = []
    white_matter_components = 0

    for atlas_id, source_labels in rules.items():
        available_points = points_by_atlas.get(atlas_id, [])
        for source_label in source_labels:
            point = next(
                (
                    item
                    for item in available_points
                    if item.get("sourceLabel") == source_label and item.get("labelValue") is not None
                ),
                None,
            )
            if not point:
                missing.append({"atlas": atlas_id, "sourceLabel": source_label})
                continue

            source_volume = point["sourceVolume"]
            label_value = int(point["labelValue"])
            _, data = cache.load(REPO_ROOT / source_volume)
            cortex_mask = data == label_value
            mask |= cortex_mask
            component = {
                "atlas": atlas_id,
                "sourceLabel": source_label,
                "labelValue": label_value,
                "sourceVolume": source_volume,
                "voxelCount": int(cortex_mask.sum()),
            }

            if atlas_id in WM_COMPATIBLE_ATLASES:
                wm_path = wmparc_path_for(source_volume)
                if wm_path.exists():
                    _, wm_data = cache.load(wm_path)
                    wm_value = label_value + 2000
                    wm_mask = wm_data == wm_value
                    if wm_mask.any():
                        mask |= wm_mask
                        white_matter_components += 1
                        component["whiteMatter"] = {
                            "atlas": "wmparc",
                            "labelValue": wm_value,
                            "sourceVolume": relative_path(wm_path),
                            "voxelCount": int(wm_mask.sum()),
                        }
                    else:
                        component["whiteMatterMissing"] = {
                            "atlas": "wmparc",
                            "labelValue": wm_value,
                            "sourceVolume": relative_path(wm_path),
                        }
                else:
                    component["whiteMatterMissing"] = {
                        "atlas": "wmparc",
                        "sourceVolume": relative_path(wm_path),
                    }
            components.append(component)

    if not mask.any():
        return None

    return mask, {
        "id": target["id"],
        "preferredName": target["preferredName"],
        "components": components,
        "missingComponents": missing,
        "includesWhiteMatter": white_matter_components > 0,
        "whiteMatterComponentCount": white_matter_components,
        "voxelCount": int(mask.sum()),
    }


def point_rows(targets: list[dict[str, Any]], label_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        point = target.get("chosenPoint")
        label = label_by_id[target["id"]]
        voxel = point.get("voxel", {}) if point else {}
        world = point.get("worldMm", {}) if point else {}
        rows.append(
            {
                "labelValue": label["labelValue"],
                "id": target["id"],
                "preferredName": target["preferredName"],
                "userAction": target["userAction"],
                "sourceStrategy": target["sourceStrategy"],
                "voxel_i": voxel.get("i", ""),
                "voxel_j": voxel.get("j", ""),
                "voxel_k": voxel.get("k", ""),
                "world_x": world.get("x", ""),
                "world_y": world.get("y", ""),
                "world_z": world.get("z", ""),
                "notes": " ".join(target.get("notes", [])),
            }
        )
    return rows


def write_review(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# ITK-SNAP Export Review",
        "",
        "Open the conformed T1 as the main image, then open the auto labelmap as the segmentation.",
        "",
        "## Files",
        "",
        f"- Main image: `{manifest['files']['mainImage']}`",
        f"- Auto segmentation labelmap: `{manifest['files']['autoSegmentation']}`",
        f"- Blank segmentation labelmap: `{manifest['files']['blankSegmentation']}`",
        f"- Label table: `{manifest['files']['labelTable']}`",
        f"- ITK-SNAP label description: `{manifest['files']['itksnapLabelDescription']}`",
        f"- Candidate point table: `{manifest['files']['pointsTable']}`",
        f"- Rough support masks directory: `{manifest['files']['roughSupportMasksDir']}`",
        f"- Full-gyrus masks directory: `{manifest['files']['fullGyrusMasksDir']}`",
        "",
        "## Counts",
        "",
        f"- Total labels in table: {manifest['summary']['totalTargets']}",
        f"- Auto masks included in segmentation: {manifest['summary']['autoMaskTargets']}",
        f"- Per-target rough masks exported: {manifest['summary']['roughMaskTargets']}",
        f"- Full-gyrus composite masks exported: {manifest['summary']['fullGyrusCompositeTargets']}",
        f"- Fully manual labels: {manifest['summary']['manualTargets']}",
        f"- Auto-mask voxel conflicts skipped: {manifest['summary']['autoMaskConflictVoxels']}",
        "",
    ]
    if manifest.get("autoMaskConflictTargets"):
        lines.extend(
            [
                "## Auto-Mask Overlap Notes",
                "",
                "These overlaps were skipped in the combined auto labelmap so earlier labels were not overwritten. QC these areas before treating the combined auto segmentation as final.",
                "",
            ]
        )
        for item in manifest["autoMaskConflictTargets"]:
            overlaps = ", ".join(
                overlap["preferredName"] or str(overlap["labelValue"])
                for overlap in item["overlapsExistingLabels"]
            )
            lines.append(
                f"- {item['preferredName']}: {item['conflictVoxelCount']} voxels overlapped existing label(s): {overlaps}"
            )
        lines.append("")

    lines.extend(
        [
            "## Workflow",
            "",
            "1. QC `auto_seed_segmentation.nii.gz` first.",
            "2. Use `points.tsv` and `rough_support_masks/` to refine support-anchor targets.",
            "3. Paint fully manual targets using the label values in `labels.tsv`.",
            "4. Save edited segmentation as a new file; do not overwrite the generated export unless intentionally regenerating.",
            "",
            "## Fully Manual Targets",
            "",
        ]
    )
    for item in manifest["manualTargets"]:
        lines.append(f"- {item['preferredName']} (`{item['id']}`)")
    lines.extend(["", "## Edit/Refine Targets", ""])
    for item in manifest["editTargets"]:
        lines.append(f"- {item['preferredName']} (`{item['id']}`)")
    lines.extend(["", "## Full-Gyrus Composite Masks", ""])
    if manifest["fullGyrusCompositeTargets"]:
        for item in manifest["fullGyrusCompositeTargets"]:
            wm_note = (
                f"{item['whiteMatterComponentCount']} WM component(s)"
                if item["includesWhiteMatter"]
                else "cortical parcel only; no exact WM parcel"
            )
            lines.append(
                f"- {item['preferredName']} (`{item['id']}`): {item['voxelCount']} voxels, {wm_note}, `{item['path']}`"
            )
    else:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--review-output", type=Path, default=DEFAULT_REVIEW)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue = load_json(args.queue)
    output_dir = args.output_dir
    rough_dir = output_dir / "rough_support_masks"
    full_gyrus_dir = output_dir / "full_gyrus_masks"
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_generated_dir(rough_dir)
    clean_generated_dir(full_gyrus_dir)

    t1_path = REPO_ROOT / queue["coordinateSpace"]["image"]
    t1_image = nib.load(str(t1_path))
    t1_output = output_dir / "t1_conformed.nii.gz"
    nib.save(make_nifti_like(t1_image, np.asarray(t1_image.dataobj)), str(t1_output))

    targets = queue["targets"]
    label_rows = make_label_table(targets)
    label_by_id = {row["id"]: row for row in label_rows}
    label_by_value = {int(row["labelValue"]): row for row in label_rows}
    save_tsv(output_dir / "labels.tsv", label_rows)
    write_itksnap_label_description(output_dir / "itksnap_label_descriptions.txt", label_rows)
    save_tsv(output_dir / "points.tsv", point_rows(targets, label_by_id))

    cache = VolumeCache()
    shape = t1_image.shape
    auto_seg = np.zeros(shape, dtype=np.uint16)
    blank_seg = np.zeros(shape, dtype=np.uint16)
    conflict_voxels = 0
    conflict_targets = []
    auto_mask_targets = []
    rough_mask_targets = []
    full_gyrus_targets = []
    manual_targets = []
    edit_targets = []

    for target in targets:
        label_value = int(label_by_id[target["id"]]["labelValue"])
        full_gyrus = full_gyrus_mask(target, cache, shape)
        if full_gyrus:
            mask, full_gyrus_record = full_gyrus
            full_gyrus_path = full_gyrus_dir / f"{label_value:03d}_{target['id']}.nii.gz"
            nib.save(make_nifti_like(t1_image, mask.astype(np.uint8)), str(full_gyrus_path))
            full_gyrus_targets.append(
                {
                    **full_gyrus_record,
                    "labelValue": label_value,
                    "path": relative_path(full_gyrus_path),
                }
            )
        else:
            mask = combined_mask(target, cache, shape)
        has_mask = bool(mask.any())
        if target["userAction"] == "qc_auto_point" and has_mask:
            conflict = mask & (auto_seg != 0) & (auto_seg != label_value)
            target_conflicts = int(conflict.sum())
            conflict_voxels += target_conflicts
            if target_conflicts:
                existing_values = sorted(int(value) for value in np.unique(auto_seg[conflict]))
                conflict_targets.append(
                    {
                        "id": target["id"],
                        "preferredName": target["preferredName"],
                        "labelValue": label_value,
                        "conflictVoxelCount": target_conflicts,
                        "overlapsExistingLabels": [
                            {
                                "labelValue": value,
                                "id": label_by_value.get(value, {}).get("id", ""),
                                "preferredName": label_by_value.get(value, {}).get("preferredName", ""),
                            }
                            for value in existing_values
                        ],
                    }
                )
            auto_seg[mask & (auto_seg == 0)] = label_value
            auto_mask_targets.append(
                {
                    "id": target["id"],
                    "preferredName": target["preferredName"],
                    "labelValue": label_value,
                    "voxelCount": int(mask.sum()),
                }
            )
        elif target["userAction"] == "edit_or_replace_anchor":
            edit_targets.append(
                {
                    "id": target["id"],
                    "preferredName": target["preferredName"],
                    "labelValue": label_value,
                    "hasRoughMask": has_mask,
                }
            )
            if has_mask:
                rough_path = rough_dir / f"{label_value:03d}_{target['id']}.nii.gz"
                nib.save(make_nifti_like(t1_image, mask.astype(np.uint8)), str(rough_path))
                rough_mask_targets.append(
                    {
                        "id": target["id"],
                        "preferredName": target["preferredName"],
                        "labelValue": label_value,
                        "voxelCount": int(mask.sum()),
                        "path": relative_path(rough_path),
                    }
                )
        else:
            manual_targets.append(
                {
                    "id": target["id"],
                    "preferredName": target["preferredName"],
                    "labelValue": label_value,
                }
            )

    auto_path = output_dir / "auto_seed_segmentation.nii.gz"
    blank_path = output_dir / "blank_segmentation.nii.gz"
    nib.save(make_nifti_like(t1_image, auto_seg), str(auto_path))
    nib.save(make_nifti_like(t1_image, blank_seg), str(blank_path))

    manifest = {
        "version": "0.1.0",
        "kind": "itksnap_working_set",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "coordinateSpace": queue["coordinateSpace"],
        "files": {
            "mainImage": relative_path(t1_output),
            "autoSegmentation": relative_path(auto_path),
            "blankSegmentation": relative_path(blank_path),
            "labelTable": relative_path(output_dir / "labels.tsv"),
            "itksnapLabelDescription": relative_path(output_dir / "itksnap_label_descriptions.txt"),
            "pointsTable": relative_path(output_dir / "points.tsv"),
            "roughSupportMasksDir": relative_path(rough_dir),
            "fullGyrusMasksDir": relative_path(full_gyrus_dir),
        },
        "summary": {
            "totalTargets": len(targets),
            "autoMaskTargets": len(auto_mask_targets),
            "roughMaskTargets": len(rough_mask_targets),
            "fullGyrusCompositeTargets": len(full_gyrus_targets),
            "manualTargets": len(manual_targets),
            "editTargets": len(edit_targets),
            "autoMaskConflictVoxels": conflict_voxels,
        },
        "autoMaskTargets": auto_mask_targets,
        "autoMaskConflictTargets": conflict_targets,
        "roughMaskTargets": rough_mask_targets,
        "fullGyrusCompositeTargets": full_gyrus_targets,
        "editTargets": edit_targets,
        "manualTargets": manual_targets,
    }
    write_json(args.manifest_output, manifest)
    write_review(args.review_output, manifest)

    print(f"Wrote {relative_path(args.manifest_output)}")
    print(f"Wrote {relative_path(args.review_output)}")
    print(json.dumps(manifest["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
