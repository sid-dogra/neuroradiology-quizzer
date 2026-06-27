# OHIF Integration Plan

OHIF should be treated as the clinical-grade viewport layer. The quiz metadata should remain independent JSON so it can be corrected and expanded without rebuilding segmentations.

## Static Hosting Strategy

OHIF can be built as static assets and hosted on GitHub Pages or another static host. The image data still needs to be web-accessible.

Most likely MVP route:

```text
OHIF static app + dicomjson manifest + public de-identified DICOM files
```

The relevant OHIF route pattern is:

```text
/viewer/dicomjson?url=/studies/demo_t1_mprage/study.json
```

The exact final path may differ depending on the OHIF build and router basename.

## Data Flow

```text
De-identified DICOM series
  -> public/studies/<study-id>/dicom/*.dcm
  -> scripts/build_dicomjson_manifest.py
  -> public/studies/<study-id>/study.json
  -> OHIF dicomjson data source
```

Anatomy metadata remains:

```text
annotations/structures/core-neuroanatomy.sample.json
```

## Quiz Integration

The custom educational mode should:

- Load the annotation JSON.
- Filter structures by difficulty and system.
- Pick a quiz target.
- Tell OHIF to navigate to the target view/slice/coordinate.
- Hide or show labels depending on quiz state.
- Reveal educational notes after the answer.

## Implementation Options

### Option A: OHIF Custom Mode

Best long-term route.

- Native layout control.
- Can coordinate with OHIF services.
- Can manage segmentations and measurements more directly.
- More setup complexity.

### Option B: Static App With OHIF iframe

Best quick prototype route.

- Keep quiz UI outside OHIF.
- Embed OHIF as an iframe.
- Use URL changes or `postMessage` for navigation.
- Less access to internal OHIF services.

### Option C: Non-OHIF Viewer

Fallback route if OHIF customization becomes too heavy.

- Use Niivue or another web neuroimaging viewer.
- Easier NIfTI/labelmap workflows.
- Less radiology-workstation feel.

## Current Recommendation

Start with Option B until the DICOM stack and annotation data are stable. Move to Option A when the basic teaching loop is proven.

## References

- OHIF deployment: https://docs.ohif.org/deployment/
- OHIF static assets: https://docs.ohif.org/deployment/static-assets/
- OHIF configuration: https://docs.ohif.org/configuration/configurationfiles/
- OHIF modes/routes: https://docs.ohif.org/platform/modes/routes/

