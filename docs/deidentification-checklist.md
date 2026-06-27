# De-identification Checklist

This project is intended for public educational hosting. Treat the scan as public before anything enters `public/`.

## Before Processing

- Confirm the scan can be used for public educational work.
- Remove direct identifiers from DICOM headers.
- Remove or replace dates if they are not needed.
- Remove institution, station, operator, accession, and patient comments.
- Inspect for burned-in annotations.
- Deface the T1 volume if the face is visible or reconstructable.

## DICOM Tags To Review

At minimum, review:

- PatientName
- PatientID
- PatientBirthDate
- PatientSex
- PatientAge
- AccessionNumber
- StudyDate
- SeriesDate
- AcquisitionDate
- ContentDate
- StudyTime
- SeriesTime
- InstitutionName
- InstitutionAddress
- ReferringPhysicianName
- PerformingPhysicianName
- OperatorsName
- PatientComments
- StudyDescription
- SeriesDescription
- ProtocolName

Descriptions and protocol names are often useful educationally, but they should not include site-specific or patient-specific identifiers.

## Geometry Safety

When de-identifying, preserve:

- Pixel data.
- Pixel spacing.
- Slice thickness.
- Image orientation.
- Image position.
- Frame of reference UID consistency.
- Series and SOP instance relationships.

The viewer and segmentation overlays depend on geometry remaining coherent.

## Public Export Rule

Only copy files to `public/studies/` after:

- PHI review is complete.
- The image has been defaced if needed.
- The anatomy labels have been reviewed.
- The public manifest loads locally.

