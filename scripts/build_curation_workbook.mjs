#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const curationDir = path.join(repoRoot, "data", "finalized", "curation");
const targetPath = path.join(curationDir, "target-structures.json");
const publicStudyPath = path.join(repoRoot, "public", "studies", "nki_a00039636_t1", "study.json");
const outputPath = path.join(curationDir, "brain_mri_curation.xlsx");
const previewDir = path.join(repoRoot, "outputs", "curation_workbook_previews");

function yesNo(value) {
  return value ? "yes" : "no";
}

function joinSystems(value) {
  return Array.isArray(value) ? value.join("; ") : "";
}

function normalizeQuizQuestion(question) {
  if (!question || typeof question !== "object") {
    return { question: "", answer: "" };
  }
  return {
    question: question.question || question.prompt || "",
    answer: question.answer || "",
  };
}

function firstQuizQuestions(structure, count = 4) {
  const questions = Array.isArray(structure.quizQuestions)
    ? structure.quizQuestions.map(normalizeQuizQuestion)
    : [];
  while (questions.length < count) {
    questions.push({ question: "", answer: "" });
  }
  return questions.slice(0, count);
}

function overlayMap(publicStudy) {
  const map = new Map();
  for (const structure of publicStudy.structures || []) {
    const overlay = structure.overlay || null;
    map.set(structure.id, {
      hasOverlay: Boolean(overlay),
      overlaySource: overlay?.sourceKind || "",
      reviewStatus: overlay?.reviewStatus || "",
      voxelCount: overlay?.voxelCount ?? "",
      overlayUrl: overlay?.url || "",
    });
  }
  return map;
}

function applyTitleStyle(range) {
  range.format = {
    fill: "#1F4E79",
    font: { bold: true, color: "#FFFFFF", size: 14 },
  };
}

function applyHeaderStyle(range) {
  range.format = {
    fill: "#D9EAF7",
    font: { bold: true, color: "#17365D" },
    borders: { preset: "outside", style: "thin", color: "#9EADBA" },
  };
}

function applyInputStyle(range) {
  range.format = {
    fill: "#FFF2CC",
    borders: { preset: "outside", style: "thin", color: "#D6B656" },
  };
}

function setColumnWidths(sheet, widths) {
  widths.forEach((width, index) => {
    sheet.getRangeByIndexes(0, index, 1, 1).format.columnWidth = width;
  });
}

