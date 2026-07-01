# ITK-SNAP Export Review

Open the conformed T1 as the main image, then open the auto labelmap as the segmentation.

## Files

- Main image: `data/working/itksnap/t1_conformed.nii.gz`
- Auto segmentation labelmap: `data/working/itksnap/auto_seed_segmentation.nii.gz`
- Blank segmentation labelmap: `data/working/itksnap/blank_segmentation.nii.gz`
- Label table: `data/working/itksnap/labels.tsv`
- ITK-SNAP label description: `data/working/itksnap/itksnap_label_descriptions.txt`
- Candidate point table: `data/working/itksnap/points.tsv`
- Rough support masks directory: `data/working/itksnap/rough_support_masks`
- Full-gyrus masks directory: `data/working/itksnap/full_gyrus_masks`

## Counts

- Total labels in table: 96
- Auto masks included in segmentation: 37
- Per-target rough masks exported: 28
- Full-gyrus composite masks exported: 23
- Fully manual labels: 31
- Auto-mask voxel conflicts skipped: 8910

## Auto-Mask Overlap Notes

These overlaps were skipped in the combined auto labelmap so earlier labels were not overwritten. QC these areas before treating the combined auto segmentation as final.

- Central sulcus: 3223 voxels overlapped existing label(s): Postcentral gyrus, Precentral gyrus
- Marginal sulcus (pars marginalis): 782 voxels overlapped existing label(s): Posterior cingulate gyrus, precuneus
- Angular gyrus: 1728 voxels overlapped existing label(s): Supramarginal gyrus
- Superior temporal gyrus: 210 voxels overlapped existing label(s): Angular gyrus
- Calcarine sulcus: 721 voxels overlapped existing label(s): Lingual gyrus, precuneus
- Parieto-occipital sulcus: 2246 voxels overlapped existing label(s): Cuneus, precuneus, Calcarine sulcus

## Workflow

1. QC `auto_seed_segmentation.nii.gz` first.
2. Use `points.tsv` and `rough_support_masks/` to refine support-anchor targets.
3. Paint fully manual targets using the label values in `labels.tsv`.
4. Save edited segmentation as a new file; do not overwrite the generated export unless intentionally regenerating.

## Fully Manual Targets

- Foramen magnum (`foramen_magnum`)
- Premedullary cistern (`premedullary_cistern`)
- External auditory canal (`external_auditory_canal`)
- Superior orbital fissure (`superior_orbital_fissure`)
- Meckel's cave (`meckel_s_cave`)
- Crista galli (`crista_galli`)
- Pituitary fossa (`pituitary_fossa`)
- Prepontine cistern (`prepontine_cistern`)
- Middle cerebellar peduncle (`middle_cerebellar_peduncle`)
- Nodule of the cerebellum (`nodule_of_the_cerebellum`)
- Suprasellar cistern (`suprasellar_cistern`)
- Tentorium cerebelli (`tentorium_cerebelli`)
- Interpeduncular cistern (`interpeduncular_cistern`)
- Cerebral crus (cerebral peduncle) (`cerebral_crus_cerebral_peduncle`)
- Mammillary body (`mammillary_bodies`)
- Median interhemispheric fissure (`median_interhemispheric_fissure`)
- Ambient cistern (`ambient_cistern`)
- Cerebral aqueduct (`cerebral_aqueduct`)
- Inferior colliculus (`inferior_colliculus`)
- Anterior limb of the internal capsule (`anterior_limb_of_the_internal_capsule`)
- Genu of the internal capsule (`genu_of_the_internal_capsule`)
- Quadrigeminal cistern (`quadrigeminal_cistern`)
- Pineal gland (`pineal_gland`)
- Vermis (`vermis`)
- Column of the fornix (`column_of_the_fornix`)
- Posterior limb of the internal capsule (`posterior_limb_of_the_internal_capsule`)
- Centrum semiovale (`centrum_semiovale`)
- Falx cerebri (`falx_cerebri`)
- Anterior commissure (`anterior_commissure`)
- Posterior commissure (`posterior_commissure`)
- Cisterna magna (`cisterna_magna`)

## Edit/Refine Targets

