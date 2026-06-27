#!/usr/bin/env python3
"""Build T1 localization worklists from the target crosswalk and FreeSurfer labels."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CROSSWALK = REPO_ROOT / "annotations" / "curation" / "target-crosswalk.json"
DEFAULT_DRAFT = REPO_ROOT / "annotations" / "structures" / "t1-targets.draft.json"
DEFAULT_QUEUE = REPO_ROOT / "annotations" / "localization" / "t1-localization-queue.json"
DEFAULT_REVIEW = REPO_ROOT / "annotations" / "localization" / "t1-localization-review.md"
DEFAULT_LOCALIZED_DRAFT = (
    REPO_ROOT / "annotations" / "structures" / "t1-targets.localized.draft.json"
)
DEFAULT_T1 = (
    REPO_ROOT
    / "data"
    / "processed"
    / "freesurfer_subjects"
    / "annotated_t1_nki_A00039636"
    / "mri"
    / "T1.mgz"
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, default=json_default)
        handle.write("\n")


def json_default(value: Any) -> Any:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def relative_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def round_float(value: float) -> float:
    return round(float(value), 3)


def voxel_dict(voxel: np.ndarray) -> dict[str, int]:
    return {"i": int(voxel[0]), "j": int(voxel[1]), "k": int(voxel[2])}


def world_dict(world: np.ndarray) -> dict[str, float]:
    return {
        "x": round_float(world[0]),
        "y": round_float(world[1]),
        "z": round_float(world[2]),
    }


class VolumeCache:
    def __init__(self) -> None:
        self._cache: dict[Path, tuple[nib.spatialimages.SpatialImage, np.ndarray]] = {}

    def load(self, path: Path) -> tuple[nib.spatialimages.SpatialImage, np.ndarray]:
        resolved = path.resolve()
        if resolved not in self._cache:
            image = nib.load(str(resolved))
            self._cache[resolved] = (image, np.asarray(image.dataobj))
        return self._cache[resolved]


def label_point(
    label: dict[str, Any],
    volume_cache: VolumeCache,
) -> dict[str, Any] | None:
    paths = label.get("paths", {})
    volume = paths.get("volume")
    label_value = label.get("labelValue")
    if not volume or label_value is None:
        return None

    volume_path = (REPO_ROOT / volume).resolve()
    image, data = volume_cache.load(volume_path)
    indices = np.argwhere(data == int(label_value))
    if indices.size == 0:
        return {
            "status": "missing_label_value",
            "labelId": label["id"],
            "sourceLabel": label["name"],
            "sourceAtlas": label["atlasId"],
            "labelValue": label_value,
            "sourceVolume": relative_path(volume_path),
        }

    mean = indices.mean(axis=0)
    squared_distance = np.sum((indices - mean) ** 2, axis=1)
    representative_voxel = indices[int(np.argmin(squared_distance))]
    world = nib.affines.apply_affine(image.affine, representative_voxel)
    bbox_min = indices.min(axis=0)
    bbox_max = indices.max(axis=0)

    return {
        "status": "point_from_label",
        "labelId": label["id"],
        "sourceLabel": label["name"],
        "sourceDisplayName": label["displayName"],
        "sourceAtlas": label["atlasId"],
        "sourceName": label["sourceName"],
        "labelValue": label_value,
        "sourceVolume": relative_path(volume_path),
        "voxel": voxel_dict(representative_voxel),
        "worldMm": world_dict(world),
        "voxelCount": int(indices.shape[0]),
        "boundingBoxVoxel": {
            "min": voxel_dict(bbox_min),
            "max": voxel_dict(bbox_max),
        },
    }


def union_point(
    labels: list[dict[str, Any]],
    volume_cache: VolumeCache,
) -> dict[str, Any] | None:
    usable_labels = [
        label
        for label in labels
        if label.get("paths", {}).get("volume") and label.get("labelValue") is not None
    ]
    if not usable_labels:
        return None

    volume_paths = {label["paths"]["volume"] for label in usable_labels}
    if len(volume_paths) != 1:
        return None

    volume_path = (REPO_ROOT / next(iter(volume_paths))).resolve()
    image, data = volume_cache.load(volume_path)
    mask = np.zeros(data.shape, dtype=bool)
    values: list[int] = []
    for label in usable_labels:
        value = int(label["labelValue"])
        values.append(value)
        mask |= data == value

    indices = np.argwhere(mask)
    if indices.size == 0:
        return None

    mean = indices.mean(axis=0)
    squared_distance = np.sum((indices - mean) ** 2, axis=1)
    representative_voxel = indices[int(np.argmin(squared_distance))]
    world = nib.affines.apply_affine(image.affine, representative_voxel)
    bbox_min = indices.min(axis=0)
    bbox_max = indices.max(axis=0)

    return {
        "status": "point_from_label_union",
        "sourceLabels": [
            {
                "labelId": label["id"],
                "sourceLabel": label["name"],
                "sourceAtlas": label["atlasId"],
                "labelValue": label.get("labelValue"),
            }
            for label in usable_labels
        ],
        "labelValues": values,
        "sourceVolume": relative_path(volume_path),
        "voxel": voxel_dict(representative_voxel),
        "worldMm": world_dict(world),
        "voxelCount": int(indices.shape[0]),
        "boundingBoxVoxel": {
            "min": voxel_dict(bbox_min),
            "max": voxel_dict(bbox_max),
        },
    }


def choose_localization_status(
    target: dict[str, Any],
    chosen_point: dict[str, Any] | None,
) -> tuple[str, str]:
    strategy = target["sourceStrategy"]
    if chosen_point is None:
        return ("manual_required", "fully_place_manually")
    if strategy == "freesurfer_seed":
        return ("auto_point_from_freesurfer", "qc_auto_point")
    return ("support_anchor_needs_edit", "edit_or_replace_anchor")


def build_target_localization(
    target: dict[str, Any],
    volume_cache: VolumeCache,
) -> dict[str, Any]:
    source_points = []
    for label in target.get("freeSurferLabels", []):
        point = label_point(label, volume_cache)
        if point:
            source_points.append(point)

    union = None
    if len(target.get("freeSurferLabels", [])) > 1:
        union = union_point(target["freeSurferLabels"], volume_cache)

    chosen_point = union or next(
        (point for point in source_points if point.get("status") == "point_from_label"),
        None,
    )
    localization_status, user_action = choose_localization_status(target, chosen_point)

    notes = []
    for candidate in target.get("candidateMatches", []):
        review_note = candidate.get("reviewNotes")
        if review_note and review_note not in notes:
            notes.append(review_note)

    return {
        "id": target["id"],
        "targetIndex": target["targetIndex"],
        "preferredName": target["preferredName"],
        "targetName": target["targetName"],
        "laterality": target["laterality"],
        "systems": target["systems"],
        "difficulty": target["difficulty"],
        "sourceStrategy": target["sourceStrategy"],
        "localizationStatus": localization_status,
        "userAction": user_action,
        "reviewFlags": target["reviewFlags"],
        "chosenPoint": chosen_point,
        "sourcePoints": source_points,
        "notes": notes,
    }


def summarize(localizations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(item["localizationStatus"] for item in localizations)
    action_counts = Counter(item["userAction"] for item in localizations)
    return {
        "targetCount": len(localizations),
        "byLocalizationStatus": dict(sorted(status_counts.items())),
        "byUserAction": dict(sorted(action_counts.items())),
        "autoPointCount": status_counts["auto_point_from_freesurfer"],
        "editAnchorCount": status_counts["support_anchor_needs_edit"],
        "manualRequiredCount": status_counts["manual_required"],
    }


def format_point(point: dict[str, Any] | None) -> str:
    if not point:
        return ""
    voxel = point.get("voxel", {})
    source = point.get("sourceVolume", "")
    return f"{voxel.get('i')},{voxel.get('j')},{voxel.get('k')} in `{source}`"


def write_review(path: Path, queue: dict[str, Any]) -> None:
    localizations = queue["targets"]
    by_action: dict[str, list[dict[str, Any]]] = {}
    for item in localizations:
        by_action.setdefault(item["userAction"], []).append(item)

    lines = [
        "# T1 Localization Review",
        "",
        "Generated candidate localization points in FreeSurfer conformed T1 space.",
        "",
        "## Summary",
        "",
        f"- Active T1 targets: {queue['summary']['targetCount']}",
        f"- Auto FreeSurfer points to QC: {queue['summary']['autoPointCount']}",
        f"- Support anchors that need editing/refinement: {queue['summary']['editAnchorCount']}",
        f"- Fully manual placements needed: {queue['summary']['manualRequiredCount']}",
        "",
        "## What You Need To Do",
        "",
        "1. QC the auto FreeSurfer points. These should usually be close, but can still be moved for better teaching.",
        "2. Edit or replace the support anchors. These are intentionally rough because the desired teaching structure is smaller, broader, or composite.",
        "3. Fully place the manual-required structures yourself or with a future external atlas.",
        "",
    ]

    sections = [
        ("Auto Points To QC", "qc_auto_point"),
        ("Need Edit Or Refinement", "edit_or_replace_anchor"),
        ("Need Full Manual Placement", "fully_place_manually"),
    ]
    for heading, action in sections:
        items = by_action.get(action, [])
        lines.extend([f"## {heading}", ""])
        if not items:
            lines.extend(["- None", ""])
            continue
        lines.append("| Target | Strategy | Candidate point | Notes |")
        lines.append("|---|---|---|---|")
        for item in items:
            note = " ".join(item["notes"])
            lines.append(
                f"| {item['preferredName']} | `{item['sourceStrategy']}` | {format_point(item['chosenPoint']) or 'none'} | {note} |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def localized_draft(
    draft: dict[str, Any],
    queue: dict[str, Any],
) -> dict[str, Any]:
    output = copy.deepcopy(draft)
    output["version"] = "0.1.0-localization-draft"
    output["study"]["title"] = (
        "NKI Rockland sub-A00039636 T1 MPRAGE Draft Anatomy Targets With Candidate Localizations"
    )
    localization_by_id = {item["id"]: item for item in queue["targets"]}

    for structure in output["structures"]:
        item = localization_by_id.get(structure["id"])
        if not item:
            continue
        note = (
            f"Localization status: {item['localizationStatus']} "
            f"({item['userAction']}) in FreeSurfer conformed T1.mgz space."
        )
        structure.setdefault("clinicalNotes", [])
        if note not in structure["clinicalNotes"]:
            structure["clinicalNotes"].append(note)
        chosen = item.get("chosenPoint")
        if chosen and structure.get("quizTargets"):
            target = structure["quizTargets"][0]
            target["status"] = "draft"
            target["voxel"] = chosen["voxel"]
            target["worldMm"] = chosen["worldMm"]
            if item["userAction"] == "qc_auto_point":
                target["hint"] = "Auto-populated from FreeSurfer label; QC before release."
            else:
                target["hint"] = "Support anchor only; move or refine manually before release."

    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crosswalk", type=Path, default=DEFAULT_CROSSWALK)
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--t1", type=Path, default=DEFAULT_T1)
    parser.add_argument("--queue-output", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--review-output", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--localized-draft-output", type=Path, default=DEFAULT_LOCALIZED_DRAFT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    crosswalk = load_json(args.crosswalk)
    draft = load_json(args.draft)
    t1 = nib.load(str(args.t1))
    volume_cache = VolumeCache()
    localizations = [
        build_target_localization(target, volume_cache)
        for target in crosswalk["targets"]
    ]
    queue = {
        "version": "0.1.0",
        "kind": "t1_localization_queue",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "coordinateSpace": {
            "image": relative_path(args.t1),
            "shape": list(t1.shape),
            "voxelSizeMm": [round_float(value) for value in t1.header.get_zooms()[:3]],
            "orientation": "".join(nib.aff2axcodes(t1.affine)),
            "affine": [[round_float(value) for value in row] for row in t1.affine.tolist()],
            "note": "FreeSurfer conformed T1.mgz voxel/world coordinates; working localization space, not final viewer export space.",
        },
        "summary": summarize(localizations),
        "targets": localizations,
    }
    write_json(args.queue_output, queue)
    write_review(args.review_output, queue)
    write_json(args.localized_draft_output, localized_draft(draft, queue))

    print(f"Wrote {relative_path(args.queue_output)}")
    print(f"Wrote {relative_path(args.review_output)}")
    print(f"Wrote {relative_path(args.localized_draft_output)}")
    print(json.dumps(queue["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