async function main() {
  await fs.mkdir(curationDir, { recursive: true });
  await fs.mkdir(previewDir, { recursive: true });

  const targetData = JSON.parse(await fs.readFile(targetPath, "utf8"));
  const publicStudy = JSON.parse(await fs.readFile(publicStudyPath, "utf8"));
  const overlays = overlayMap(publicStudy);
  const structures = [...(targetData.structures || [])].sort((a, b) =>
    (a.preferredName || a.id).localeCompare(b.preferredName || b.id, undefined, { sensitivity: "base" })
  );

  const workbook = Workbook.create();
  const instructions = workbook.worksheets.add("Instructions");
  const structureSheet = workbook.worksheets.add("Structures");
  const quizSheet = workbook.worksheets.add("Quiz Questions");

  for (const sheet of [instructions, structureSheet, quizSheet]) {
    sheet.showGridLines = false;
  }

  instructions.getRange("A1:H1").merge();
  instructions.getRange("A1").values = [["Brain MRI Curation Workbook"]];
  applyTitleStyle(instructions.getRange("A1:H1"));
  instructions.getRange("A3:H9").values = [
    ["What to edit", "Use the yellow columns in Structures to include/remove targets, change beginner/advanced level, and leave review notes.", "", "", "", "", "", ""],
    ["Target JSON", "data/finalized/curation/target-structures.json is the source of truth used by the public viewer build.", "", "", "", "", "", ""],
    ["Accepted masks", "Place reviewed mask NIfTIs in data/finalized/accepted_annotations. Rebuild the public bundle afterward.", "", "", "", "", "", ""],
    ["Quiz questions", "Use the Quiz Questions tab for optional revealable questions, such as foraminal contents.", "", "", "", "", "", ""],
    ["Important", "After editing this workbook, run node scripts/apply_curation_workbook.mjs to apply changes back into target-structures.json before rebuilding.", "", "", "", "", "", ""],
    ["Current source", targetData.study?.title || "", "", "", "", "", "", ""],
    ["Structure count", structures.length, "", "", "", "", "", ""],
  ];
  instructions.getRange("A3:A9").format = {
    fill: "#D9EAF7",
    font: { bold: true, color: "#17365D" },
  };
  instructions.getRange("B3:H9").format = { wrapText: true };
  setColumnWidths(instructions, [22, 82, 10, 10, 10, 10, 10, 10]);

  const structureHeaders = [
    "include_in_viewer",
    "difficulty",
    "id",
    "display_name",
    "systems",
    "has_overlay",
    "overlay_source",
    "review_status",
    "accepted_or_generated_file",
    "label_value",
    "target_name",
    "review_notes",
  ];
  const structureRows = structures.map(structure => {
    const overlay = overlays.get(structure.id) || {};
    return [
      yesNo(structure.includeInViewer !== false),
      structure.difficulty || "",
      structure.id,
      structure.preferredName || "",
      joinSystems(structure.systems),
      yesNo(overlay.hasOverlay),
      overlay.overlaySource || "",
      overlay.reviewStatus || "",
      overlay.overlayUrl || "",
      structure.sourceLabels?.[0]?.labelValue ?? "",
      structure.targetName || "",
      structure.curationNote || "",
    ];
  });
  structureSheet.getRangeByIndexes(0, 0, 1, structureHeaders.length).values = [structureHeaders];
  structureSheet.getRangeByIndexes(1, 0, structureRows.length, structureHeaders.length).values = structureRows;
  applyHeaderStyle(structureSheet.getRangeByIndexes(0, 0, 1, structureHeaders.length));
  applyInputStyle(structureSheet.getRangeByIndexes(1, 0, structureRows.length, 2));
  applyInputStyle(structureSheet.getRangeByIndexes(1, 11, structureRows.length, 1));
  structureSheet.getRangeByIndexes(1, 0, structureRows.length, 1).dataValidation = {
    rule: { type: "list", values: ["yes", "no"] },
  };
  structureSheet.getRangeByIndexes(1, 1, structureRows.length, 1).dataValidation = {
    rule: { type: "list", values: ["beginner", "advanced"] },
  };
  structureSheet.getRangeByIndexes(0, 0, structureRows.length + 1, structureHeaders.length).format = {
    wrapText: true,
    borders: { preset: "inside", style: "thin", color: "#E6E6E6" },
  };
  structureSheet.freezePanes.freezeRows(1);
  structureSheet.tables.add(
    `A1:L${structureRows.length + 1}`,
    true,
    "StructureCurationTable"
  );
  setColumnWidths(structureSheet, [16, 14, 32, 34, 34, 12, 22, 16, 42, 12, 34, 44]);

  const quizHeaders = [
    "id",
    "display_name",
    "difficulty",
    "systems",
    "question_1",
    "answer_1",
    "question_2",
    "answer_2",
    "question_3",
    "answer_3",
    "question_4",
    "answer_4",
    "notes",
  ];
  const quizRows = structures.map(structure => {
    const questions = firstQuizQuestions(structure, 4);
    return [
      structure.id,
      structure.preferredName || "",
      structure.difficulty || "",
      joinSystems(structure.systems),
      questions[0].question,
      questions[0].answer,
      questions[1].question,
      questions[1].answer,
      questions[2].question,
      questions[2].answer,
      questions[3].question,
      questions[3].answer,
      structure.quizQuestionNotes || "",
    ];
  });
  quizSheet.getRangeByIndexes(0, 0, 1, quizHeaders.length).values = [quizHeaders];
  quizSheet.getRangeByIndexes(1, 0, quizRows.length, quizHeaders.length).values = quizRows;
  applyHeaderStyle(quizSheet.getRangeByIndexes(0, 0, 1, quizHeaders.length));
  applyInputStyle(quizSheet.getRangeByIndexes(1, 4, quizRows.length, 9));
  quizSheet.getRangeByIndexes(0, 0, quizRows.length + 1, quizHeaders.length).format = {
    wrapText: true,
    borders: { preset: "inside", style: "thin", color: "#E6E6E6" },
  };
  quizSheet.freezePanes.freezeRows(1);
  quizSheet.freezePanes.freezeColumns(2);
  quizSheet.tables.add(
    `A1:M${quizRows.length + 1}`,
    true,
    "QuizQuestionTable"
  );
  setColumnWidths(quizSheet, [32, 34, 14, 30, 48, 62, 48, 62, 48, 62, 48, 62, 42]);

  const checks = await workbook.inspect({
    kind: "workbook,sheet,table",
    maxChars: 5000,
    tableMaxRows: 4,
    tableMaxCols: 6,
  });
  console.log(checks.ndjson);

  const formulaErrors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    summary: "formula error scan",
  });
  console.log(formulaErrors.ndjson);

  for (const sheetName of ["Instructions", "Structures", "Quiz Questions"]) {
    const preview = await workbook.render({
      sheetName,
      autoCrop: "all",
      scale: 1,
      format: "png",
    });
    await fs.writeFile(
      path.join(previewDir, `${sheetName.replaceAll(" ", "_").toLowerCase()}.png`),
      new Uint8Array(await preview.arrayBuffer())
    );
  }

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(outputPath);
  await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });
  console.log(`Saved ${outputPath}`);
}

await main();
