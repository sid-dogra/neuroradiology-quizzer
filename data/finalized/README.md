# Finalized Review Bundle

This folder is the review-friendly handoff area for the current annotated T1 project and the source of truth for the public viewer build.

## Open In ITK-SNAP

Use this pair for reviewing the current generated candidate annotations:

```text
source/t1_conformed_freesurfer.nii.gz
generated_review/candidate_auto_seed_segmentation.nii.gz
```

The raw original T1 MPRAGE is also copied here:

```text
source/t1_mprage_original.nii.gz
source/t1_mprage_original.json
```

## Folder Meaning

- `source/`: original T1 MPRAGE plus FreeSurfer-conformed T1 used by the labelmaps.
- `curation/`: human-editable target JSON and curation spreadsheets. The sync script does not overwrite this folder.
- `generated_review/`: generated candidate annotations and review tables. Only regenerate this folder when you intentionally want to bring candidates over from `data/working/`.
- `accepted_annotations/`: put manually reviewed, accepted labelmaps here. The sync script does not overwrite this folder.

The generated labelmaps are review candidates, not manually accepted final labels yet.
