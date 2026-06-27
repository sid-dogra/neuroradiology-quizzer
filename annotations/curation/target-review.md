# Target Review

Generated from the workbook `Target` tab plus the FreeSurfer and curation inventories.

## Summary

- Workbook targets: 109
- Active T1 anatomy targets: 96
- Deferred separate-study targets: 13
- FreeSurfer exact/seed matches: 65
- Curation/manual matches: 75
- Manual localization needed: 59
- T1 visibility QC needed: 0
- Needs manual refinement from an atlas/support label: 15
- Unmatched targets: 0

## What To Review First

1. Confirm the learner-facing names, especially where FreeSurfer names were converted into standard anatomy terms.
2. Confirm whether skull-base, cisternal, and small manual targets are localizable enough on the current T1 to keep.
3. Confirm composite structures that use FreeSurfer only as rough support, such as ventricle subregions, corpus callosum parts, lentiform nucleus, and internal capsule parts.
4. Decide whether advanced small structures should remain in the first release or wait for a later module.

## Deferred To Separate Study

- Vertebral artery | target: `Vertebral artery` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Internal jugular vein | target: `Internal jugular vein` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Basilar artery | target: `Basilar artery` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Sigmoid sinus | target: `Sigmoid sinus` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Petrous internal carotid artery in the carotid canal | target: `Petrous internal carotid artery in the carotid canal` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Cavernous ICA in the cavernous sinus | target: `Cavernous ICA in the cavernous sinus` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- MCA M1 segment | target: `MCA M1 segment` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Torcula herophili (confluence of sinuses) | target: `Torcula herophili (confluence of sinuses)` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Transverse sinus | target: `Transverse sinus` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Internal cerebral vein | target: `Internal cerebral vein` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Straight sinus | target: `Straight sinus` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Inferior sagittal sinus | target: `Inferior sagittal sinus` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.
- Superior sagittal sinus | target: `Superior sagittal sinus` | deferred study: `vascular_and_venous_sinuses` | reason: Save vessels and venous sinuses for a separate study/module rather than the first T1 anatomy annotation pass.

## Unmatched

- None

## Needs Manual Localization

