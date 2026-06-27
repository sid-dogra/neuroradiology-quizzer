# T1 Localization Review

Generated candidate localization points in FreeSurfer conformed T1 space.

## Summary

- Active T1 targets: 96
- Auto FreeSurfer points to QC: 37
- Support anchors that need editing/refinement: 28
- Fully manual placements needed: 31

## What You Need To Do

1. QC the auto FreeSurfer points. These should usually be close, but can still be moved for better teaching.
2. Edit or replace the support anchors. These are intentionally rough because the desired teaching structure is smaller, broader, or composite.
3. Fully place the manual-required structures yourself or with a future external atlas.

## Auto Points To QC

| Target | Strategy | Candidate point | Notes |
|---|---|---|---|
| Lateral Ventricle | `freesurfer_seed` | 140,84,116 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Thalamus | `freesurfer_seed` | 138,97,112 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Good stock label candidate. |
| Caudate | `freesurfer_seed` | 140,90,139 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Putamen | `freesurfer_seed` | 152,100,130 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Globus pallidus | `freesurfer_seed` | 146,101,127 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Third ventricle | `freesurfer_seed` | 128,104,123 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Good stock label candidate. |
| Fourth ventricle | `freesurfer_seed` | 127,135,93 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Good stock label candidate. |
| Hippocampus | `freesurfer_seed` | 150,113,110 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Amygdala | `freesurfer_seed` | 148,116,129 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Nucleus accumbens | `freesurfer_seed` | 135,104,142 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Choroid plexus | `freesurfer_seed` | 147,95,96 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Good stock label candidate, with QC. |
| Optic chiasm | `freesurfer_seed` | 127,114,137 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` |  |
| Cuneus | `freesurfer_seed` | 132,98,46 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Entorhinal cortex | `freesurfer_seed` | 150,129,131 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Fusiform gyrus | `freesurfer_seed` | 156,123,94 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Lingual gyrus | `freesurfer_seed` | 137,110,69 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Pars opercularis | `freesurfer_seed` | 172,86,138 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Pars orbitalis | `freesurfer_seed` | 167,107,163 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Pars triangularis | `freesurfer_seed` | 172,93,154 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Postcentral gyrus | `freesurfer_seed` | 169,65,100 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Posterior cingulate gyrus | `freesurfer_seed` | 134,72,106 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Precentral gyrus | `freesurfer_seed` | 165,66,114 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| precuneus | `freesurfer_seed` | 135,79,70 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Superior frontal gyrus | `freesurfer_seed` | 137,60,149 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Supramarginal gyrus | `freesurfer_seed` | 177,76,91 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` |  |
| Temporal pole | `freesurfer_seed` | 155,130,150 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Rename from atlas display name and hide laterality in viewer. |
| Insular cortex | `freesurfer_seed` | 164,102,132 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Good cortical target; use learner-facing name. |
| Gyrus rectus | `freesurfer_seed` | 131,111,172 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | Destrieux provides an explicit gyrus rectus label. |
| Central sulcus | `freesurfer_seed` | 162,66,105 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | Excellent landmark; Destrieux explicit sulcal label. |
| Marginal sulcus (pars marginalis) | `freesurfer_seed` | 140,70,89 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | Useful for paracentral lobule/cingulate anatomy. |
| Angular gyrus | `freesurfer_seed` | 171,78,65 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | High-yield parietal language/network landmark; pair with supramarginal gyrus. |
| Superior temporal gyrus | `freesurfer_seed` | 177,108,125 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Common temporal lobe landmark along the Sylvian fissure. |
| Middle temporal gyrus | `freesurfer_seed` | 182,113,106 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Common temporal lobe landmark. |
| Inferior temporal gyrus | `freesurfer_seed` | 175,124,103 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Useful inferior temporal landmark. |
| Parahippocampal gyrus | `freesurfer_seed` | 149,118,103 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Important medial temporal landmark adjacent to hippocampus and uncus. |
| Calcarine sulcus | `freesurfer_seed` | 140,103,70 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | High-yield visual cortex landmark on sagittal/axial views. |
| Parieto-occipital sulcus | `freesurfer_seed` | 140,92,61 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | Useful midline sagittal landmark separating parietal and occipital lobes. |

