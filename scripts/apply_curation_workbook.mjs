#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const curationDir = path.join(repoRoot, "data", "finalized", "curation");
const workbookPath = path.join(curationDir, "brain_mri_curation.xlsx");
const targetPath = path.join(curationDir, "target-structures.json");

function asText(value) {
  return String(value ?? "").trim();
}

function headerMap(values) {
  const headers = values[0] || [];
  const map = new Map();
  headers.forEach((header, index) => {
    map.set(asText(header), index);
  });
  return map;
}

function cell(row, headers, name) {
  const index = headers.get(name);
  return index === undefined ? "" : asText(row[index]);
}

function boolFromYesNo(value, fallback = true) {
  const text = asText(value).toLowerCase();
  if (["yes", "true", "1", "y"].includes(text)) {
    return true;
  }
  if (["no", "false", "0", "n"].includes(text)) {
    return false;
  }
  return fallback;
}

function normalizeDifficulty(value, fallback = "advanced") {
  return asText(value).toLowerCase() === "beginner" ? "beginner" : fallback === "beginner" ? "beginner" : "advanced";
}

function rowsById(values) {
  const headers = headerMap(values);
  const rows = new Map();
  for (const row of values.slice(1)) {
    const id = cell(row, headers, "id");
    if (id) {
      rows.set(id, { row, headers });
    }
  }
  return rows;
}

function quizQuestionsFromRow(row, headers) {
  const questions = [];
  for (let index = 1; index <= 4; index += 1) {
    const question = cell(row, headers, `question_${index}`);
    const answer = cell(row, headers, `answer_${index}`);
    if (question || answer) {
      questions.push({ question, answer });
    }
  }
  return questions;
}

async function readSheetValues(workbook, sheetName) {
  const sheet = workbook.worksheets.getItem(sheetName);
  return sheet.getUsedRange(true).values;
}

async function main() {
  const workbookBlob = await FileBlob.load(workbookPath);
  const workbook = await SpreadsheetFile.importXlsx(workbookBlob);
  const targetData = JSON.parse(await fs.readFile(targetPath, "utf8"));

  const structureRows = rowsById(await readSheetValues(workbook, "Structures"));
  const quizRows = rowsById(await readSheetValues(workbook, "Quiz Questions"));

  let updated = 0;
  for (const structure of targetData.structures || []) {
    const structureEntry = structureRows.get(structure.id);
    if (structureEntry) {
      const { row, headers } = structureEntry;
      structure.includeInViewer = boolFromYesNo(
        cell(row, headers, "include_in_viewer"),
        structure.includeInViewer !== false
      );
      structure.difficulty = normalizeDifficulty(
        cell(row, headers, "difficulty"),
        structure.difficulty || "advanced"
      );
      const note = cell(row, headers, "review_notes");
      if (note) {
        structure.curationNote = note;
      } else {
        delete structure.curationNote;
      }
      updated += 1;
    }

    const quizEntry = quizRows.get(structure.id);
    if (quizEntry) {
      const { row, headers } = quizEntry;
      const questions = quizQuestionsFromRow(row, headers);
      if (questions.length) {
        structure.quizQuestions = questions;
      } else {
        structure.quizQuestions = [];
      }
      const notes = cell(row, headers, "notes");
      if (notes) {
        structure.quizQuestionNotes = notes;
      } else {
        delete structure.quizQuestionNotes;
      }
    }
  }

  await fs.writeFile(targetPath, `${JSON.stringify(targetData, null, 2)}\n`);
  console.log(`Applied workbook edits to ${path.relative(repoRoot, targetPath)}`);
  console.log(`Updated ${updated} structures`);
}

await main();
