# Local Processing Workflow

This is the intended local workflow once the T1 MPRAGE is available.

## 1. Place Input Data

Use either DICOM:

```text
data/raw/t1_mprage_dicom/
```

Or NIfTI:

```text
data/raw/t1_mprage.nii.gz
```

## 2. De-identify And Deface

Recommended options:

- Use `dcm2niix` for DICOM to NIfTI conversion.
- Use `pydeface`, FreeSurfer `mri_deface`, or equivalent for face removal.
- Keep a private record of the exact commands used in `data/working/processing-notes.md`.

Do not commit private processing notes if they contain source paths or clinical identifiers.

## 3. Run FreeSurfer Or SynthSeg

For a standard FreeSurfer subject from NIfTI:

```bash
recon-all -i data/raw/t1_mprage.nii.gz -s annotated_t1 -all
```

For DICOM input, FreeSurfer can accept one file from the T1 series:

```bash
recon-all -i data/raw/t1_mprage_dicom/IM0001.dcm -s annotated_t1 -all
```

Expected useful outputs:

```text
subjects/annotated_t1/mri/orig.mgz
subjects/annotated_t1/mri/brain.mgz
subjects/annotated_t1/mri/aseg.mgz
subjects/annotated_t1/mri/aparc+aseg.mgz
subjects/annotated_t1/surf/
subjects/annotated_t1/label/
```

## 4. Manual Review

Review atlas labels in Freeview, 3D Slicer, or ITK-SNAP.

Focus especially on:

- Skull base foramina.
- Brainstem subdivisions.
- Cranial nerve/cisternal anatomy.
- Hypothalamic and basal forebrain landmarks.
- Cavernous sinus and parasellar anatomy.
- Fine white matter landmarks.
- Any structure where atlas labels are coarse or absent.

## 5. Export Web Assets

For OHIF, the practical target is:

```text
public/studies/demo_t1_mprage/
  dicom/
    *.dcm
  study.json
  labels.dcm
```

Where:

- `dicom/` contains the de-identified T1 DICOM series.
- `study.json` is the OHIF `dicomjson` manifest.
- `labels.dcm` is a DICOM SEG if this route works cleanly.

If DICOM SEG becomes a bottleneck, use a custom labelmap export for the quiz overlay while keeping the underlying image display in OHIF.

## 6. Local QA

- Load the public DICOM series locally.
- Confirm no PHI in headers.
- Confirm axial, coronal, and sagittal views are correctly oriented.
- Confirm segmentations align with anatomy.
- Validate `annotations/structures/*.json`.
- Try the quiz preview with beginner, intermediate, and advanced filters.