## Need Edit Or Refinement

| Target | Strategy | Candidate point | Notes |
|---|---|---|---|
| Medulla oblongata | `manual_or_external_atlas` | 127,131,106 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | FreeSurfer has only a coarse brainstem label in this run. |
| Cerebellar tonsil | `manual` | 151,136,78 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Stock FreeSurfer cerebellum label is too coarse for tonsil. |
| Cerebellum | `freesurfer_support_manual_refine` | 149,137,79 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Rename learner-facing label to Cerebellum or Cerebellar hemisphere. |
| Foramen of Magendie | `manual` | 127,135,93 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Small fourth ventricular outlet; manual point target. |
| Foramen of Luschka | `manual` | 127,135,93 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Small lateral fourth ventricular outlet. |
| Pons | `manual_or_external_atlas` | 127,131,106 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Split manually from coarse brainstem label. |
| Uncus | `manual` | 148,116,129 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Use nearby labels only as orientation support. |
| Temporal horn of the lateral ventricle | `freesurfer_support_manual_refine` | 140,84,116 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | FreeSurfer inferior lateral ventricle is a useful seed, but refine teaching target. |
| Sylvian fissure | `manual` | 165,91,110 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | Destrieux fissure components can support, but a simple manual target may teach better. |
| Midbrain | `manual_or_external_atlas` | 127,131,106 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Split manually from coarse brainstem label. |
| Interventricular foramen (foramen of Monro) | `manual` | 136,85,120 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Small communication between lateral and third ventricles. |
| Genu of the corpus callosum | `freesurfer_support_manual_refine` | 128,92,153 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Rename FreeSurfer corpus callosum segment into standard anatomy. |
| Frontal horn of the lateral ventricle | `freesurfer_support_manual_refine` | 140,84,116 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Use whole lateral ventricle label as support, but target frontal horn manually. |
| Head of the caudate nucleus | `freesurfer_support_manual_refine` | 140,90,139 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | FreeSurfer labels whole caudate; teach head with manual target. |
| Lentiform nucleus | `freesurfer_support_manual_refine` | 150,100,129 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Composite teaching structure from putamen and globus pallidus. |
| Cingulate gyrus | `freesurfer_support_manual_refine` | 131,77,119 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | May be cleaner as anterior/posterior cingulate or one broader teaching target. |
| Septum pellucidum | `manual` | 131,85,117 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Thin membrane between frontal horns. |
| Forceps minor | `manual_or_external_atlas` | 128,92,153 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Callosal frontal radiation; consider tract atlas. |
| Trigone (atrium) of the lateral ventricle | `freesurfer_support_manual_refine` | 140,84,116 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Manual target within lateral ventricle label. |
| Occipital lobe | `freesurfer_support_manual_refine` | 146,115,56 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Can be a broad teaching region rather than exact atlas parcel. |
| Splenium of the corpus callosum | `freesurfer_support_manual_refine` | 127,92,97 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Rename FreeSurfer posterior corpus callosum segment. |
| Occipital horn of the lateral ventricle | `freesurfer_support_manual_refine` | 140,84,116 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Manual target within lateral ventricle label. |
| Body of the lateral ventricle | `freesurfer_support_manual_refine` | 140,84,116 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Manual target within lateral ventricle label. |
| Forceps major | `manual_or_external_atlas` | 127,92,97 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Callosal occipital radiation; consider tract atlas. |
| Body of the corpus callosum | `freesurfer_support_manual_refine` | 128,84,127 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aseg.mgz` | Composite/renamed FreeSurfer corpus callosum segment. |
| Hand bump of the precentral gyrus | `manual` | 165,66,114 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Manual point/region within precentral gyrus. |
| Orbitofrontal cortex | `freesurfer_support_manual_refine` | 150,111,162 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc+aseg.mgz` | Learner-facing broad region; may be represented by medial/lateral orbitofrontal parcels. |
| Cingulate sulcus | `freesurfer_support_manual_refine` | 134,76,143 in `data/processed/freesurfer_subjects/annotated_t1_nki_A00039636/mri/aparc.a2009s+aseg.mgz` | Useful for cingulate/paracentral region orientation; may need manual target. |

