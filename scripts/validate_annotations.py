#!/usr/bin/env python3
"""Validate anatomy quiz metadata without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
DIFFICULTIES = {"beginner", "intermediate", "advanced"}
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
VIEWS = {"axial", "coronal", "sagittal", "mpr"}
TARGET_STATUSES = {"needs_localization", "draft", "reviewed"}


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON at line {exc.lineno}: {exc.msg}") from exc


def require_string(
    obj: dict[str, Any], key: str, context: str, errors: list[str]
) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}: `{key}` must be a non-empty string")
        return None
    return value


def require_string_list(
    obj: dict[str, Any], key: str, context: str, errors: list[str]
) -> list[str]:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"{context}: `{key}` must be a non-empty list")
        return []

    strings = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{context}: `{key}[{index}]` must be a non-empty string")
        else:
            strings.append(item)
    return strings


def validate_target(
    target: dict[str, Any],
    structure_id: str,
    target_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    context = f"{structure_id}.quizTargets"

    target_id = require_string(target, "id", context, errors)
    if target_id:
        if not ID_RE.match(target_id):
            errors.append(f"{context}: target id `{target_id}` must be snake_case")
        if target_id in target_ids:
            errors.append(f"{context}: duplicate target id `{target_id}`")
        target_ids.add(target_id)

    view = require_string(target, "view", context, errors)
    if view and view not in VIEWS:
        errors.append(f"{context}.{target_id}: invalid view `{view}`")

    status = require_string(target, "status", context, errors)
    if status and status not in TARGET_STATUSES:
        errors.append(f"{context}.{target_id}: invalid status `{status}`")

    require_string(target, "prompt", context, errors)

    has_position = any(key in target for key in ("voxel", "worldMm", "linkedSopInstanceUid"))
    if status in {"draft", "reviewed"} and not has_position:
        errors.append(
            f"{context}.{target_id}: `{status}` targets need voxel, worldMm, or linkedSopInstanceUid"
        )
    if status == "needs_localization" and has_position:
        warnings.append(
            f"{context}.{target_id}: target has coordinates but status is needs_localization"
        )


def validate_structure(
    structure: dict[str, Any],
    seen_ids: set[str],
    target_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    structure_id = require_string(structure, "id", "structure", errors)
    context = structure_id or "structure"

    if structure_id:
        if not ID_RE.match(structure_id):
            errors.append(f"{context}: id must be snake_case")
        if structure_id in seen_ids:
            errors.append(f"{context}: duplicate structure id")
        seen_ids.add(structure_id)

    preferred_name = require_string(structure, "preferredName", context, errors)
    accepted = require_string_list(structure, "acceptedAnswers", context, errors)
    require_string(structure, "description", context, errors)

    difficulty = require_string(structure, "difficulty", context, errors)
    if difficulty and difficulty not in DIFFICULTIES:
        errors.append(f"{context}: invalid difficulty `{difficulty}`")

    systems = require_string_list(structure, "systems", context, errors)
    invalid_systems = sorted(set(systems) - SYSTEMS)
    if invalid_systems:
        errors.append(f"{context}: invalid systems {', '.join(invalid_systems)}")

    if preferred_name and accepted:
        accepted_normalized = {item.lower().strip() for item in accepted}
        if preferred_name.lower().strip() not in accepted_normalized:
            warnings.append(f"{context}: preferredName is not listed in acceptedAnswers")

    targets = structure.get("quizTargets")
    if not isinstance(targets, list) or not targets:
        errors.append(f"{context}: quizTargets must be a non-empty list")
        return

    for target in targets:
        if not isinstance(target, dict):
            errors.append(f"{context}: each quiz target must be an object")
            continue
        validate_target(target, context, target_ids, errors, warnings)


def validate_document(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    require_string(data, "version", "document", errors)

    study = data.get("study")
    if not isinstance(study, dict):
        errors.append("document: `study` must be an object")
    else:
        for key in ("id", "title", "modality", "sequence"):
            require_string(study, key, "study", errors)
        if study.get("modality") != "MR":
            errors.append("study: modality must be `MR`")

    structures = data.get("structures")
    if not isinstance(structures, list) or not structures:
        errors.append("document: `structures` must be a non-empty list")
        return errors, warnings

    seen_ids: set[str] = set()
    target_ids: set[str] = set()
    for structure in structures:
        if not isinstance(structure, dict):
            errors.append("document: every structure must be an object")
            continue
        validate_structure(structure, seen_ids, target_ids, errors, warnings)

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Annotation JSON files to validate.")
    args = parser.parse_args()

    exit_code = 0
    for path in args.paths:
        try:
            data = load_json(path)
            errors, warnings = validate_document(data)
        except ValueError as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            exit_code = 1
            continue

        for warning in warnings:
            print(f"WARNING {path}: {warning}")
        for error in errors:
            print(f"ERROR {path}: {error}", file=sys.stderr)

        if errors:
            exit_code = 1
        else:
            count = len(data.get("structures", []))
            print(f"OK {path}: {count} structures")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

