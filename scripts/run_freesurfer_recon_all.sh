#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FREESURFER_HOME="${FREESURFER_HOME:-/Applications/freesurfer/7.3.2}"
OUTPUT_SUBJECTS_DIR="${SUBJECTS_DIR:-$ROOT_DIR/data/processed/freesurfer_subjects}"
DRY_RUN=0

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

INPUT="${1:-$ROOT_DIR/data/raw/t1_mprage.nii.gz}"
SUBJECT_ID="${2:-annotated_t1_nki_A00039636}"

if [[ ! -f "$INPUT" ]]; then
  echo "Input not found: $INPUT" >&2
  exit 1
fi

if [[ ! -f "$FREESURFER_HOME/SetUpFreeSurfer.sh" ]]; then
  echo "FreeSurfer setup script not found under: $FREESURFER_HOME" >&2
  exit 1
fi

export FREESURFER_HOME
unset SUBJECTS_DIR
set +e +u +o pipefail
source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
fs_setup_status=$?
set -euo pipefail
if [[ "$fs_setup_status" != "0" ]]; then
  echo "FreeSurfer setup failed with status $fs_setup_status" >&2
  exit "$fs_setup_status"
fi
export SUBJECTS_DIR="$OUTPUT_SUBJECTS_DIR"

mkdir -p "$SUBJECTS_DIR"

echo "Input: $INPUT"
echo "Subject: $SUBJECT_ID"
echo "SUBJECTS_DIR: $SUBJECTS_DIR"
echo
echo "Command:"
echo "recon-all -sd \"$SUBJECTS_DIR\" -i \"$INPUT\" -s \"$SUBJECT_ID\" -all"

if [[ "$DRY_RUN" == "1" ]]; then
  exit 0
fi

echo
echo "This can take several hours."

recon-all -sd "$SUBJECTS_DIR" -i "$INPUT" -s "$SUBJECT_ID" -all
