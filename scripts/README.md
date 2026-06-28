# Scripts

## Validate Annotations

```bash
python3 scripts/validate_annotations.py annotations/structures/core-neuroanatomy.sample.json
```

This uses only the Python standard library.

## Build FreeSurfer Annotation Inventory

After `recon-all` has completed, generate the machine-readable atlas inventory:

```bash
python3 scripts/build_freesurfer_annotation_inventory.py
```

Default output:

```text
annotations/generated/freesurfer-label-inventory.json
annotations/generated/freesurfer-structure-list.md
```

This uses only the Python standard library. The output is a candidate-label database, not a reviewed teaching set; every entry starts as `needs_qc`.

## Build Public NiiVue Study

After exporting or syncing the finalized review bundle, build the static NIfTI
assets consumed by `viewer/`:

```bash
python3 scripts/build_public_niivue_study.py
```

Default output:

```text
public/studies/nki_a00039636_t1/
  study.json
  t1_display_freesurfer_orig.nii.gz
  annotations/
```

This requires `nibabel`, `numpy`, and `scipy`. Generated-review masks are marked
`needs_review` in the manifest; masks copied from
`data/finalized/accepted_annotations/` are marked `accepted`.

Accepted masks with filenames ending in `.edited.nii.gz` are cleaned during
public export: tiny disconnected islands are removed, enclosed holes are filled
slice-by-slice on axial views, a light Gaussian boundary smooth is applied to
reduce attached edge streaks, then a gentle close/fill is applied to reduce
small editing gaps. Source masks in
`data/finalized/accepted_annotations/` are not modified.

## Build OHIF DicomJson Manifest

After de-identifying and copying a public DICOM series into:

```text
public/studies/demo_t1_mprage/dicom/
```

Run:

```bash
python3 scripts/build_dicomjson_manifest.py \
  public/studies/demo_t1_mprage/dicom \
  public/studies/demo_t1_mprage/study.json \
  --url-prefix dicom
```

This script requires `pydicom`.

```bash
python3 -m pip install pydicom
```

## Render NIfTI QC Montage

```bash
python3 scripts/render_nifti_montage.py \
  data/raw/t1_mprage.nii.gz \
  data/processed/t1_mprage_qc_montage.png
```

This requires `nibabel`, `numpy`, and `Pillow`.
