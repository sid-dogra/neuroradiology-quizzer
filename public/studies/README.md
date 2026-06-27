# Public Studies

Only place de-identified, publishable study assets here.

Recommended first NiiVue study layout:

```text
public/studies/nki_a00039636_t1/
  study.json
  t1_display_freesurfer_orig.nii.gz
  annotations/
    001_lateral_ventricle.nii.gz
    002_thalamus.nii.gz
    ...
```

Build or refresh this bundle with:

```bash
python3 scripts/build_public_niivue_study.py
```

Before adding public imaging files:

- Confirm PHI removal.
- Confirm defacing if needed.
- Confirm the study loads locally.
- Confirm public educational use is allowed.
