#!/usr/bin/env python3
"""Build a machine-generated annotation inventory from FreeSurfer outputs."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBJECT_ID = "annotated_t1_nki_A00039636"
DEFAULT_SUBJECT_DIR = (
    REPO_ROOT
    / "data"
    / "processed"
    / "freesurfer_subjects"
    / DEFAULT_SUBJECT_ID
)
DEFAULT_OUTPUT = REPO_ROOT / "annotations" / "generated" / "freesurfer-label-inventory.json"
DEFAULT_MARKDOWN_OUTPUT = (
    REPO_ROOT / "annotations" / "generated" / "freesurfer-structure-list.md"
)
DEFAULT_FREESURFER_HOME = Path(
    os.environ.get("FREESURFER_HOME", "/Applications/freesurfer/7.3.2")
)


FIELD_MAP = {
    "Index": "index",
    "SegId": "segmentationId",
    "NVoxels": "voxelCount",
    "Volume_mm3": "volumeMm3",
    "StructName": "structureName",
    "normMean": "normMean",
    "normStdDev": "normStdDev",
    "normMin": "normMin",
    "normMax": "normMax",
    "normRange": "normRange",
    "NumVert": "vertexCount",
    "SurfArea": "surfaceAreaMm2",
    "GrayVol": "grayMatterVolumeMm3",
    "ThickAvg": "thicknessAverageMm",
    "ThickStd": "thicknessStdMm",
    "MeanCurv": "meanCurvature",
    "GausCurv": "gaussianCurvature",
    "FoldInd": "foldingIndex",
    "CurvInd": "curvatureIndex",
}

SYSTEMS = {
    "ventricles",
    "basal_ganglia",
    "white_matter",
    "brainstem",
    "cerebellum",
    "skull_base",
    "cranial_nerves",
    "vascular",
    "limbic",
    "midline",
    "cortex",
    "deep_gray",
    "csf_spaces",
}

MIDLINE_NAMES = {
    "3rd-ventricle",
    "4th-ventricle",
    "5th-ventricle",
    "brain-stem",
    "csf",
    "optic-chiasm",
}

EXCLUDE_PATTERNS = (
    "unknown",
    "hypointensities",
    "lesion",
    "undetermined",
    "exterior",
    "vessel",
    "medial_wall",
    "nofix",
    "cortex+hipamyg",
)


VOLUME_ATLASES = [
    {
        "id": "aseg",
        "displayName": "FreeSurfer aseg",
        "description": "Subcortical and major tissue-class segmentation from recon-all.",
        "sourceKind": "volume",
        "volumePath": "mri/aseg.mgz",
        "statsPath": "stats/aseg.stats",
        "lutCandidates": ("ASegStatsLUT.txt", "FreeSurferColorLUT.txt"),
    },
    {
        "id": "wmparc",
        "displayName": "FreeSurfer wmparc",
        "description": "White-matter parcellation derived from cortical labels and aseg.",
        "sourceKind": "volume",
        "volumePath": "mri/wmparc.mgz",
        "statsPath": "stats/wmparc.stats",
        "lutCandidates": ("WMParcStatsLUT.txt", "FreeSurferColorLUT.txt"),
    },
]

CORTICAL_ATLASES = [
    {
        "id": "aparc",
        "displayName": "FreeSurfer Desikan-Killiany aparc",
        "description": "Desikan-Killiany cortical surface parcellation.",
        "sourceKind": "surface_and_volume",
        "volumePath": "mri/aparc+aseg.mgz",
        "ctabPath": "label/aparc.annot.ctab",
        "statsPattern": "{hemi}.aparc.stats",
        "annotPattern": "label/{hemi}.aparc.annot",
        "volumeOffsets": {"lh": 1000, "rh": 2000},
        "defaultDifficulty": "intermediate",
    },
    {
        "id": "aparc_a2009s",
        "displayName": "FreeSurfer Destrieux aparc.a2009s",
        "description": "Destrieux sulcal/gyral cortical surface parcellation.",
        "sourceKind": "surface_and_volume",
        "volumePath": "mri/aparc.a2009s+aseg.mgz",
        "ctabPath": "label/aparc.annot.a2009s.ctab",
        "statsPattern": "{hemi}.aparc.a2009s.stats",
        "annotPattern": "label/{hemi}.aparc.a2009s.annot",
        "volumeOffsets": {"lh": 11100, "rh": 12100},
        "defaultDifficulty": "advanced",
    },
    {
        "id": "aparc_dkt",
        "displayName": "FreeSurfer DKT atlas",
        "description": "DKT cortical surface parcellation.",
        "sourceKind": "surface_and_volume",
        "volumePath": "mri/aparc.DKTatlas+aseg.mgz",
        "ctabPath": "label/aparc.annot.DKTatlas.ctab",
        "statsPattern": "{hemi}.aparc.DKTatlas.stats",
        "annotPattern": "label/{hemi}.aparc.DKTatlas.annot",
        "volumeOffsets": {"lh": 1000, "rh": 2000},
        "defaultDifficulty": "intermediate",
    },
    {
        "id": "ba_exvivo",
        "displayName": "FreeSurfer ex vivo Brodmann areas",
        "description": "Surface-projected ex vivo Brodmann/visual/MT/entorhinal labels.",
        "sourceKind": "surface",
        "ctabPath": "label/BA_exvivo.ctab",
        "statsPattern": "{hemi}.BA_exvivo.stats",
        "annotPattern": "label/{hemi}.BA_exvivo.annot",
        "volumeOffsets": None,
        "defaultDifficulty": "advanced",
    },
    {
        "id": "ba_exvivo_thresh",
        "displayName": "FreeSurfer thresholded ex vivo Brodmann areas",
        "description": "Thresholded surface-projected ex vivo Brodmann/visual/MT/entorhinal labels.",
        "sourceKind": "surface",
        "ctabPath": "label/BA_exvivo.thresh.ctab",
        "statsPattern": "{hemi}.BA_exvivo.thresh.stats",
        "annotPattern": "label/{hemi}.BA_exvivo.thresh.annot",
        "volumeOffsets": None,
        "defaultDifficulty": "advanced",
    },
]


def coerce_scalar(value: str) -> int | float | str:
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?", value):
        return float(value)
    if re.fullmatch(r"[-+]?\d+[eE][-+]?\d+", value):
        return float(value)
    return value


def clean_id(*parts: object) -> str:
    text = "_".join(str(part) for part in parts if part is not None and str(part))
    text = text.replace("+", "_plus_")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    text = re.sub(r"_+", "_", text)
    return text or "unknown"


def relative_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def existing_relative(path: Path | None) -> str | None:
    if path and path.exists():
        return relative_path(path)
    return None


def parse_color_table(path: Path) -> dict[str, Any]:
    by_index: dict[int, dict[str, Any]] = {}
    by_name: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return {"path": path, "byIndex": by_index, "byName": by_name}

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) < 6:
                continue
            try:
                index = int(parts[0])
                rgba = [int(value) for value in parts[-4:]]
            except ValueError:
                continue
            name = " ".join(parts[1:-4])
            entry = {
                "index": index,
                "name": name,
                "color": {
                    "r": rgba[0],
                    "g": rgba[1],
                    "b": rgba[2],
                    "a": rgba[3],
                },
            }
            by_index[index] = entry
            by_name[name] = entry
    return {"path": path, "byIndex": by_index, "byName": by_name}


def parse_stats(path: Path) -> dict[str, Any]:
    headers: list[str] = []
    rows: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}

    if not path.exists():
        return {"path": path, "headers": headers, "rows": rows, "metadata": metadata}

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("#"):
                content = stripped[1:].strip()
                if content.startswith("ColHeaders"):
                    headers = content.split()[1:]
                elif content.startswith("cvs_version"):
                    metadata["freesurferVersion"] = content.split(maxsplit=1)[1]
                elif content.startswith("anatomy_type"):
                    metadata["anatomyType"] = content.split(maxsplit=1)[1]
                elif content.startswith("subjectname"):
                    metadata["subjectName"] = content.split(maxsplit=1)[1]
                elif content.startswith("hemi"):
                    metadata["hemisphere"] = content.split(maxsplit=1)[1]
                elif content.startswith("SegVolFile"):
                    metadata["segmentationVolumeFile"] = content.split(maxsplit=1)[1]
                elif content.startswith("AnnotationFile"):
                    metadata["annotationFile"] = content.split(maxsplit=1)[1]
                elif content.startswith("ColorTable"):
                    metadata["colorTable"] = content.split(maxsplit=1)[1]
                continue

            if not headers:
                continue
            parts = stripped.split()
            if len(parts) < len(headers):
                continue
            row = {
                header: coerce_scalar(value)
                for header, value in zip(headers, parts[: len(headers)])
            }
            rows.append(row)

    return {"path": path, "headers": headers, "rows": rows, "metadata": metadata}


def normalize_stats(row: dict[str, Any]) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    for key, value in row.items():
        if key == "StructName":
            continue
        stats[FIELD_MAP.get(key, clean_id(key))] = value
    return stats


def infer_laterality(name: str, hemi: str | None = None) -> str:
    lowered = name.lower()
    if hemi == "lh" or lowered.startswith("left-") or lowered.startswith("wm-lh-"):
        return "left"
    if hemi == "rh" or lowered.startswith("right-") or lowered.startswith("wm-rh-"):
        return "right"
    if lowered in MIDLINE_NAMES or lowered.startswith("cc_"):
        return "midline"
    return "not_applicable"


def humanize_name(name: str, hemi: str | None = None) -> str:
    text = name
    text = re.sub(r"^wm-lh-", "Left white matter ", text)
    text = re.sub(r"^wm-rh-", "Right white matter ", text)
    text = re.sub(r"^Left-", "Left ", text)
    text = re.sub(r"^Right-", "Right ", text)
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if hemi == "lh" and not text.lower().startswith("left"):
        text = f"Left {text}"
    if hemi == "rh" and not text.lower().startswith("right"):
        text = f"Right {text}"
    return text[:1].upper() + text[1:]


def infer_systems(name: str, atlas_id: str, source_kind: str) -> list[str]:
    lowered = name.lower()
    systems: set[str] = set()

    if "ventricle" in lowered or "choroid" in lowered or lowered == "csf":
        systems.update({"ventricles", "csf_spaces"})
    if "caudate" in lowered or "putamen" in lowered or "pallidum" in lowered:
        systems.update({"basal_ganglia", "deep_gray"})
    if "accumbens" in lowered or "substantia" in lowered:
        systems.update({"basal_ganglia", "deep_gray"})
    if "thalamus" in lowered or "ventraldc" in lowered:
        systems.add("deep_gray")
    if any(term in lowered for term in ("hippocampus", "amygdala", "entorhinal", "perirhinal", "parahippocampal", "cingul")):
        systems.add("limbic")
    if "brain-stem" in lowered or "brainstem" in lowered:
        systems.add("brainstem")
    if "cerebell" in lowered or "vermis" in lowered:
        systems.add("cerebellum")
    if "white-matter" in lowered or lowered.startswith("wm-") or "corpuscallosum" in lowered or lowered.startswith("cc_"):
        systems.add("white_matter")
    if "optic-chiasm" in lowered:
        systems.update({"cranial_nerves", "skull_base"})
    if "vessel" in lowered:
        systems.add("vascular")
    if "surface" in source_kind or atlas_id.startswith(("aparc", "ba_")):
        systems.add("cortex")
    if atlas_id == "surface_label_files" and any(term in lowered for term in ("v1", "v2", "mt", "hoc", "fg")):
        systems.add("cortex")

    valid = sorted(system for system in systems if system in SYSTEMS)
    if valid:
        return valid
    if atlas_id == "wmparc":
        return ["white_matter"]
    if "surface" in source_kind:
        return ["cortex"]
    return ["deep_gray"]


def suggest_difficulty(name: str, atlas_id: str, default: str | None = None) -> str:
    lowered = name.lower()
    beginner_terms = (
        "lateral-ventricle",
        "3rd-ventricle",
        "4th-ventricle",
        "thalamus",
        "caudate",
        "putamen",
        "pallidum",
        "hippocampus",
        "amygdala",
        "brain-stem",
        "cerebellum",
        "cc_",
    )
    if atlas_id == "aseg" and any(term in lowered for term in beginner_terms):
        return "beginner"
    if atlas_id in {"aparc", "aparc_dkt", "wmparc"}:
        return "intermediate"
    if default:
        return default
    if atlas_id.startswith("ba_") or atlas_id == "surface_label_files":
        return "advanced"
    return "intermediate"


def metric_count(stats: dict[str, Any]) -> float | None:
    for key in ("volumeMm3", "grayMatterVolumeMm3", "vertexCount", "voxelCount"):
        value = stats.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def include_suggestion(
    name: str,
    laterality: str,
    atlas_id: str,
    stats: dict[str, Any],
    teaching_side: str,
) -> tuple[bool, str]:
    lowered = name.lower()
    if any(pattern in lowered for pattern in EXCLUDE_PATTERNS):
        return False, "non-teaching or technical label"
    count = metric_count(stats)
    if count is not None and count <= 0:
        return False, "absent or empty in this subject"
    if laterality == "right" and teaching_side == "left":
        return False, "right side reserved as unlabeled comparison"
    if atlas_id == "surface_label_files" and lowered.endswith(".thresh"):
        return True, "thresholded left/midline surface label candidate"
    return True, "left/midline label candidate"


def color_for_label(
    label_value: int | None,
    label_name: str,
    color_tables: list[dict[str, Any]],
) -> dict[str, int] | None:
    for table in color_tables:
        if label_value is not None and label_value in table["byIndex"]:
            return table["byIndex"][label_value]["color"]
        if label_name in table["byName"]:
            return table["byName"][label_name]["color"]
    return None


def make_label_entry(
    *,
    atlas_id: str,
    source_name: str,
    source_kind: str,
    label_name: str,
    stats: dict[str, Any],
    paths: dict[str, str | None],
    teaching_side: str,
    hemi: str | None = None,
    label_value: int | None = None,
    label_index: int | None = None,
    color: dict[str, int] | None = None,
    default_difficulty: str | None = None,
) -> dict[str, Any]:
    laterality = infer_laterality(label_name, hemi)
    include, include_reason = include_suggestion(
        label_name, laterality, atlas_id, stats, teaching_side
    )
    systems = infer_systems(label_name, atlas_id, source_kind)
    entry = {
        "id": clean_id(atlas_id, hemi, label_name),
        "atlasId": atlas_id,
        "sourceName": source_name,
        "sourceKind": source_kind,
        "name": label_name,
        "displayName": humanize_name(label_name, hemi),
        "laterality": laterality,
        "hemisphere": hemi,
        "labelValue": label_value,
        "labelIndex": label_index,
        "color": color,
        "systemsSuggested": systems,
        "difficultySuggested": suggest_difficulty(label_name, atlas_id, default_difficulty),
        "includeSuggested": include,
        "includeReason": include_reason,
        "curationStatus": "needs_qc",
        "stats": stats,
        "paths": {key: value for key, value in paths.items() if value},
    }
    return {key: value for key, value in entry.items() if value is not None}


def pick_lut(freesurfer_home: Path, candidates: tuple[str, ...]) -> Path:
    for candidate in candidates:
        path = freesurfer_home / candidate
        if path.exists():
            return path
    return freesurfer_home / candidates[0]


def build_volume_labels(
    subject_dir: Path,
    freesurfer_home: Path,
    teaching_side: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    freesurfer_lut = parse_color_table(freesurfer_home / "FreeSurferColorLUT.txt")

    for atlas in VOLUME_ATLASES:
        stats_path = subject_dir / atlas["statsPath"]
        volume_path = subject_dir / atlas["volumePath"]
        lut_path = pick_lut(freesurfer_home, atlas["lutCandidates"])
        atlas_lut = parse_color_table(lut_path)
        stats_doc = parse_stats(stats_path)
        sources.append(
            {
                "id": atlas["id"],
                "displayName": atlas["displayName"],
                "description": atlas["description"],
                "sourceKind": atlas["sourceKind"],
                "volumePath": existing_relative(volume_path),
                "statsPath": existing_relative(stats_path),
                "colorTablePath": existing_relative(lut_path),
                "entryCount": len(stats_doc["rows"]),
            }
        )

        for row in stats_doc["rows"]:
            label_name = str(row.get("StructName", "Unknown"))
            label_value = row.get("SegId")
            if not isinstance(label_value, int):
                label_value = None
            normalized = normalize_stats(row)
            labels.append(
                make_label_entry(
                    atlas_id=atlas["id"],
                    source_name=atlas["displayName"],
                    source_kind=atlas["sourceKind"],
                    label_name=label_name,
                    stats=normalized,
                    paths={
                        "volume": existing_relative(volume_path),
                        "stats": existing_relative(stats_path),
                        "colorTable": existing_relative(lut_path),
                    },
                    teaching_side=teaching_side,
                    label_value=label_value,
                    color=color_for_label(label_value, label_name, [atlas_lut, freesurfer_lut]),
                )
            )

    return labels, sources


def build_cortical_labels(
    subject_dir: Path,
    teaching_side: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []

    for atlas in CORTICAL_ATLASES:
        ctab_path = subject_dir / atlas["ctabPath"]
        ctab = parse_color_table(ctab_path)
        volume_path = subject_dir / atlas["volumePath"] if atlas.get("volumePath") else None
        atlas_entry_count = 0
        sources.append(
            {
                "id": atlas["id"],
                "displayName": atlas["displayName"],
                "description": atlas["description"],
                "sourceKind": atlas["sourceKind"],
                "volumePath": existing_relative(volume_path),
                "colorTablePath": existing_relative(ctab_path),
                "leftAnnotationPath": existing_relative(
                    subject_dir / str(atlas["annotPattern"]).format(hemi="lh")
                ),
                "rightAnnotationPath": existing_relative(
                    subject_dir / str(atlas["annotPattern"]).format(hemi="rh")
                ),
            }
        )

        for hemi in ("lh", "rh"):
            stats_path = subject_dir / "stats" / str(atlas["statsPattern"]).format(hemi=hemi)
            annot_path = subject_dir / str(atlas["annotPattern"]).format(hemi=hemi)
            stats_doc = parse_stats(stats_path)
            atlas_entry_count += len(stats_doc["rows"])
            offsets = atlas.get("volumeOffsets")
            offset = offsets.get(hemi) if isinstance(offsets, dict) else None

            for row in stats_doc["rows"]:
                label_name = str(row.get("StructName", "unknown"))
                ctab_entry = ctab["byName"].get(label_name)
                label_index = ctab_entry["index"] if ctab_entry else None
                label_value = None
                if isinstance(offset, int) and isinstance(label_index, int):
                    label_value = offset + label_index
                labels.append(
                    make_label_entry(
                        atlas_id=atlas["id"],
                        source_name=atlas["displayName"],
                        source_kind=atlas["sourceKind"],
                        label_name=label_name,
                        stats=normalize_stats(row),
                        paths={
                            "volume": existing_relative(volume_path),
                            "surfaceAnnotation": existing_relative(annot_path),
                            "stats": existing_relative(stats_path),
                            "colorTable": existing_relative(ctab_path),
                        },
                        teaching_side=teaching_side,
                        hemi=hemi,
                        label_value=label_value,
                        label_index=label_index,
                        color=ctab_entry["color"] if ctab_entry else None,
                        default_difficulty=str(atlas["defaultDifficulty"]),
                    )
                )

        sources[-1]["entryCount"] = atlas_entry_count

    return labels, sources


def parse_label_vertex_count(path: Path) -> int | None:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if re.fullmatch(r"\d+", stripped):
                    return int(stripped)
                return None
    except OSError:
        return None
    return None


def build_surface_label_file_labels(
    subject_dir: Path,
    teaching_side: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    label_dir = subject_dir / "label"
    labels: list[dict[str, Any]] = []
    paths = sorted(label_dir.glob("[lr]h.*.label"))

    for path in paths:
        hemi, raw_name = path.name.split(".", maxsplit=1)
        label_name = raw_name.removesuffix(".label")
        labels.append(
            make_label_entry(
                atlas_id="surface_label_files",
                source_name="FreeSurfer surface label files",
                source_kind="surface_label_file",
                label_name=label_name,
                stats={"vertexCount": parse_label_vertex_count(path)},
                paths={"surfaceLabel": existing_relative(path)},
                teaching_side=teaching_side,
                hemi=hemi,
                default_difficulty="advanced",
            )
        )

    source = {
        "id": "surface_label_files",
        "displayName": "FreeSurfer surface label files",
        "description": "Individual .label files for ex vivo, visual, fusiform, occipital, cortex, and related surface ROIs.",
        "sourceKind": "surface_label_file",
        "labelDirectory": existing_relative(label_dir),
        "entryCount": len(labels),
    }
    return labels, [source]


def summarize(labels: list[dict[str, Any]], sources: list[dict[str, Any]]) -> dict[str, Any]:
    by_atlas = Counter(label["atlasId"] for label in labels)
    by_laterality = Counter(label["laterality"] for label in labels)
    by_difficulty = Counter(label["difficultySuggested"] for label in labels)
    by_include = Counter("included" if label["includeSuggested"] else "held_back" for label in labels)
    return {
        "sourceCount": len(sources),
        "labelCount": len(labels),
        "includeSuggestedCount": by_include["included"],
        "heldBackCount": by_include["held_back"],
        "byAtlas": dict(sorted(by_atlas.items())),
        "byLaterality": dict(sorted(by_laterality.items())),
        "byDifficulty": dict(sorted(by_difficulty.items())),
    }


def format_metric(stats: dict[str, Any]) -> str:
    for key, label in (
        ("volumeMm3", "mm3"),
        ("grayMatterVolumeMm3", "gray mm3"),
        ("surfaceAreaMm2", "mm2"),
        ("vertexCount", "vertices"),
    ):
        value = stats.get(key)
        if isinstance(value, float):
            return f"{value:.1f} {label}"
        if isinstance(value, int):
            return f"{value} {label}"
    return ""


def write_markdown_inventory(inventory: dict[str, Any], output: Path) -> None:
    labels = inventory["labels"]
    labels_by_atlas: dict[str, list[dict[str, Any]]] = {}
    source_by_id = {source["id"]: source for source in inventory["sources"]}
    for label in labels:
        labels_by_atlas.setdefault(label["atlasId"], []).append(label)

    lines = [
        "# FreeSurfer Structure List",
        "",
        "Machine-generated list of current atlas-derived annotation candidates.",
        "",
        "Use this as an inventory, not as final reviewed teaching content.",
        "",
        "## Summary",
        "",
        f"- Subject: `{inventory['subject']['id']}`",
        f"- Generated: `{inventory['generatedAt']}`",
        f"- Sources: {inventory['summary']['sourceCount']}",
        f"- Total labels: {inventory['summary']['labelCount']}",
        f"- Suggested first-pass teaching labels: {inventory['summary']['includeSuggestedCount']}",
        f"- Teaching side convention: `{inventory['curationPolicy']['teachingLaterality']}`",
        "",
        "## Sources",
        "",
    ]

    for source in inventory["sources"]:
        lines.append(
            f"- `{source['id']}`: {source['displayName']} "
            f"({source.get('entryCount', 0)} labels)"
        )

    for atlas_id in sorted(labels_by_atlas):
        source = source_by_id.get(atlas_id, {"displayName": atlas_id})
        atlas_labels = sorted(
            labels_by_atlas[atlas_id],
            key=lambda item: (
                item.get("laterality", ""),
                str(item.get("name", "")).lower(),
            ),
        )
        lines.extend(["", f"## {source['displayName']}", ""])
        for label in atlas_labels:
            include = "yes" if label["includeSuggested"] else "no"
            value = label.get("labelValue")
            index = label.get("labelIndex")
            metric = format_metric(label.get("stats", {}))
            details = [
                f"laterality: {label['laterality']}",
                f"difficulty: {label['difficultySuggested']}",
                f"first-pass: {include}",
            ]
            if value is not None:
                details.append(f"value: {value}")
            elif index is not None:
                details.append(f"index: {index}")
            if metric:
                details.append(metric)
            lines.append(f"- {label['displayName']} ({'; '.join(details)})")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def build_inventory(subject_dir: Path, freesurfer_home: Path, teaching_side: str) -> dict[str, Any]:
    labels: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []

    volume_labels, volume_sources = build_volume_labels(
        subject_dir, freesurfer_home, teaching_side
    )
    cortical_labels, cortical_sources = build_cortical_labels(subject_dir, teaching_side)
    surface_file_labels, surface_file_sources = build_surface_label_file_labels(
        subject_dir, teaching_side
    )
    labels.extend(volume_labels)
    labels.extend(cortical_labels)
    labels.extend(surface_file_labels)
    sources.extend(volume_sources)
    sources.extend(cortical_sources)
    sources.extend(surface_file_sources)

    subject_id = subject_dir.name
    fs_version = None
    for stats_path in (subject_dir / "stats").glob("*.stats"):
        stats_doc = parse_stats(stats_path)
        fs_version = stats_doc["metadata"].get("freesurferVersion")
        if fs_version:
            break

    inventory = {
        "version": "0.1.0",
        "kind": "freesurfer_label_inventory",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "subject": {
            "id": subject_id,
            "sourceDataset": "NKI Rockland Sample / RawDataBIDSLatest",
            "sourceParticipant": "sub-A00039636",
            "sourceSession": "ses-BAS1",
            "sourceSequence": "3D T1 MPRAGE",
            "subjectDir": existing_relative(subject_dir),
            "freesurferHome": existing_relative(freesurfer_home),
            "freesurferVersion": fs_version,
        },
        "curationPolicy": {
            "teachingLaterality": teaching_side,
            "rightSideUse": "reserved as unlabeled comparison for most bilateral anatomy",
            "statusMeaning": "needs_qc means atlas-derived and not yet manually reviewed for teaching use",
            "surfaceCaveat": "FreeSurfer completed, but final sphere/sphere.reg outputs reported one residual negative triangle; QC surface-derived cortical labels before teaching use.",
        },
        "sources": sources,
        "labels": labels,
        "summary": summarize(labels, sources),
    }
    return inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--subject-dir",
        type=Path,
        default=DEFAULT_SUBJECT_DIR,
        help="FreeSurfer subject directory.",
    )
    parser.add_argument(
        "--freesurfer-home",
        type=Path,
        default=DEFAULT_FREESURFER_HOME,
        help="FreeSurfer installation directory containing LUT files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON path.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=DEFAULT_MARKDOWN_OUTPUT,
        help="Readable Markdown list output path. Pass an empty string to skip.",
    )
    parser.add_argument(
        "--teaching-side",
        choices=("left", "right"),
        default="left",
        help="Preferred side for first-pass unilateral teaching annotations.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subject_dir = args.subject_dir.resolve()
    freesurfer_home = args.freesurfer_home.resolve()
    output = args.output.resolve()
    markdown_output = args.markdown_output

    if not subject_dir.exists():
        raise SystemExit(f"FreeSurfer subject directory not found: {subject_dir}")
    if not (subject_dir / "stats").exists() or not (subject_dir / "label").exists():
        raise SystemExit(f"Expected FreeSurfer stats/label directories in: {subject_dir}")

    inventory = build_inventory(subject_dir, freesurfer_home, args.teaching_side)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(inventory, handle, indent=2, sort_keys=False)
        handle.write("\n")
    if markdown_output:
        write_markdown_inventory(inventory, markdown_output.resolve())

    summary = inventory["summary"]
    print(f"Wrote {relative_path(output)}")
    if markdown_output:
        print(f"Wrote {relative_path(markdown_output.resolve())}")
    print(
        f"{summary['labelCount']} labels from {summary['sourceCount']} sources; "
        f"{summary['includeSuggestedCount']} suggested for first-pass teaching"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
