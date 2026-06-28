# Accepted Annotations

Place manually reviewed, accepted labelmaps here.

The generated sync script does not overwrite this folder. Use the conformed image
for labelmaps copied here:

```text
../source/t1_conformed_freesurfer.nii.gz
```

## Naming

For an existing target, no spreadsheet change is needed. Put the downloaded mask
here and rebuild the public viewer bundle. The builder matches any of these
patterns to the existing target slug:

```text
071_septum_pellucidum.edited.nii.gz
septum_pellucidum.edited.nii.gz
new_septum_pellucidum.edited.nii.gz
```

The `new_...` pattern is what the browser editor downloads when a blank mask is
created in Edit Mode. It is accepted as long as the rest of the filename matches
an existing target id or display-name slug.

For anatomy that is not already in the target database, add it to the curation
workbook/target JSON first so the viewer has a display name, difficulty, and
systems metadata, then place the matching mask here.
