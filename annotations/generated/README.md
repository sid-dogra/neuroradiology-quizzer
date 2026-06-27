# Generated Annotation Inventories

This directory holds machine-generated metadata derived from local atlas/segmentation outputs.

The generated files are not the final teaching database. Treat them as an inventory of candidate labels that the curated quiz/content layer can reference.

## Current Generator

```bash
python3 scripts/build_freesurfer_annotation_inventory.py
```

Default output:

```text
annotations/generated/freesurfer-label-inventory.json
annotations/generated/freesurfer-structure-list.md
```

The inventory includes:

- FreeSurfer atlas/source paths.
- Label names, values, colors, laterality, and available subject-specific stats.
- Suggested systems and difficulty levels.
- A first-pass `includeSuggested` flag that favors left-sided and midline structures.
- `needs_qc` status for every label.

## Curation Rule

Use this generated file to decide which labels should become human-reviewed entries in `annotations/structures/`. For bilateral anatomy, prefer the left label first and leave the right side available as the unlabeled comparison side unless the anatomy lesson needs bilateral context.