- Medulla oblongata (`medulla_oblongata`)
- Cerebellar tonsil (`cerebellar_tonsil`)
- Cerebellum (`cerebellum`)
- Foramen of Magendie (`foramen_of_magendie`)
- Foramen of Luschka (`foramen_of_luschka`)
- Pons (`pons`)
- Uncus (`uncus`)
- Temporal horn of the lateral ventricle (`temporal_horn_of_the_lateral_ventricle`)
- Sylvian fissure (`sylvian_fissure`)
- Midbrain (`midbrain`)
- Interventricular foramen (foramen of Monro) (`interventricular_foramen_foramen_of_monro`)
- Genu of the corpus callosum (`genu_of_the_corpus_callosum`)
- Frontal horn of the lateral ventricle (`frontal_horn_of_the_lateral_ventricle`)
- Head of the caudate nucleus (`head_of_the_caudate_nucleus`)
- Lentiform nucleus (`lentiform_nucleus`)
- Cingulate gyrus (`cingulate_gyrus`)
- Septum pellucidum (`septum_pellucidum`)
- Forceps minor (`forceps_minor`)
- Trigone (atrium) of the lateral ventricle (`trigone_atrium_of_the_lateral_ventricle`)
- Occipital lobe (`occipital_lobe`)
- Splenium of the corpus callosum (`splenium_of_the_corpus_callosum`)
- Occipital horn of the lateral ventricle (`occipital_horn_of_the_lateral_ventricle`)
- Body of the lateral ventricle (`body_of_the_lateral_ventricle`)
- Forceps major (`forceps_major`)
- Body of the corpus callosum (`body_of_the_corpus_callosum`)
- Hand bump of the precentral gyrus (`hand_bump_of_the_precentral_gyrus`)
- Orbitofrontal cortex (`orbitofrontal_cortex`)
- Cingulate sulcus (`cingulate_sulcus`)

## Full-Gyrus Composite Masks

- Cuneus (`cuneus`): 3817 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/013_cuneus.nii.gz`
- Entorhinal cortex (`entorhinal_cortex`): 3210 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/014_entorhinal_cortex.nii.gz`
- Fusiform gyrus (`fusiform_gyrus`): 16576 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/015_fusiform_gyrus.nii.gz`
- Lingual gyrus (`lingual_gyrus`): 9058 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/016_lingual_gyrus.nii.gz`
- Pars opercularis (`pars_opercularis`): 7419 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/017_pars_opercularis.nii.gz`
- Pars orbitalis (`pars_orbitalis`): 4127 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/018_pars_orbitalis.nii.gz`
- Pars triangularis (`pars_triangularis`): 6996 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/019_pars_triangularis.nii.gz`
- Postcentral gyrus (`postcentral_gyrus`): 14803 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/020_postcentral_gyrus.nii.gz`
- Posterior cingulate gyrus (`posterior_cingulate_gyrus`): 7380 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/021_posterior_cingulate_gyrus.nii.gz`
- Precentral gyrus (`precentral_gyrus`): 24629 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/022_precentral_gyrus.nii.gz`
- precuneus (`precuneus`): 18044 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/023_precuneus.nii.gz`
- Superior frontal gyrus (`superior_frontal_gyrus`): 41234 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/024_superior_frontal_gyrus.nii.gz`
- Supramarginal gyrus (`supramarginal_gyrus`): 17560 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/025_supramarginal_gyrus.nii.gz`
- Temporal pole (`temporal_pole`): 3672 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/026_temporal_pole.nii.gz`
- Insula (`insular_cortex`): 15182 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/027_insular_cortex.nii.gz`
- Gyrus rectus (`gyrus_rectus`): 2039 voxels, cortical parcel only; no exact WM parcel, `data/working/itksnap/full_gyrus_masks/041_gyrus_rectus.nii.gz`
- Cingulate gyrus (`cingulate_gyrus`): 21368 voxels, 4 WM component(s), `data/working/itksnap/full_gyrus_masks/070_cingulate_gyrus.nii.gz`
- Angular gyrus (`angular_gyrus`): 7079 voxels, cortical parcel only; no exact WM parcel, `data/working/itksnap/full_gyrus_masks/085_angular_gyrus.nii.gz`
- Superior temporal gyrus (`superior_temporal_gyrus`): 16178 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/086_superior_temporal_gyrus.nii.gz`
- Middle temporal gyrus (`middle_temporal_gyrus`): 13743 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/087_middle_temporal_gyrus.nii.gz`
- Inferior temporal gyrus (`inferior_temporal_gyrus`): 18474 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/088_inferior_temporal_gyrus.nii.gz`
- Parahippocampal gyrus (`parahippocampal_gyrus`): 3156 voxels, 1 WM component(s), `data/working/itksnap/full_gyrus_masks/089_parahippocampal_gyrus.nii.gz`
- Orbitofrontal cortex (`orbitofrontal_cortex`): 23476 voxels, 2 WM component(s), `data/working/itksnap/full_gyrus_masks/090_orbitofrontal_cortex.nii.gz`
