#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const defaultInput = path.join(
  repoRoot,
  "annotations",
  "generated",
  "freesurfer-label-inventory.json",
);
const defaultOutput = path.join(
  repoRoot,
  "outputs",
  "annotation_curation",
  "freesurfer_annotation_options.xlsx",
);

function getArg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1 || index === process.argv.length - 1) {
    return fallback;
  }
  return path.resolve(process.argv[index + 1]);
}

function columnName(index) {
  let name = "";
  let n = index + 1;
  while (n > 0) {
    const remainder = (n - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

function rangeAddress(sheetName, rowCount, columnCount) {
  return `${sheetName}!A1:${columnName(columnCount - 1)}${rowCount}`;
}

function systemList(label) {
  return (label.systemsSuggested || []).join("; ");
}

function pathValue(label, key) {
  return label.paths?.[key] || "";
}

function colorValue(label) {
  const color = label.color;
  if (!color) {
    return "";
  }
  return `${color.r},${color.g},${color.b}`;
}

function num(label, key) {
  const value = label.stats?.[key];
  return Number.isFinite(value) ? value : "";
}

function buildOptionRows(labels) {
  const headers = [
    "include_decision",
    "priority",
    "reviewer_notes",
    "manual_edit_needed",
    "label_id",
    "display_name",
    "raw_label_name",
    "atlas_id",
    "source_name",
    "source_kind",
    "laterality",
    "hemisphere",
    "label_value",
    "label_index",
    "suggested_systems",
    "suggested_difficulty",
    "first_pass_suggested",
    "include_reason",
    "curation_status",
    "volume_mm3",
    "gray_matter_volume_mm3",
    "surface_area_mm2",
    "vertex_count",
    "voxel_count",
    "thickness_avg_mm",
    "color_rgb",
    "volume_path",
    "surface_annotation_path",
    "surface_label_path",
    "stats_path",
    "color_table_path",
  ];

  const rows = labels.map((label) => [
    "",
    "",
    "",
    "",
    label.id,
    label.displayName,
    label.name,
    label.atlasId,
    label.sourceName,
    label.sourceKind,
    label.laterality,
    label.hemisphere || "",
    label.labelValue ?? "",
    label.labelIndex ?? "",
    systemList(label),
    label.difficultySuggested,
    label.includeSuggested ? "yes" : "no",
    label.includeReason,
    label.curationStatus,
    num(label, "volumeMm3"),
    num(label, "grayMatterVolumeMm3"),
    num(label, "surfaceAreaMm2"),
    num(label, "vertexCount"),
    num(label, "voxelCount"),
    num(label, "thicknessAverageMm"),
    colorValue(label),
    pathValue(label, "volume"),
    pathValue(label, "surfaceAnnotation"),
    pathValue(label, "surfaceLabel"),
    pathValue(label, "stats"),
    pathValue(label, "colorTable"),
  ]);

  return [headers, ...rows];
}

function buildSourceRows(inventory) {
  const headers = [
    "atlas_id",
    "source_name",
    "source_kind",
    "label_count",
    "volume_path",
    "left_annotation_path",
    "right_annotation_path",
    "label_directory",
    "notes",
  ];
  const labelsByAtlas = new Map();
  for (const label of inventory.labels) {
    labelsByAtlas.set(label.atlasId, (labelsByAtlas.get(label.atlasId) || 0) + 1);
  }
  const rows = inventory.sources.map((source) => [
    source.id,
    source.displayName,
    source.sourceKind,
    labelsByAtlas.get(source.id) || source.entryCount || 0,
    source.volumePath || "",
    source.leftAnnotationPath || "",
    source.rightAnnotationPath || "",
    source.labelDirectory || "",
    source.description || "",
  ]);
  return [headers, ...rows];
}

function buildSummaryRows(inventory) {
  return [
    ["field", "value"],
    ["subject_id", inventory.subject.id],
    ["source_dataset", inventory.subject.sourceDataset],
    ["source_participant", inventory.subject.sourceParticipant],
    ["source_session", inventory.subject.sourceSession],
    ["source_sequence", inventory.subject.sourceSequence],
    ["freesurfer_version", inventory.subject.freesurferVersion || ""],
    ["total_labels", inventory.summary.labelCount],
    ["suggested_first_pass", inventory.summary.includeSuggestedCount],
    ["held_back", inventory.summary.heldBackCount],
    ["teaching_laterality", inventory.curationPolicy.teachingLaterality],
    ["right_side_policy", inventory.curationPolicy.rightSideUse],
    ["qc_note", inventory.curationPolicy.rightHemisphereCaveat],
  ];
}

function buildInstructionsRows(inventory) {
  return [
    ["FreeSurfer Annotation Options"],
    [""],
    ["Purpose", "Review atlas-derived labels and mark what should enter the curated teaching annotation database."],
    ["How to use", "Edit the first four columns on All Options or Suggested First Pass, then send the workbook back."],
    ["include_decision", "Use include / exclude / maybe / needs_manual / duplicate."],
    ["priority", "Use high / medium / low if useful."],
    ["manual_edit_needed", "Use yes / no / unsure."],
    ["Important", "Rows are machine-generated candidates and all require QC before public teaching use."],
    ["Laterality", inventory.curationPolicy.rightSideUse],
    ["Generated labels", inventory.summary.labelCount],
    ["Suggested first pass", inventory.summary.includeSuggestedCount],
    [""],
    ["Recommended first pass", "Start with left-sided and midline labels where first_pass_suggested = yes."],
  ];
}

async function main() {
  const inputPath = getArg("--input", defaultInput);
  const outputPath = getArg("--output", defaultOutput);
  const raw = await fs.readFile(inputPath, "utf8");
  const inventory = JSON.parse(raw);

  const workbook = Workbook.create();
  const instructions = workbook.worksheets.add("Instructions");
  const allOptions = workbook.worksheets.add("All Options");
  const suggested = workbook.worksheets.add("Suggested First Pass");
  const sources = workbook.worksheets.add("Atlas Summary");

  const allRows = buildOptionRows(inventory.labels);
  const suggestedRows = buildOptionRows(
    inventory.labels.filter((label) => label.includeSuggested),
  );
  const sourceRows = buildSourceRows(inventory);
  const summaryRows = buildSummaryRows(inventory);
  const instructionRows = buildInstructionsRows(inventory);

  instructions.getRange(rangeAddress("Instructions", instructionRows.length, 2)).values =
    instructionRows;
  instructions.getRange(`D1:E${summaryRows.length}`).values = summaryRows;
  allOptions.getRange(rangeAddress("All Options", allRows.length, allRows[0].length)).values =
    allRows;
  suggested.getRange(
    rangeAddress("Suggested First Pass", suggestedRows.length, suggestedRows[0].length),
  ).values = suggestedRows;
  sources.getRange(rangeAddress("Atlas Summary", sourceRows.length, sourceRows[0].length)).values =
    sourceRows;

  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(outputPath);

  console.log(`Wrote ${path.relative(repoRoot, outputPath)}`);
  console.log(`${inventory.summary.labelCount} options exported`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
