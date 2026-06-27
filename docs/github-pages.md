# GitHub Pages Deployment

The current scaffold can be served as static files.

## Static NiiVue Preview

If the repository is published with GitHub Pages from the repository root, the
viewer should be reachable at:

```text
https://<username>.github.io/<repo>/viewer/
```

The `.nojekyll` file is included so GitHub Pages serves all static assets directly.

## Public Study Layout

The current viewer expects a static NIfTI study bundle:

```text
public/studies/nki_a00039636_t1/
  study.json
  t1_display_freesurfer_orig.nii.gz
  annotations/
    001_lateral_ventricle.nii.gz
    002_thalamus.nii.gz
    ...
```

Refresh the bundle with:

```bash
python3 scripts/build_public_niivue_study.py
```

Large imaging files may eventually be better hosted outside the repository, for
example GitHub Releases, Cloudflare R2, S3, or another static object store with
CORS enabled.

## Local Smoke Test

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/viewer/
```

## Possible Future OHIF Build

OHIF remains useful if the project later needs a DICOM/SEG or DICOMweb release.
If OHIF is added, use a build process that outputs static assets. The app can either:

- Live under `viewer/ohif/` as a compiled OHIF bundle.
- Live as a separate GitHub Pages deployment while this repository hosts annotation and study data.
- Be embedded by the custom quiz shell with an iframe or route-level integration.
