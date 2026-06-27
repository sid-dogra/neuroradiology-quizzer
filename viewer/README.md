# Viewer

This folder contains the static browser viewer for Neuroradiology Quizzer.
It uses NiiVue in the browser to load a T1 `.nii.gz` and per-structure `.nii.gz`
annotation overlays from `public/studies/`.

## Run Locally

From the repository root:

```bash
python3 -m http.server 8000
```

Open:

```text
http://localhost:8000/viewer/
```

The default study manifest is:

```text
public/studies/nki_a00039636_t1/study.json
```

The viewer loads NiiVue from jsDelivr at runtime, so the first page load needs
internet access even though the T1 and annotation masks are local/static files.

## Rebuild The Public Study Bundle

After regenerating or accepting annotations:

```bash
python3 scripts/build_public_niivue_study.py
```

The script writes:

```text
public/studies/nki_a00039636_t1/
  study.json
  t1_display_freesurfer_orig.nii.gz
  annotations/
    001_lateral_ventricle.nii.gz
    ...
```

## Load A Different Study

Use the `study` query parameter:

```text
http://localhost:8000/viewer/?study=../public/studies/nki_a00039636_t1/study.json
```

## Current Modes

- Browse: filter structures and toggle overlays on the T1.
- Quiz: show one randomly ordered overlay at a time, then reveal the answer and notes.
- Level: beginner includes first-pass resident anatomy; advanced includes the remaining intermediate/advanced targets.
- Plane: axial, sagittal, and coronal single-plane views; axial is the default.

Quiz targets jump to the slice with the largest cross-section for the active
plane when `overlay.bestSlices` is present in the study manifest.

## Data Notes

The viewer currently uses a NIfTI export of FreeSurfer `orig.mgz` because it has
more raw-MPRAGE-like contrast while remaining in the same conformed grid as the
generated masks. The original scanner-space MPRAGE remains in
`data/finalized/source/` for provenance, but labels should be resampled before
using it directly as the viewer base image.