## Need Full Manual Placement

| Target | Strategy | Candidate point | Notes |
|---|---|---|---|
| Foramen magnum | `manual` | none | Large skull-base landmark; manual point or contour. |
| Premedullary cistern | `manual` | none | CSF space anterior to medulla. |
| External auditory canal | `manual` | none | Bony landmark, better on CT but usually localizable. |
| Superior orbital fissure | `manual` | none | High-yield foraminal anatomy; add contents later. |
| Meckel's cave | `manual` | none | Trigeminal cistern; may be visible on T1 but needs QC. |
| Crista galli | `manual` | none | Anterior midline skull-base landmark. |
| Pituitary fossa | `manual` | none | Sella turcica region; useful midline landmark. |
| Prepontine cistern | `manual` | none | CSF space anterior to pons; basilar artery relationship. |
| Middle cerebellar peduncle | `manual_or_external_atlas` | none | High-yield fiber tract landmark, not a stock FreeSurfer label here. |
| Nodule of the cerebellum | `manual_or_external_atlas` | none | Small vermian structure; manual or specialized atlas. |
| Suprasellar cistern | `manual` | none | Good midline CSF landmark around optic chiasm/pituitary stalk. |
| Tentorium cerebelli | `manual` | none | Dural reflection; visible as boundary rather than segmented tissue. |
| Interpeduncular cistern | `manual` | none | CSF space between cerebral peduncles. |
| Cerebral crus (cerebral peduncle) | `manual_or_external_atlas` | none | Use midbrain-level manual target. |
| Mammillary bodies | `manual` | none | Small hypothalamic structures. |
| Median interhemispheric fissure | `manual` | none | Useful orientation landmark. |
| Ambient cistern | `manual` | none | Cistern lateral to midbrain. |
| Cerebral aqueduct | `manual` | none | High-yield small CSF channel between third and fourth ventricles. |
| Inferior colliculus | `manual_or_external_atlas` | none | Small dorsal midbrain structure. |
| Anterior limb of the internal capsule | `manual_or_external_atlas` | none | High-yield white matter structure not directly labeled by current FreeSurfer outputs. |
| Genu of the internal capsule | `manual_or_external_atlas` | none | Manual target between anterior and posterior limbs. |
| Quadrigeminal cistern | `manual` | none | Posterior to midbrain tectum. |
| Pineal gland | `manual` | none | Small midline gland posterior to third ventricle. |
| Vermis | `manual_or_external_atlas` | none | Vermis is not separated in current FreeSurfer outputs. |
| Column of the fornix | `manual_or_external_atlas` | none | Small limbic white matter structure. |
| Posterior limb of the internal capsule | `manual_or_external_atlas` | none | High-yield motor pathway landmark. |
| Centrum semiovale | `manual_or_external_atlas` | none | Broad white matter region; manual target may teach better than FreeSurfer white matter parcellation. |
| Falx cerebri | `manual` | none | Midline dural reflection; visible as boundary rather than segmented tissue. |
| Anterior commissure | `manual` | none | Classic small midline landmark; useful with AC-PC plane concepts. |
| Posterior commissure | `manual` | none | Small midline landmark near pineal/aqueduct region. |
| Cisterna magna | `manual` | none | Common posterior fossa CSF landmark inferior to the cerebellum. |

