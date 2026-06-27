#!/usr/bin/env python3
"""Build a static OHIF dicomjson manifest from a de-identified DICOM series."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


try:
    import pydicom
except ImportError:  # pragma: no cover - depends on local environment
    pydicom = None


METADATA_FIELDS = [
    "Columns",
    "Rows",
    "InstanceNumber",
    "AcquisitionNumber",
    "PhotometricInterpretation",
    "BitsAllocated",
    "BitsStored",
    "PixelRepresentation",
    "SamplesPerPixel",
    "PixelSpacing",
    "HighBit",
    "ImageOrientationPatient",
    "ImagePositionPatient",
    "FrameOfReferenceUID",
    "ImageType",
    "Modality",
    "SOPInstanceUID",
    "SeriesInstanceUID",
    "StudyInstanceUID",
    "SliceThickness",
    "SpacingBetweenSlices",
    "WindowCenter",
    "WindowWidth",
    "RescaleIntercept",
    "RescaleSlope",
]


def json_value(value: Any) -> Any:
    if hasattr(value, "original_string"):
        value = value.original_string
    if isinstance(value, (str, int, float)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if value.__class__.__name__ in {"MultiValue", "PersonName"}:
        return [json_value(item) for item in value] if not isinstance(value, str) else str(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        pass
    return str(value)


def read_dicom(path: Path):
    if pydicom is None:
        raise RuntimeError("pydicom is required. Install with `python3 -m pip install pydicom`.")
    return pydicom.dcmread(path, stop_before_pixels=True, force=True)


def instance_metadata(dataset: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for field in METADATA_FIELDS:
        if hasattr(dataset, field):
            metadata[field] = json_value(getattr(dataset, field))
    return metadata


def dicom_files(input_dir: Path) -> list[Path]:
    candidates = [path for path in input_dir.rglob("*") if path.is_file()]
    return sorted(candidates)


def build_manifest(input_dir: Path, url_prefix: str) -> dict[str, Any]:
    studies: dict[str, dict[str, Any]] = {}
    series_instances: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for path in dicom_files(input_dir):
        try:
            dataset = read_dicom(path)
        except Exception as exc:
            print(f"Skipping {path}: {exc}", file=sys.stderr)
            continue

        if not hasattr(dataset, "StudyInstanceUID") or not hasattr(dataset, "SeriesInstanceUID"):
            print(f"Skipping {path}: missing study or series UID", file=sys.stderr)
            continue

        study_uid = str(dataset.StudyInstanceUID)
        series_uid = str(dataset.SeriesInstanceUID)
        relative = path.relative_to(input_dir).as_posix()
        url = f"{url_prefix.rstrip('/')}/{relative}"

        studies.setdefault(
            study_uid,
            {
                "StudyInstanceUID": study_uid,
                "StudyDescription": str(getattr(dataset, "StudyDescription", "Annotated Brain MRI")),
                "StudyDate": str(getattr(dataset, "StudyDate", "")),
                "StudyTime": str(getattr(dataset, "StudyTime", "")),
                "PatientName": str(getattr(dataset, "PatientName", "Anonymous")),
                "PatientId": str(getattr(dataset, "PatientID", "anonymous")),
                "series": {},
            },
        )

        if series_uid not in studies[study_uid]["series"]:
            studies[study_uid]["series"][series_uid] = {
                "SeriesDescription": str(getattr(dataset, "SeriesDescription", "T1 MPRAGE")),
                "SeriesInstanceUID": series_uid,
                "SeriesNumber": json_value(getattr(dataset, "SeriesNumber", 1)),
                "SeriesDate": str(getattr(dataset, "SeriesDate", "")),
                "SeriesTime": str(getattr(dataset, "SeriesTime", "")),
                "Modality": str(getattr(dataset, "Modality", "MR")),
                "instances": [],
            }

        series_instances[(study_uid, series_uid)].append(
            {
                "metadata": instance_metadata(dataset),
                "url": f"dicomjson:{url}",
            }
        )

    for (study_uid, series_uid), instances in series_instances.items():
        instances.sort(key=lambda item: item["metadata"].get("InstanceNumber", 0))
        studies[study_uid]["series"][series_uid]["instances"] = instances

    output_studies = []
    for study in studies.values():
        series = list(study["series"].values())
        series.sort(key=lambda item: item.get("SeriesNumber", 0))
        study["series"] = series
        output_studies.append(study)

    output_studies.sort(key=lambda item: item.get("StudyDate", ""))
    return {"studies": output_studies}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="Directory containing de-identified DICOM files.")
    parser.add_argument("output_json", type=Path, help="Output OHIF dicomjson manifest.")
    parser.add_argument(
        "--url-prefix",
        default="dicom",
        help="URL prefix from the manifest location to the DICOM files. Default: dicom",
    )
    args = parser.parse_args()

    try:
        manifest = build_manifest(args.input_dir, args.url_prefix)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not manifest["studies"]:
        print("ERROR: no readable DICOM instances found", file=sys.stderr)
        return 1

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")

    instance_count = sum(
        len(series["instances"]) for study in manifest["studies"] for series in study["series"]
    )
    print(f"Wrote {args.output_json} with {instance_count} instances")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

