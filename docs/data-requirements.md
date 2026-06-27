# Data Requirements

## Preferred Input

Provide one de-identified volumetric T1-weighted brain MRI:

- Sequence: 3D T1 MPRAGE, BRAVO, SPGR, or equivalent.
- Voxel size: isotropic 1.0 mm preferred; 0.8 to 1.2 mm acceptable.
- Coverage: entire brain, skull base, and upper cervical region if foramina/skull base anatomy will be included.
- Format: original DICOM series preferred; NIfTI is also workable.
- Orientation: any orientation is acceptable if geometry metadata is intact.

See `docs/public-data-options.md` for public datasets that may work if you do not want to use a local clinical/research scan.

## Useful Optional Inputs

- FreeSurfer subject directory if already processed.
- SynthSeg output if already available.
- Manual segmentations from Freeview, ITK-SNAP, or 3D Slicer.
- A priority anatomy list for the first quiz release.
- A short note on intended audience: medical students, radiology residents, neurology residents, anatomy learners, or mixed.

## Do Not Provide

- Identifiable clinical DICOM.
- Burned-in screenshots with name, MRN, accession, date of birth, institution, or face.
- Full PACS exports containing unrelated series.
- Clinical reports.

## Initial MVP Anatomy Set

A realistic first public release could include 40 to 80 structures:

- Ventricles and major cisterns.
- Basal ganglia and thalami.
- Internal capsule and major white matter landmarks.
- Corpus callosum and midline structures.
- Brainstem levels and fourth ventricle.
- Hippocampus, amygdala, and medial temporal landmarks.
- Major skull base foramina.
- Major arteries, dural venous sinuses, and cavernous sinus contents.

## File Placement

Put source data here:

```text
data/raw/
```

Suggested local names:

```text
data/raw/t1_mprage_dicom/
data/raw/t1_mprage.nii.gz
```

The raw folder is ignored by Git.