- Foramen magnum | target: `Foramen magnum` | strategy: `manual` | note: Large skull-base landmark; manual point or contour.
- Medulla oblongata | target: `Medulla oblongata` | strategy: `manual_or_external_atlas` | support: aseg:Brain-Stem | note: FreeSurfer has only a coarse brainstem label in this run.
- Cerebellar tonsil | target: `Cerebellar tonsil` | strategy: `manual` | support: aseg:Left-Cerebellum-Cortex | note: Stock FreeSurfer cerebellum label is too coarse for tonsil.
- Premedullary cistern | target: `Premedullary cistern` | strategy: `manual` | note: CSF space anterior to medulla.
- Cerebellum | target: `Cerebellum` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Cerebellum-Cortex; aseg:Left-Cerebellum-White-Matter | note: Rename learner-facing label to Cerebellum or Cerebellar hemisphere.
- External auditory canal | target: `External auditory canal` | strategy: `manual` | note: Bony landmark, better on CT but usually localizable.
- Foramen of Magendie | target: `Foramen of Magendie` | strategy: `manual` | support: aseg:4th-Ventricle | note: Small fourth ventricular outlet; manual point target.
- Superior orbital fissure | target: `Superior orbital fissure` | strategy: `manual` | note: High-yield foraminal anatomy; add contents later.
- Meckel's cave | target: `Meckel's cave` | strategy: `manual` | note: Trigeminal cistern; may be visible on T1 but needs QC.
- Foramen of Luschka | target: `Foramen of Luschka` | strategy: `manual` | support: aseg:4th-Ventricle | note: Small lateral fourth ventricular outlet.
- Crista galli | target: `Crista galli` | strategy: `manual` | note: Anterior midline skull-base landmark.
- Pituitary fossa | target: `Pituitary fossa` | strategy: `manual` | note: Sella turcica region; useful midline landmark.
- Pons | target: `Pons` | strategy: `manual_or_external_atlas` | support: aseg:Brain-Stem | note: Split manually from coarse brainstem label.
- Prepontine cistern | target: `Prepontine cistern` | strategy: `manual` | note: CSF space anterior to pons; basilar artery relationship.
- Middle cerebellar peduncle | target: `Middle cerebellar peduncle` | strategy: `manual_or_external_atlas` | note: High-yield fiber tract landmark, not a stock FreeSurfer label here.
- Uncus | target: `Uncus` | strategy: `manual` | support: aseg:Left-Amygdala; aparc:entorhinal; aparc:parahippocampal | note: Use nearby labels only as orientation support.
- Temporal horn of the lateral ventricle | target: `Temporal horn of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Inf-Lat-Vent; aseg:Left-Lateral-Ventricle | note: FreeSurfer inferior lateral ventricle is a useful seed, but refine teaching target.
- Nodule of the cerebellum | target: `Nodule of the cerebellum` | strategy: `manual_or_external_atlas` | note: Small vermian structure; manual or specialized atlas.
- Suprasellar cistern | target: `Suprasellar cistern` | strategy: `manual` | note: Good midline CSF landmark around optic chiasm/pituitary stalk.
- Tentorium cerebelli | target: `Tentorium cerebelli` | strategy: `manual` | note: Dural reflection; visible as boundary rather than segmented tissue.
- Interpeduncular cistern | target: `Interpeduncular cistern` | strategy: `manual` | note: CSF space between cerebral peduncles.
- Cerebral crus (cerebral peduncle) | target: `Cerebral crus (cerebral peduncle)` | strategy: `manual_or_external_atlas` | note: Use midbrain-level manual target.
- Sylvian fissure | target: `Sylvian fissure` | strategy: `manual` | support: aparc_a2009s:Lat_Fis-ant-Horizont; aparc_a2009s:Lat_Fis-ant-Vertical; aparc_a2009s:Lat_Fis-post | note: Destrieux fissure components can support, but a simple manual target may teach better.
- Mammillary bodies | target: `Mammillary bodies` | strategy: `manual` | note: Small hypothalamic structures.
- Median interhemispheric fissure | target: `Median interhemispheric fissure` | strategy: `manual` | note: Useful orientation landmark.
- Midbrain | target: `Midbrain` | strategy: `manual_or_external_atlas` | support: aseg:Brain-Stem | note: Split manually from coarse brainstem label.
- Ambient cistern | target: `Ambient cistern` | strategy: `manual` | note: Cistern lateral to midbrain.
- Cerebral aqueduct | target: `Cerebral aqueduct` | strategy: `manual` | note: High-yield small CSF channel between third and fourth ventricles.
- Inferior colliculus | target: `Inferior colliculus` | strategy: `manual_or_external_atlas` | note: Small dorsal midbrain structure.
- Anterior limb of the internal capsule | target: `Anterior limb of the internal capsule` | strategy: `manual_or_external_atlas` | note: High-yield white matter structure not directly labeled by current FreeSurfer outputs.
- Interventricular foramen (foramen of Monro) | target: `Interventricular foramen (foramen of Monro)` | strategy: `manual` | support: aseg:Left-Lateral-Ventricle; aseg:3rd-Ventricle | note: Small communication between lateral and third ventricles.
- Genu of the corpus callosum | target: `Genu of the corpus callosum` | strategy: `freesurfer_support_manual_refine` | support: aseg:CC_Anterior | note: Rename FreeSurfer corpus callosum segment into standard anatomy.
- Frontal horn of the lateral ventricle | target: `Frontal horn of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Use whole lateral ventricle label as support, but target frontal horn manually.
- Genu of the internal capsule | target: `Genu of the internal capsule` | strategy: `manual_or_external_atlas` | note: Manual target between anterior and posterior limbs.
- Quadrigeminal cistern | target: `Quadrigeminal cistern` | strategy: `manual` | note: Posterior to midbrain tectum.
- Head of the caudate nucleus | target: `Head of the caudate nucleus` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Caudate | note: FreeSurfer labels whole caudate; teach head with manual target.
- Lentiform nucleus | target: `Lentiform nucleus` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Putamen; aseg:Left-Pallidum | note: Composite teaching structure from putamen and globus pallidus.
- Pineal gland | target: `Pineal gland` | strategy: `manual` | note: Small midline gland posterior to third ventricle.
- Vermis | target: `Vermis` | strategy: `manual_or_external_atlas` | note: Vermis is not separated in current FreeSurfer outputs.
- Column of the fornix | target: `Column of the fornix` | strategy: `manual_or_external_atlas` | note: Small limbic white matter structure.
- Posterior limb of the internal capsule | target: `Posterior limb of the internal capsule` | strategy: `manual_or_external_atlas` | note: High-yield motor pathway landmark.
- Cingulate gyrus | target: `Cingulate gyrus` | strategy: `freesurfer_support_manual_refine` | support: aparc:caudalanteriorcingulate; aparc:rostralanteriorcingulate; aparc:posteriorcingulate; aparc:isthmuscingulate | note: May be cleaner as anterior/posterior cingulate or one broader teaching target.
- Septum pellucidum | target: `Septum pellucidum` | strategy: `manual` | support: aseg:Left-Lateral-Ventricle; aseg:Right-Lateral-Ventricle | note: Thin membrane between frontal horns.
- Forceps minor | target: `Forceps minor` | strategy: `manual_or_external_atlas` | support: aseg:CC_Anterior | note: Callosal frontal radiation; consider tract atlas.
- Trigone (atrium) of the lateral ventricle | target: `Trigone (atrium) of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Manual target within lateral ventricle label.
- Occipital lobe | target: `Occipital lobe` | strategy: `freesurfer_support_manual_refine` | support: aparc:cuneus; aparc:lateraloccipital; aparc:lingual; aparc:pericalcarine | note: Can be a broad teaching region rather than exact atlas parcel.
- Splenium of the corpus callosum | target: `Splenium of the corpus callosum` | strategy: `freesurfer_support_manual_refine` | support: aseg:CC_Posterior | note: Rename FreeSurfer posterior corpus callosum segment.
- Occipital horn of the lateral ventricle | target: `Occipital horn of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Manual target within lateral ventricle label.
- Body of the lateral ventricle | target: `Body of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Manual target within lateral ventricle label.
- Forceps major | target: `Forceps major` | strategy: `manual_or_external_atlas` | support: aseg:CC_Posterior | note: Callosal occipital radiation; consider tract atlas.
- Body of the corpus callosum | target: `Body of the corpus callosum` | strategy: `freesurfer_support_manual_refine` | support: aseg:CC_Central; aseg:CC_Mid_Anterior; aseg:CC_Mid_Posterior | note: Composite/renamed FreeSurfer corpus callosum segment.
- Centrum semiovale | target: `Centrum semiovale` | strategy: `manual_or_external_atlas` | note: Broad white matter region; manual target may teach better than FreeSurfer white matter parcellation.
- Hand bump of the precentral gyrus | target: `Hand bump of the precentral gyrus` | strategy: `manual` | support: aparc:precentral; aparc_a2009s:G_precentral | note: Manual point/region within precentral gyrus.
- Falx cerebri | target: `Falx cerebri` | strategy: `manual` | note: Midline dural reflection; visible as boundary rather than segmented tissue.
- Orbitofrontal cortex | target: `Orbitofrontal cortex` | strategy: `freesurfer_support_manual_refine` | support: aparc:lateralorbitofrontal; aparc:medialorbitofrontal; aparc_a2009s:G_orbital | note: Learner-facing broad region; may be represented by medial/lateral orbitofrontal parcels.
- Cingulate sulcus | target: `Cingulate sulcus` | strategy: `freesurfer_support_manual_refine` | support: aparc_a2009s:S_cingul-Marginalis; aparc_a2009s:G_and_S_cingul-Ant; aparc_a2009s:G_and_S_cingul-Mid-Ant | note: Useful for cingulate/paracentral region orientation; may need manual target.
- Anterior commissure | target: `Anterior commissure` | strategy: `manual` | note: Classic small midline landmark; useful with AC-PC plane concepts.
- Posterior commissure | target: `Posterior commissure` | strategy: `manual` | note: Small midline landmark near pineal/aqueduct region.
- Cisterna magna | target: `Cisterna magna` | strategy: `manual` | note: Common posterior fossa CSF landmark inferior to the cerebellum.

