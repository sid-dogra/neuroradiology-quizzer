# Curation Files

This folder contains the human-editable structure database for the viewer.

## Main Files

- `target-structures.json`: source of truth for the public viewer build.
- `brain_mri_curation.xlsx`: spreadsheet view of the same structure list, with tabs for level assignment and optional quiz questions.

## Editing Targets

In `target-structures.json`:

- Set `includeInViewer` to `false` to temporarily remove a structure from the viewer.
- Set `difficulty` to `beginner` or `advanced` to move a structure between quiz/viewer levels.
- Use `quizQuestions` for optional revealable teaching questions.

In `brain_mri_curation.xlsx`:

- Use the `Structures` tab to review include/exclude status, difficulty, overlay status, and notes.
- Use the `Quiz Questions` tab for optional question/answer pairs.

For now, the JSON is the build source. If you edit the workbook, ask Codex to apply the spreadsheet edits back to `target-structures.json` before rebuilding the public viewer bundle.

## Commands

After editing the workbook:

```bash
node scripts/apply_curation_workbook.mjs
```

To regenerate the workbook from the JSON:

```bash
node scripts/build_curation_workbook.mjs
```

To rebuild the public viewer bundle:

```bash
python3 scripts/build_public_niivue_study.py
```
