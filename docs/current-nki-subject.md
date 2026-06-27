# Current NKI Subject

This project is currently using an NKI Rockland Sample baseline T1w scan as the candidate anatomical base.

## Source

Dataset:

```text
NKI Rockland Sample / RawDataBIDSLatest
```

Subject/session:

```text
sub-A00039636 / ses-BAS1
```

Downloaded local files:

```text
data/raw/t1_mprage.nii.gz
data/raw/t1_mprage.json
```

Source URLs:

```text
https://s3.amazonaws.com/fcp-indi/data/Projects/RocklandSample/RawDataBIDSLatest/sub-A00039636/ses-BAS1/anat/sub-A00039636_ses-BAS1_T1w.nii.gz
https://s3.amazonaws.com/fcp-indi/data/Projects/RocklandSample/RawDataBIDSLatest/sub-A00039636/ses-BAS1/anat/sub-A00039636_ses-BAS1_T1w.json
```

## Sequence Metadata

From the BIDS sidecar:

```text
Manufacturer: Siemens
Model: TrioTim
Field strength: 3T
SeriesDescription: MPRAGE_SIEMENS
ProtocolName: MPRAGE_SIEMENS
SequenceName: tfl3d1_ns
ScanningSequence: GR_IR
SequenceVariant: SP_MP_OSP
TR: 1.9 s
TE: 0.00252 s
TI: 0.9 s
Flip angle: 9 degrees
```

## Local QC

Generated montage:

```text
data/processed/t1_mprage_qc_montage.png
```

Header summary:

```text
dimensions: 176 x 256 x 256
voxel sizes: 1.000000 x 0.976562 x 0.976562 mm
orientation: LAS
primary slice direction: axial
```

The quick visual montage shows better proof-of-concept anatomy than the original trial T1, though the scan still needs full visual review in Freeview, 3D Slicer, or ITK-SNAP before committing to it as the public atlas base.

The montage renderer reorients images by affine before display, so these PNGs are intended as radiology-oriented quick QC snapshots rather than raw voxel-axis views.

## FreeSurfer

FreeSurfer is installed locally at:

```text
/Applications/freesurfer/7.3.2
```

Run:

```bash
scripts/run_freesurfer_recon_all.sh --dry-run
scripts/run_freesurfer_recon_all.sh
```

Default output:

```text
data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/
```

Completed run:

```text
Started: 2026-06-20 20:51:09 EDT
Ended:   2026-06-20 23:57:28 EDT
Runtime: 3.105 hours
Status:  finished without error
```

FreeSurfer conformed T1:

```text
dimensions: 256 x 256 x 256
voxel sizes: 1.000000 x 1.000000 x 1.000000 mm
orientation: LIA
```

Key generated volumes:

```text
mri/aseg.mgz
mri/aparc+aseg.mgz
mri/aparc.a2009s+aseg.mgz
mri/aparc.DKTatlas+aseg.mgz
mri/wmparc.mgz
mri/ribbon.mgz
```

Key generated left-hemisphere annotation layers:

```text
label/lh.aparc.annot
label/lh.aparc.a2009s.annot
label/lh.aparc.DKTatlas.annot
label/lh.BA_exvivo.annot
label/lh.BA_exvivo.thresh.annot
label/lh.mpm.vpnl.annot
```

Post-run QC montages:

```text
data/processed/freesurfer_T1_montage.png
data/processed/freesurfer_aseg_montage.png
data/processed/freesurfer_aparc_aseg_montage.png
```

QC note:

```text
The run completed successfully. Topology correction finished with genus 0 for
both hemispheres. Sphere generation/registration still reported one residual
negative triangle on the final sphere/sphere.reg outputs, and pial placement had
many local sigma increases during the fine passes. Treat cortical/pial boundaries
as a required QC item, especially for surface-derived cortical labels.
```

Generated annotation review files:

```text
annotations/generated/freesurfer-label-inventory.json
annotations/generated/freesurfer-structure-list.md
annotations/curation/target-crosswalk.json
annotations/curation/target-review.md
annotations/localization/t1-localization-queue.json
annotations/localization/t1-localization-review.md
annotations/localization/itksnap-export-manifest.json
annotations/localization/itksnap-export-review.md
```

ITK-SNAP working set:

```text
data/working/itksnap/t1_conformed.nii.gz
data/working/itksnap/auto_seed_segmentation.nii.gz
data/working/itksnap/blank_segmentation.nii.gz
data/working/itksnap/labels.tsv
data/working/itksnap/points.tsv
data/working/itksnap/itksnap_label_descriptions.txt
data/working/itksnap/rough_support_masks/
data/working/itksnap/full_gyrus_masks/
```
