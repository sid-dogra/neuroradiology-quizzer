# T1 Localization Working Files

This directory holds generated worklists for placing annotation targets in the current T1/FreeSurfer space.

Coordinate space for the current generated files:

```text
data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/T1.mgz
```

The voxel coordinates are FreeSurfer conformed voxel indices. The world coordinates are the affine-derived coordinates from that MGZ space. These are working coordinates for QC and annotation, not final web viewer coordinates.

Use the generated review file to decide:

- which automatically generated FreeSurfer points are acceptable,
- which candidate support points need to be moved/refined, and
- which structures need a fully manual point or ROI.

For gyral/cortical teaching targets, the ITK-SNAP export also writes generated
full-gyrus masks to:

```text
data/working/itksnap/full_gyrus_masks/
```

When an exact `wmparc` partner exists, these masks combine the cortical
parcellation with the corresponding gyral white matter. Destrieux-only labels
without exact `wmparc` partners remain cortical-only.
