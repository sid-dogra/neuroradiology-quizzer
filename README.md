# Annotated Brain MRI

Interactive educational brain MRI atlas and quiz project.

This repository is structured around a simple rule: raw imaging and local processing outputs stay private, while publishable viewer assets, anatomy metadata, and documentation are versioned.

## Project Goals

- Host a de-identified volumetric T1 MPRAGE in an interactive web viewer.
- Use atlas-derived labels as a starting point, with manual corrections for teaching-quality anatomy.
- Support quiz modes by difficulty, system, structure, and view.
- Attach high-yield anatomy notes where useful, such as foraminal contents, arterial supply, cranial nerve relationships, or clinical correlations.
- Deploy the public app through GitHub Pages or a similar static host.

## Current State

This repository now includes a working static NIfTI viewer prototype:

- Annotation schema and curated draft structure metadata.
- A generated FreeSurfer label inventory pipeline for building the annotation database.
- A finalized local review bundle under `data/finalized/`.
- A public NiiVue study bundle under `public/studies/nki_a00039636_t1/`.
- A browser viewer in `viewer/` with browse and reveal-style quiz modes.
- Helper scripts for validating annotations, building the NiiVue study bundle, and optionally building an OHIF `dicomjson` manifest from a local DICOM series.

The current public viewer bundle is still a generated review build, not a final
teaching release. The overlay masks need visual QC and manual edits before they
should be considered accepted annotations.

The current candidate source scan is documented in `docs/current-nki-subject.md`.

## Directory Layout

```text
annotations/
  generated/              Machine-generated atlas label inventories
  schema/                 JSON schema for anatomy/quiz metadata
  structures/             Versioned educational labels and quiz targets
data/
  raw/                    Local-only source DICOM/NIfTI inputs
  working/                Local-only FreeSurfer/Slicer/ITK-SNAP work
  processed/              Local-only intermediate exports
docs/                     Workflow, de-identification, and deployment notes
public/
  studies/                Publishable de-identified NIfTI study bundles
scripts/                  Local helper scripts
viewer/                   Static NiiVue viewer with browse and quiz modes
```

## Fast Start

Validate the sample annotations:

```bash
python3 scripts/validate_annotations.py annotations/structures/core-neuroanatomy.sample.json
```

Render a quick QC montage for the current NKI scan:

```bash
python3 scripts/render_nifti_montage.py data/raw/t1_mprage.nii.gz data/processed/t1_mprage_qc_montage.png
```

Run FreeSurfer when ready:

```bash
scripts/run_freesurfer_recon_all.sh --dry-run
scripts/run_freesurfer_recon_all.sh
```

Build the generated FreeSurfer annotation inventory:

```bash
python3 scripts/build_freesurfer_annotation_inventory.py
```

Build or refresh the public NiiVue study bundle:

```bash
python3 scripts/build_public_niivue_study.py
```

Preview the current viewer:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/viewer/
```

## What You Need To Provide Next

The current NKI proof-of-concept scan is already wired through the viewer. The
next project need is annotation review:

- Review generated masks in ITK-SNAP.
- Save accepted or manually corrected masks into `data/finalized/accepted_annotations/`.
- Rebuild the public bundle with `python3 scripts/build_public_niivue_study.py`.

See `docs/data-requirements.md` if switching to a new public scan later.

## Public Data Warning

Do not commit raw clinical DICOM, identifiable NIfTI sidecars, screenshots with overlays containing PHI, or unrevised FreeSurfer subjects. The `.gitignore` is intentionally conservative.