## T1 Visibility QC

- None

## Needs Manual Refinement

- Cerebellum | target: `Cerebellum` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Cerebellum-Cortex; aseg:Left-Cerebellum-White-Matter | note: Rename learner-facing label to Cerebellum or Cerebellar hemisphere.
- Temporal horn of the lateral ventricle | target: `Temporal horn of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Inf-Lat-Vent; aseg:Left-Lateral-Ventricle | note: FreeSurfer inferior lateral ventricle is a useful seed, but refine teaching target.
- Genu of the corpus callosum | target: `Genu of the corpus callosum` | strategy: `freesurfer_support_manual_refine` | support: aseg:CC_Anterior | note: Rename FreeSurfer corpus callosum segment into standard anatomy.
- Frontal horn of the lateral ventricle | target: `Frontal horn of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Use whole lateral ventricle label as support, but target frontal horn manually.
- Head of the caudate nucleus | target: `Head of the caudate nucleus` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Caudate | note: FreeSurfer labels whole caudate; teach head with manual target.
- Lentiform nucleus | target: `Lentiform nucleus` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Putamen; aseg:Left-Pallidum | note: Composite teaching structure from putamen and globus pallidus.
- Cingulate gyrus | target: `Cingulate gyrus` | strategy: `freesurfer_support_manual_refine` | support: aparc:caudalanteriorcingulate; aparc:rostralanteriorcingulate; aparc:posteriorcingulate; aparc:isthmuscingulate | note: May be cleaner as anterior/posterior cingulate or one broader teaching target.
- Trigone (atrium) of the lateral ventricle | target: `Trigone (atrium) of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Manual target within lateral ventricle label.
- Occipital lobe | target: `Occipital lobe` | strategy: `freesurfer_support_manual_refine` | support: aparc:cuneus; aparc:lateraloccipital; aparc:lingual; aparc:pericalcarine | note: Can be a broad teaching region rather than exact atlas parcel.
- Splenium of the corpus callosum | target: `Splenium of the corpus callosum` | strategy: `freesurfer_support_manual_refine` | support: aseg:CC_Posterior | note: Rename FreeSurfer posterior corpus callosum segment.
- Occipital horn of the lateral ventricle | target: `Occipital horn of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Manual target within lateral ventricle label.
- Body of the lateral ventricle | target: `Body of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Lateral-Ventricle | note: Manual target within lateral ventricle label.
- Body of the corpus callosum | target: `Body of the corpus callosum` | strategy: `freesurfer_support_manual_refine` | support: aseg:CC_Central; aseg:CC_Mid_Anterior; aseg:CC_Mid_Posterior | note: Composite/renamed FreeSurfer corpus callosum segment.
- Orbitofrontal cortex | target: `Orbitofrontal cortex` | strategy: `freesurfer_support_manual_refine` | support: aparc:lateralorbitofrontal; aparc:medialorbitofrontal; aparc_a2009s:G_orbital | note: Learner-facing broad region; may be represented by medial/lateral orbitofrontal parcels.
- Cingulate sulcus | target: `Cingulate sulcus` | strategy: `freesurfer_support_manual_refine` | support: aparc_a2009s:S_cingul-Marginalis; aparc_a2009s:G_and_S_cingul-Ant; aparc_a2009s:G_and_S_cingul-Mid-Ant | note: Useful for cingulate/paracentral region orientation; may need manual target.

## Viewer Name Review

- Globus pallidus | target: `Left Pallidum` | strategy: `freesurfer_seed` | support: aseg:Left-Pallidum
- Third ventricle | target: `3rd Ventricle` | strategy: `freesurfer_seed` | support: aseg:3rd-Ventricle | note: Good stock label candidate.
- Fourth ventricle | target: `4th Ventricle` | strategy: `freesurfer_seed` | support: aseg:4th-Ventricle | note: Good stock label candidate.
- Nucleus accumbens | target: `Left Accumbens area` | strategy: `freesurfer_seed` | support: aseg:Left-Accumbens-area
- Choroid plexus | target: `Left choroid plexus` | strategy: `freesurfer_seed` | support: aseg:Left-choroid-plexus | note: Good stock label candidate, with QC.
- Optic chiasm | target: `Optic Chiasm` | strategy: `freesurfer_seed` | support: aseg:Optic-Chiasm
- Cuneus | target: `Left cuneus` | strategy: `freesurfer_seed` | support: aparc:cuneus
- Entorhinal cortex | target: `Left entorhinal` | strategy: `freesurfer_seed` | support: aparc:entorhinal
- Fusiform gyrus | target: `Left fusiform` | strategy: `freesurfer_seed` | support: aparc:fusiform
- Lingual gyrus | target: `Left lingual` | strategy: `freesurfer_seed` | support: aparc:lingual
- Pars opercularis | target: `Left parsopercularis` | strategy: `freesurfer_seed` | support: aparc:parsopercularis
- Pars orbitalis | target: `Left parsorbitalis` | strategy: `freesurfer_seed` | support: aparc:parsorbitalis
- Pars triangularis | target: `Left parstriangularis` | strategy: `freesurfer_seed` | support: aparc:parstriangularis
- Postcentral gyrus | target: `Left postcentral` | strategy: `freesurfer_seed` | support: aparc:postcentral
- Posterior cingulate gyrus | target: `Left posteriorcingulate` | strategy: `freesurfer_seed` | support: aparc:posteriorcingulate
- Precentral gyrus | target: `Left precentral` | strategy: `freesurfer_seed` | support: aparc:precentral
- Superior frontal gyrus | target: `Left superiorfrontal` | strategy: `freesurfer_seed` | support: aparc:superiorfrontal
- Supramarginal gyrus | target: `Left supramarginal` | strategy: `freesurfer_seed` | support: aparc:supramarginal
- Temporal pole | target: `Left temporalpole` | strategy: `freesurfer_seed` | support: aparc:temporalpole; aparc_a2009s:Pole_temporal | note: Rename from atlas display name and hide laterality in viewer.
- Insular cortex | target: `Left insula` | strategy: `freesurfer_seed` | support: aparc:insula; aparc_a2009s:G_Ins_lg_and_S_cent_ins; aparc_a2009s:G_insular_short | note: Good cortical target; use learner-facing name.

## Multiple Source Labels

- Temporal pole | target: `Left temporalpole` | strategy: `freesurfer_seed` | support: aparc:temporalpole; aparc_a2009s:Pole_temporal | note: Rename from atlas display name and hide laterality in viewer.
- Insular cortex | target: `Left insula` | strategy: `freesurfer_seed` | support: aparc:insula; aparc_a2009s:G_Ins_lg_and_S_cent_ins; aparc_a2009s:G_insular_short | note: Good cortical target; use learner-facing name.
- Cerebellum | target: `Cerebellum` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Cerebellum-Cortex; aseg:Left-Cerebellum-White-Matter | note: Rename learner-facing label to Cerebellum or Cerebellar hemisphere.
- Uncus | target: `Uncus` | strategy: `manual` | support: aseg:Left-Amygdala; aparc:entorhinal; aparc:parahippocampal | note: Use nearby labels only as orientation support.
- Temporal horn of the lateral ventricle | target: `Temporal horn of the lateral ventricle` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Inf-Lat-Vent; aseg:Left-Lateral-Ventricle | note: FreeSurfer inferior lateral ventricle is a useful seed, but refine teaching target.
- Sylvian fissure | target: `Sylvian fissure` | strategy: `manual` | support: aparc_a2009s:Lat_Fis-ant-Horizont; aparc_a2009s:Lat_Fis-ant-Vertical; aparc_a2009s:Lat_Fis-post | note: Destrieux fissure components can support, but a simple manual target may teach better.
- Interventricular foramen (foramen of Monro) | target: `Interventricular foramen (foramen of Monro)` | strategy: `manual` | support: aseg:Left-Lateral-Ventricle; aseg:3rd-Ventricle | note: Small communication between lateral and third ventricles.
- Lentiform nucleus | target: `Lentiform nucleus` | strategy: `freesurfer_support_manual_refine` | support: aseg:Left-Putamen; aseg:Left-Pallidum | note: Composite teaching structure from putamen and globus pallidus.
- Cingulate gyrus | target: `Cingulate gyrus` | strategy: `freesurfer_support_manual_refine` | support: aparc:caudalanteriorcingulate; aparc:rostralanteriorcingulate; aparc:posteriorcingulate; aparc:isthmuscingulate | note: May be cleaner as anterior/posterior cingulate or one broader teaching target.
- Septum pellucidum | target: `Septum pellucidum` | strategy: `manual` | support: aseg:Left-Lateral-Ventricle; aseg:Right-Lateral-Ventricle | note: Thin membrane between frontal horns.
- Occipital lobe | target: `Occipital lobe` | strategy: `freesurfer_support_manual_refine` | support: aparc:cuneus; aparc:lateraloccipital; aparc:lingual; aparc:pericalcarine | note: Can be a broad teaching region rather than exact atlas parcel.
- Body of the corpus callosum | target: `Body of the corpus callosum` | strategy: `freesurfer_support_manual_refine` | support: aseg:CC_Central; aseg:CC_Mid_Anterior; aseg:CC_Mid_Posterior | note: Composite/renamed FreeSurfer corpus callosum segment.
- Hand bump of the precentral gyrus | target: `Hand bump of the precentral gyrus` | strategy: `manual` | support: aparc:precentral; aparc_a2009s:G_precentral | note: Manual point/region within precentral gyrus.
- Angular gyrus | target: `Angular gyrus` | strategy: `freesurfer_seed` | support: aparc_a2009s:G_pariet_inf-Angular; aparc:inferiorparietal | note: High-yield parietal language/network landmark; pair with supramarginal gyrus.
- Superior temporal gyrus | target: `Superior temporal gyrus` | strategy: `freesurfer_seed` | support: aparc:superiortemporal; aparc_a2009s:G_temp_sup-Lateral | note: Common temporal lobe landmark along the Sylvian fissure.
- Middle temporal gyrus | target: `Middle temporal gyrus` | strategy: `freesurfer_seed` | support: aparc:middletemporal; aparc_a2009s:G_temporal_middle | note: Common temporal lobe landmark.
- Inferior temporal gyrus | target: `Inferior temporal gyrus` | strategy: `freesurfer_seed` | support: aparc:inferiortemporal; aparc_a2009s:G_temporal_inf | note: Useful inferior temporal landmark.
- Parahippocampal gyrus | target: `Parahippocampal gyrus` | strategy: `freesurfer_seed` | support: aparc:parahippocampal; aparc_a2009s:G_oc-temp_med-Parahip | note: Important medial temporal landmark adjacent to hippocampus and uncus.
- Orbitofrontal cortex | target: `Orbitofrontal cortex` | strategy: `freesurfer_support_manual_refine` | support: aparc:lateralorbitofrontal; aparc:medialorbitofrontal; aparc_a2009s:G_orbital | note: Learner-facing broad region; may be represented by medial/lateral orbitofrontal parcels.
- Calcarine sulcus | target: `Calcarine sulcus` | strategy: `freesurfer_seed` | support: aparc_a2009s:S_calcarine; aparc:pericalcarine | note: High-yield visual cortex landmark on sagittal/axial views.
- Cingulate sulcus | target: `Cingulate sulcus` | strategy: `freesurfer_support_manual_refine` | support: aparc_a2009s:S_cingul-Marginalis; aparc_a2009s:G_and_S_cingul-Ant; aparc_a2009s:G_and_S_cingul-Mid-Ant | note: Useful for cingulate/paracentral region orientation; may need manual target.

## All Targets

| # | Preferred name | Target entry | Strategy | Laterality | Source support | Flags |
|---:|---|---|---|---|---|---|
| 1 | Lateral Ventricle | Left Lateral Ventricle | freesurfer_seed | left | aseg:Left-Lateral-Ventricle |  |
| 2 | Thalamus | Left Thalamus | freesurfer_seed | left | aseg:Left-Thalamus |  |
| 3 | Caudate | Left Caudate | freesurfer_seed | left | aseg:Left-Caudate |  |
| 4 | Putamen | Left Putamen | freesurfer_seed | left | aseg:Left-Putamen |  |
| 5 | Globus pallidus | Left Pallidum | freesurfer_seed | left | aseg:Left-Pallidum | viewer_name_review |
| 6 | Third ventricle | 3rd Ventricle | freesurfer_seed | midline | aseg:3rd-Ventricle | viewer_name_review |
| 7 | Fourth ventricle | 4th Ventricle | freesurfer_seed | midline | aseg:4th-Ventricle | viewer_name_review |
| 8 | Hippocampus | Left Hippocampus | freesurfer_seed | left | aseg:Left-Hippocampus |  |
| 9 | Amygdala | Left Amygdala | freesurfer_seed | left | aseg:Left-Amygdala |  |
| 10 | Nucleus accumbens | Left Accumbens area | freesurfer_seed | left | aseg:Left-Accumbens-area | viewer_name_review |
| 11 | Choroid plexus | Left choroid plexus | freesurfer_seed | left | aseg:Left-choroid-plexus | viewer_name_review |
| 12 | Optic chiasm | Optic Chiasm | freesurfer_seed | midline | aseg:Optic-Chiasm | viewer_name_review |
| 13 | Cuneus | Left cuneus | freesurfer_seed | left | aparc:cuneus | viewer_name_review |
| 14 | Entorhinal cortex | Left entorhinal | freesurfer_seed | left | aparc:entorhinal | viewer_name_review |
| 15 | Fusiform gyrus | Left fusiform | freesurfer_seed | left | aparc:fusiform | viewer_name_review |
| 16 | Lingual gyrus | Left lingual | freesurfer_seed | left | aparc:lingual | viewer_name_review |
| 17 | Pars opercularis | Left parsopercularis | freesurfer_seed | left | aparc:parsopercularis | viewer_name_review |
| 18 | Pars orbitalis | Left parsorbitalis | freesurfer_seed | left | aparc:parsorbitalis | viewer_name_review |
| 19 | Pars triangularis | Left parstriangularis | freesurfer_seed | left | aparc:parstriangularis | viewer_name_review |
| 20 | Postcentral gyrus | Left postcentral | freesurfer_seed | left | aparc:postcentral | viewer_name_review |
| 21 | Posterior cingulate gyrus | Left posteriorcingulate | freesurfer_seed | left | aparc:posteriorcingulate | viewer_name_review |
| 22 | Precentral gyrus | Left precentral | freesurfer_seed | left | aparc:precentral | viewer_name_review |
| 23 | precuneus | Left precuneus | freesurfer_seed | left | aparc:precuneus |  |
| 24 | Superior frontal gyrus | Left superiorfrontal | freesurfer_seed | left | aparc:superiorfrontal | viewer_name_review |
| 25 | Supramarginal gyrus | Left supramarginal | freesurfer_seed | left | aparc:supramarginal | viewer_name_review |
| 26 | Temporal pole | Left temporalpole | freesurfer_seed | left | aparc:temporalpole<br>aparc_a2009s:Pole_temporal | viewer_name_review, multiple_source_labels_review |
| 27 | Insular cortex | Left insula | freesurfer_seed | left | aparc:insula<br>aparc_a2009s:G_Ins_lg_and_S_cent_ins<br>aparc_a2009s:G_insular_short | viewer_name_review, multiple_source_labels_review |
| 28 | Foramen magnum | Foramen magnum | manual | midline | manual | needs_manual_localization |
| 29 | Medulla oblongata | Medulla oblongata | manual_or_external_atlas | midline | aseg:Brain-Stem | needs_manual_localization, external_atlas_candidate |
| 31 | Cerebellar tonsil | Cerebellar tonsil | manual | left | aseg:Left-Cerebellum-Cortex | needs_manual_localization |
| 32 | Premedullary cistern | Premedullary cistern | manual | midline | manual | needs_manual_localization |
| 37 | Cerebellum | Cerebellum | freesurfer_support_manual_refine | left | aseg:Left-Cerebellum-Cortex<br>aseg:Left-Cerebellum-White-Matter | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 38 | External auditory canal | External auditory canal | manual | left | manual | needs_manual_localization |
| 39 | Foramen of Magendie | Foramen of Magendie | manual | midline | aseg:4th-Ventricle | needs_manual_localization |
| 40 | Superior orbital fissure | Superior orbital fissure | manual | left | manual | needs_manual_localization |
| 41 | Meckel's cave | Meckel's cave | manual | left | manual | needs_manual_localization |
| 42 | Foramen of Luschka | Foramen of Luschka | manual | left | aseg:4th-Ventricle | needs_manual_localization |
| 43 | Crista galli | Crista galli | manual | midline | manual | needs_manual_localization |
| 44 | Pituitary fossa | Pituitary fossa | manual | midline | manual | needs_manual_localization |
| 45 | Pons | Pons | manual_or_external_atlas | midline | aseg:Brain-Stem | needs_manual_localization, external_atlas_candidate |
| 46 | Gyrus rectus | Gyrus rectus | freesurfer_seed | left | aparc_a2009s:G_rectus |  |
| 48 | Prepontine cistern | Prepontine cistern | manual | midline | manual | needs_manual_localization |
| 49 | Middle cerebellar peduncle | Middle cerebellar peduncle | manual_or_external_atlas | left | manual | needs_manual_localization, external_atlas_candidate |
| 50 | Uncus | Uncus | manual | left | aseg:Left-Amygdala<br>aparc:entorhinal<br>aparc:parahippocampal | needs_manual_localization, multiple_source_labels_review |
| 51 | Temporal horn of the lateral ventricle | Temporal horn of the lateral ventricle | freesurfer_support_manual_refine | left | aseg:Left-Inf-Lat-Vent<br>aseg:Left-Lateral-Ventricle | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 52 | Nodule of the cerebellum | Nodule of the cerebellum | manual_or_external_atlas | midline | manual | needs_manual_localization, external_atlas_candidate |
| 54 | Suprasellar cistern | Suprasellar cistern | manual | midline | manual | needs_manual_localization |
| 55 | Tentorium cerebelli | Tentorium cerebelli | manual | bilateral | manual | needs_manual_localization |
| 56 | Interpeduncular cistern | Interpeduncular cistern | manual | midline | manual | needs_manual_localization |
| 57 | Cerebral crus (cerebral peduncle) | Cerebral crus (cerebral peduncle) | manual_or_external_atlas | left | manual | needs_manual_localization, external_atlas_candidate |
| 58 | Sylvian fissure | Sylvian fissure | manual | left | aparc_a2009s:Lat_Fis-ant-Horizont<br>aparc_a2009s:Lat_Fis-ant-Vertical<br>aparc_a2009s:Lat_Fis-post | needs_manual_localization, multiple_source_labels_review |
| 59 | Mammillary bodies | Mammillary bodies | manual | bilateral | manual | needs_manual_localization |
| 60 | Median interhemispheric fissure | Median interhemispheric fissure | manual | midline | manual | needs_manual_localization |
| 61 | Midbrain | Midbrain | manual_or_external_atlas | midline | aseg:Brain-Stem | needs_manual_localization, external_atlas_candidate |
| 62 | Ambient cistern | Ambient cistern | manual | left | manual | needs_manual_localization |
| 63 | Cerebral aqueduct | Cerebral aqueduct | manual | midline | manual | needs_manual_localization |
| 64 | Inferior colliculus | Inferior colliculus | manual_or_external_atlas | left | manual | needs_manual_localization, external_atlas_candidate |
| 66 | Anterior limb of the internal capsule | Anterior limb of the internal capsule | manual_or_external_atlas | left | manual | needs_manual_localization, external_atlas_candidate |
| 67 | Interventricular foramen (foramen of Monro) | Interventricular foramen (foramen of Monro) | manual | left | aseg:Left-Lateral-Ventricle<br>aseg:3rd-Ventricle | needs_manual_localization, multiple_source_labels_review |
| 69 | Genu of the corpus callosum | Genu of the corpus callosum | freesurfer_support_manual_refine | midline | aseg:CC_Anterior | needs_manual_localization, needs_manual_refinement |
| 70 | Frontal horn of the lateral ventricle | Frontal horn of the lateral ventricle | freesurfer_support_manual_refine | left | aseg:Left-Lateral-Ventricle | needs_manual_localization, needs_manual_refinement |
| 71 | Genu of the internal capsule | Genu of the internal capsule | manual_or_external_atlas | left | manual | needs_manual_localization, external_atlas_candidate |
| 72 | Quadrigeminal cistern | Quadrigeminal cistern | manual | midline | manual | needs_manual_localization |
| 73 | Head of the caudate nucleus | Head of the caudate nucleus | freesurfer_support_manual_refine | left | aseg:Left-Caudate | needs_manual_localization, needs_manual_refinement |
| 74 | Lentiform nucleus | Lentiform nucleus | freesurfer_support_manual_refine | left | aseg:Left-Putamen<br>aseg:Left-Pallidum | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 75 | Pineal gland | Pineal gland | manual | midline | manual | needs_manual_localization |
| 76 | Vermis | Vermis | manual_or_external_atlas | midline | manual | needs_manual_localization, external_atlas_candidate |
| 77 | Column of the fornix | Column of the fornix | manual_or_external_atlas | bilateral | manual | needs_manual_localization, external_atlas_candidate |
| 78 | Posterior limb of the internal capsule | Posterior limb of the internal capsule | manual_or_external_atlas | left | manual | needs_manual_localization, external_atlas_candidate |
| 81 | Cingulate gyrus | Cingulate gyrus | freesurfer_support_manual_refine | left | aparc:caudalanteriorcingulate<br>aparc:rostralanteriorcingulate<br>aparc:posteriorcingulate<br>aparc:isthmuscingulate | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 82 | Septum pellucidum | Septum pellucidum | manual | midline | aseg:Left-Lateral-Ventricle<br>aseg:Right-Lateral-Ventricle | needs_manual_localization, multiple_source_labels_review |
| 83 | Forceps minor | Forceps minor | manual_or_external_atlas | bilateral | aseg:CC_Anterior | needs_manual_localization, external_atlas_candidate |
| 84 | Trigone (atrium) of the lateral ventricle | Trigone (atrium) of the lateral ventricle | freesurfer_support_manual_refine | left | aseg:Left-Lateral-Ventricle | needs_manual_localization, needs_manual_refinement |
| 85 | Occipital lobe | Occipital lobe | freesurfer_support_manual_refine | left | aparc:cuneus<br>aparc:lateraloccipital<br>aparc:lingual<br>aparc:pericalcarine | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 86 | Splenium of the corpus callosum | Splenium of the corpus callosum | freesurfer_support_manual_refine | midline | aseg:CC_Posterior | needs_manual_localization, needs_manual_refinement |
| 87 | Occipital horn of the lateral ventricle | Occipital horn of the lateral ventricle | freesurfer_support_manual_refine | left | aseg:Left-Lateral-Ventricle | needs_manual_localization, needs_manual_refinement |
| 88 | Body of the lateral ventricle | Body of the lateral ventricle | freesurfer_support_manual_refine | left | aseg:Left-Lateral-Ventricle | needs_manual_localization, needs_manual_refinement |
| 89 | Forceps major | Forceps major | manual_or_external_atlas | bilateral | aseg:CC_Posterior | needs_manual_localization, external_atlas_candidate |
| 91 | Body of the corpus callosum | Body of the corpus callosum | freesurfer_support_manual_refine | midline | aseg:CC_Central<br>aseg:CC_Mid_Anterior<br>aseg:CC_Mid_Posterior | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 92 | Centrum semiovale | Centrum semiovale | manual_or_external_atlas | bilateral | manual | needs_manual_localization, external_atlas_candidate |
| 93 | Central sulcus | Central sulcus | freesurfer_seed | left | aparc_a2009s:S_central |  |
| 94 | Hand bump of the precentral gyrus | Hand bump of the precentral gyrus | manual | left | aparc:precentral<br>aparc_a2009s:G_precentral | needs_manual_localization, multiple_source_labels_review |
| 95 | Marginal sulcus (pars marginalis) | Marginal sulcus (pars marginalis) | freesurfer_seed | left | aparc_a2009s:S_cingul-Marginalis |  |
| 97 | Falx cerebri | Falx cerebri | manual | midline | manual | needs_manual_localization |
| 98 | Angular gyrus | Angular gyrus | freesurfer_seed | left | aparc_a2009s:G_pariet_inf-Angular<br>aparc:inferiorparietal | multiple_source_labels_review |
| 99 | Superior temporal gyrus | Superior temporal gyrus | freesurfer_seed | left | aparc:superiortemporal<br>aparc_a2009s:G_temp_sup-Lateral | multiple_source_labels_review |
| 100 | Middle temporal gyrus | Middle temporal gyrus | freesurfer_seed | left | aparc:middletemporal<br>aparc_a2009s:G_temporal_middle | multiple_source_labels_review |
| 101 | Inferior temporal gyrus | Inferior temporal gyrus | freesurfer_seed | left | aparc:inferiortemporal<br>aparc_a2009s:G_temporal_inf | multiple_source_labels_review |
| 102 | Parahippocampal gyrus | Parahippocampal gyrus | freesurfer_seed | left | aparc:parahippocampal<br>aparc_a2009s:G_oc-temp_med-Parahip | multiple_source_labels_review |
| 103 | Orbitofrontal cortex | Orbitofrontal cortex | freesurfer_support_manual_refine | left | aparc:lateralorbitofrontal<br>aparc:medialorbitofrontal<br>aparc_a2009s:G_orbital | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 104 | Calcarine sulcus | Calcarine sulcus | freesurfer_seed | left | aparc_a2009s:S_calcarine<br>aparc:pericalcarine | multiple_source_labels_review |
| 105 | Parieto-occipital sulcus | Parieto-occipital sulcus | freesurfer_seed | left | aparc_a2009s:S_parieto_occipital |  |
| 106 | Cingulate sulcus | Cingulate sulcus | freesurfer_support_manual_refine | left | aparc_a2009s:S_cingul-Marginalis<br>aparc_a2009s:G_and_S_cingul-Ant<br>aparc_a2009s:G_and_S_cingul-Mid-Ant | needs_manual_localization, needs_manual_refinement, multiple_source_labels_review |
| 107 | Anterior commissure | Anterior commissure | manual | midline | manual | needs_manual_localization |
| 108 | Posterior commissure | Posterior commissure | manual | midline | manual | needs_manual_localization |
| 109 | Cisterna magna | Cisterna magna | manual | midline | manual | needs_manual_localization |
