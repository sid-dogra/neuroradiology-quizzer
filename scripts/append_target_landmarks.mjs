#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const defaultWorkbook = path.join(
  repoRoot,
  "outputs",
  "annotation_curation",
  "freesurfer_annotation_options.xlsx",
);
const defaultCandidates = path.join(
  repoRoot,
  "annotations",
  "curation",
  "radiology-landmark-candidates.json",
);

const replacements = new Map([
  ["Cerebellar hemisphere", "Cerebellum"],
  ["Superior vermis of the cerebellum", "Vermis"],
]);

const equivalentNames = new Map([
  ["third ventricle", "3rd ventricle"],
  ["fourth ventricle", "4th ventricle"],
  ["thalamus", "left thalamus"],
  ["choroid plexus", "left choroid plexus"],
  ["insular cortex", "left insula"],
  ["temporal pole", "left temporalpole"],
  ["cerebellar vermis", "vermis"],
]);

function getArg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1 || index === process.argv.length - 1) {
    return fallback;
  }
  return path.resolve(process.argv[index + 1]);
}

function normalizeName(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[()]/g, "")
    .replace(/\bof sylvius\b/g, "")
    .replace(/\bmonroe\b/g, "monro")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function canonicalName(value) {
  const normalized = normalizeName(value);
  return equivalentNames.get(normalized) || normalized;
}

function parseTableNdjson(ndjson) {
  const lines = ndjson.trim().split(/\n+/).filter(Boolean);
  const table = lines.find((line) => JSON.parse(line).kind === "table");
  return table ? JSON.parse(table) : null;
}

async function main() {
  const workbookPath = getArg("--workbook", defaultWorkbook);
  const candidatesPath = getArg("--candidates", defaultCandidates);
  const targetSheetName = "Target";

  const candidates = JSON.parse(await fs.readFile(candidatesPath, "utf8"));
  const input = await FileBlob.load(workbookPath);
  const workbook = await SpreadsheetFile.importXlsx(input);

  const targetInspect = await workbook.inspect({
    kind: "table",
    range: `${targetSheetName}!A1:A500`,
    include: "values,formulas",
    tableMaxRows: 500,
    tableMaxCols: 1,
  });
  const targetTable = parseTableNdjson(targetInspect.ndjson);
  const existingRows = targetTable?.values || [];
  const existingNames = existingRows
    .map((row) => row[0])
    .filter((value) => typeof value === "string" && value.trim());
  const seen = new Set(existingNames.map(canonicalName));

  const additions = [];
  for (const structure of candidates.structures) {
    const preferredName = replacements.get(structure.preferredName) || structure.preferredName;
    const canonical = canonicalName(preferredName);
    if (seen.has(canonical)) {
      continue;
    }
    seen.add(canonical);
    additions.push(preferredName);
  }

  const lastExistingRow = existingRows.reduce((last, row, index) => {
    if (typeof row[0] === "string" && row[0].trim()) {
      return index + 1;
    }
    return last;
  }, 0);
  const startRow = lastExistingRow + 2;
  const targetSheet = workbook.worksheets.getItem(targetSheetName);
  const values = additions.map((name) => [name]);
  if (values.length > 0) {
    targetSheet.getRange(`A${startRow}:A${startRow + values.length - 1}`).values = values;
  }

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(workbookPath);
  console.log(`Preserved ${existingNames.length} existing Target entries`);
  console.log(`Appended ${additions.length} discussed landmarks starting at row ${startRow}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
