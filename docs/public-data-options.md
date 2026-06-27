# Public T1 MRI Data Options

This project needs a high-quality 3D T1-weighted scan that can be processed with FreeSurfer and used as the anatomical base for the viewer.

## Short Recommendation

Start with the NKI Rockland Sample or HCP Young Adult:

- Use **NKI Rockland Sample** if you want quick, public, BIDS-style NIfTI access with a 1 mm MPRAGE-like acquisition.
- Use **HCP Young Adult** if you want the highest structural image quality, but review the HCP data-use terms carefully before rehosting anything.

For a public GitHub Pages atlas, a dataset with permissive reuse and clear de-identification is more important than squeezing out the last bit of acquisition quality.

## Option 1: NKI Rockland Sample

Good default candidate.

Pros:

- Public S3 bucket.
- Raw data are organized in BIDS format.
- Anatomical scan is MPRAGE.
- Protocol documentation lists MPRAGE at 1 mm isotropic.
- Neuroimaging release includes limited phenotyping only.

Things to watch:

- Current Rockland docs say DICOM is not included in the latest BIDS S3 release; use NIfTI.
- Defacing/anonymization can affect some FreeSurfer steps, so inspect outputs.
- Pick one high-quality adult subject after visual review.

Useful paths:

```text
s3://fcp-indi/data/Projects/RocklandSample/RawDataBIDSLatest
```

Example baseline T1w candidate found in the public file list:

```text
sub-A00039636/ses-BAS1/anat/sub-A00039636_ses-BAS1_T1w.nii.gz
```

Example sidecar metadata checked locally:

```json
{
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "TrioTim",
  "SeriesDescription": "MPRAGE_SIEMENS",
  "ProtocolName": "MPRAGE_SIEMENS",
  "MagneticFieldStrength": 3,
  "EchoTime": 0.00252,
  "RepetitionTime": 1.9,
  "InversionTime": 0.9
}
```

Local header check for that example NIfTI:

```text
dimensions: 176 x 256 x 256
voxel size: 1.0000005 x 0.9765625 x 0.9765625 mm
```

Sources:

- Rockland access page: https://rocklandsample.org/accessing-the-neuroimaging-data-releases
- NKI-RS MRI protocol: https://fcon_1000.projects.nitrc.org/indi/enhanced/mri_protocol.html

## Option 2: Human Connectome Project Young Adult

Best image quality candidate.

Pros:

- 3T structural scans are very high resolution.
- HCP protocol uses 0.7 mm isotropic T1w MPRAGE.
- Strong fit for FreeSurfer/HCP-style structural processing.
- Excellent for cortical and deep anatomy.

Things to watch:

- Requires ConnectomeDB/BALSA account and acceptance of HCP data-use terms.
- HCP open-access data are not simply public-domain images for arbitrary redistribution.
- If using it for a public GitHub Pages project, review whether you can rehost derived DICOM/NIfTI assets.

Sources:

- HCP Young Adult data releases: https://www.humanconnectome.org/study/hcp-young-adult/data-releases
- HCP S1200 release: https://www.humanconnectome.org/study/hcp-young-adult/document/1200-subjects-data-release
- HCP scan protocol appendix: https://www.humanconnectome.org/storage/app/media/documentation/s1200/HCP_S1200_Release_Appendix_I.pdf
- HCP data-use terms: https://www.humanconnectome.org/study/hcp-young-adult/data-use-terms

## Option 3: OASIS-1 / OASIS-3

Good FreeSurfer/aging-neuroimaging candidate.

Pros:

- OASIS-1 has direct raw downloads and FreeSurfer downloads.
- OASIS-1 includes averaged processed images resampled to 1 mm isotropic voxels.
- OASIS-3 includes many MR sessions and many sessions with FreeSurfer-derived volumetric segmentation files.

Things to watch:

- OASIS-1 individual raw scans are 1 x 1 x 1.25 mm, while the averaged processed images are 1 mm isotropic.
- OASIS-3/OASIS-4 have stricter access and data-use terms.
- The cohort skews toward aging and Alzheimer disease research, which may or may not be ideal for a generic anatomy atlas.

Sources:

- OASIS homepage and terms: https://sites.wustl.edu/oasisbrains/
- OASIS-1: https://sites.wustl.edu/oasisbrains/home/oasis-1/
- OASIS-1 fact sheet: https://sites.wustl.edu/oasisbrains/files/2024/03/oasis_cross-sectional_facts-bcc7a002dfb104f4.pdf
- OASIS-3: https://sites.wustl.edu/oasisbrains/home/oasis-3/

## Option 4: IXI Dataset

Permissive-license fallback.

Pros:

- Nearly 600 normal healthy subjects.
- T1 images are downloadable in NIfTI format.
- Data are available under CC BY-SA 3.0.
- No application workflow needed.

Things to watch:

- Not all acquisitions are ideal 1 mm isotropic MPRAGE.
- Multi-site scanner variation.
- Need visual QC and probably defacing/reuse review before public hosting.

Sources:

- IXI dataset: https://brain-development.org/ixi-dataset/
- IXI 3T scanner parameters: https://brain-development.org/scanner-philips-medical-systems-intera-3t/

## Practical Selection Rule

Pick one subject with:

- Adult anatomy without major pathology.
- Full brain and skull base coverage.
- Minimal motion.
- Good gray-white contrast.
- No residual facial identifiability if public hosting is planned.
- Clear reuse terms.

Then run:

```bash
recon-all -i data/raw/t1_mprage.nii.gz -s annotated_t1 -all
```

FreeSurfer accepts both a single DICOM file from a T1 series and a single NIfTI file as input.
