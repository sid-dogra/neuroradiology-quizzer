# Anatomy Content Style Guide

## Structure Entries

Each structure should have:

- One preferred name.
- Common aliases and abbreviations.
- Accepted quiz answers.
- Difficulty level.
- One or more systems.
- A short description.
- Practical relationships.
- Clinical notes only when they are high-yield and anatomically grounded.

## Difficulty Levels

Beginner:

- Large structures visible on routine T1.
- Useful orientation landmarks.
- Examples: lateral ventricles, thalamus, caudate, pons.

Intermediate:

- Structures that require slice-level confidence or neighboring relationships.
- Examples: posterior limb of internal capsule, hippocampus, IAC, cerebral aqueduct.

Advanced:

- Small foramina, skull base contents, cranial nerve pathways, fine white matter, vascular compartments.
- Examples: foramen ovale, cavernous sinus contents, superior cerebellar peduncle decussation.

## Answer Rules

- Include common abbreviations when unambiguous.
- Avoid accepting overly broad answers for precise structures.
- For paired structures, decide whether laterality matters per question.
- Keep spelling forgiving in UI, but keep metadata names precise.

## Laterality Convention

For bilateral anatomy, prefer left-sided annotations as the default labeled teaching side. Leave the right side unlabeled when possible so learners can compare the highlighted anatomy with the mirror-side native MRI appearance.

Annotate both sides only when laterality is itself the lesson, when pathology/asymmetry is relevant, or when a structure is easier to understand with bilateral context.

## Notes

Descriptions should be brief. The quiz reveal should feel like a useful anatomy pearl, not a textbook page.

Good:

```text
White matter band between thalamus and lentiform nucleus; contains corticospinal and corticobulbar fibers.
```

Too much:

```text
Long multi-paragraph summaries of all known projection fibers and disease associations.
```
