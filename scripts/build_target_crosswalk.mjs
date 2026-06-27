#!/usr/bin/env node
import fs from "node:fs/promises";
import { execFile } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const execFileAsync = promisify(execFile);

const DEFAULTS = {
  workbook: path.join(
    repoRoot,
    "outputs",
    "annotation_curation",
    "freesurfer_annotation_options.xlsx",
  ),
  freesurferInventory: path.join(
    repoRoot,
    "annotations",
    "generated",
    "freesurfer-label-inventory.json",
  ),
  curationCandidates: [
    path.join(repoRoot, "annotations", "curation", "radiology-landmark-candidates.json"),
    path.join(repoRoot, "annotations", "curation", "high-value-common-anatomy-candidates.json"),
  ],
  deferredPolicy: path.join(repoRoot, "annotations", "curation", "deferred-targets.json"),
  crosswalkOutput: path.join(repoRoot, "annotations", "curation", "target-crosswalk.json"),
  reviewOutput: path.join(repoRoot, "annotations", "curation", "target-review.md"),
  draftOutput: path.join(repoRoot, "annotations", "structures", "t1-targets.draft.json"),
};

const ALLOWED_SYSTEMS = new Set([
  "ventricles",
  "basal_ganglia",
  "white_matter",
  "brainstem",
  "cerebellum",
  "skull_base",
  "cranial_nerves",
  "vascular",
  "limbic",
  "midline",
  "cortex",
  "deep_gray",
  "csf_spaces",
]);

const LEARNER_NAME_OVERRIDES = new Map([
  ["3rd Ventricle", "Third ventricle"],
  ["4th Ventricle", "Fourth ventricle"],
  ["Left Accumbens area", "Nucleus accumbens"],
  ["Left choroid plexus", "Choroid plexus"],
  ["Left cuneus", "Cuneus"],
  ["Left entorhinal", "Entorhinal cortex"],
  ["Left fusiform", "Fusiform gyrus"],
  ["Left insula", "Insular cortex"],
  ["Left lingual", "Lingual gyrus"],
  ["Left Pallidum", "Globus pallidus"],
  ["Left parsopercularis", "Pars opercularis"],
  ["Left parsorbitalis", "Pars orbitalis"],
  ["Left parstriangularis", "Pars triangularis"],
  ["Left postcentral", "Postcentral gyrus"],
  ["Left posteriorcingulate", "Posterior cingulate gyrus"],
  ["Left precentral", "Precentral gyrus"],
  ["Left superiorfrontal", "Superior frontal gyrus"],
  ["Left supramarginal", "Supramarginal gyrus"],
  ["Left temporalpole", "Temporal pole"],
  ["Optic Chiasm", "Optic chiasm"],
]);

const CANONICAL_EQUIVALENTS = new Map([
  ["3rd ventricle", "third ventricle"],
  ["4th ventricle", "fourth ventricle"],
  ["cerebellar hemisphere", "cerebellum"],
  ["superior vermis of cerebellum", "vermis"],
  ["superior vermis of the cerebellum", "vermis"],
  ["temporalpole", "temporal pole"],
  ["insular cortex", "insula"],
  ["left insula", "insula"],
  ["choroid plexus", "choroid plexus"],
  ["left choroid plexus", "choroid plexus"],
]);

function getArg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1 || index === process.argv.length - 1) {
    return fallback;
  }
  return path.resolve(process.argv[index + 1]);
}

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/\bmonroe\b/g, "monro")
    .replace(/\bof sylvius\b/g, "")
    .replace(/[()]/g, " ")
    .replace(/[_-]+/g, " ")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function stripLaterality(value) {
  return normalize(value).replace(/^(left|right)\s+/, "");
}

function canonical(value) {
  const base = stripLaterality(value);
  return CANONICAL_EQUIVALENTS.get(base) || base;
}

function slug(value) {
  return normalize(value).replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

async function readTargetNames(workbookPath) {
  const python = String.raw`
import json
import sys

from openpyxl import load_workbook

workbook_path = sys.argv[1]
workbook = load_workbook(workbook_path, read_only=True, data_only=False)
if "Target" not in workbook.sheetnames:
    raise SystemExit("Could not read Target tab from workbook")

sheet = workbook["Target"]
targets = []
for row_index, row in enumerate(
    sheet.iter_rows(min_row=1, max_row=500, min_col=1, max_col=1, values_only=True),
    start=1,
):
    value = row[0]
    if not isinstance(value, str):
        continue
    value = value.strip()
    if not value or value.lower() == "display_name":
        continue
    targets.append({"row": row_index, "name": value})

print(json.dumps(targets))
`;
  const { stdout } = await execFileAsync("python3", ["-c", python, workbookPath], {
    maxBuffer: 1024 * 1024,
  });
  return JSON.parse(stdout);
}

function readJson(pathname) {
  return fs.readFile(pathname, "utf8").then(JSON.parse);
}

function buildFreeSurferIndexes(inventory) {
  const byDisplay = new Map();
  const byCanonical = new Map();
  const byAtlasRaw = new Map();

  for (const label of inventory.labels) {
    for (const key of [normalize(label.displayName), normalize(label.name)]) {
      if (!byDisplay.has(key)) {
        byDisplay.set(key, []);
      }
      byDisplay.get(key).push(label);
    }

    const c = canonical(label.displayName);
    if (!byCanonical.has(c)) {
      byCanonical.set(c, []);
    }
    byCanonical.get(c).push(label);

    const rawKey = `${label.atlasId}:${normalize(label.name)}`;
    if (!byAtlasRaw.has(rawKey)) {
      byAtlasRaw.set(rawKey, []);
    }
    byAtlasRaw.get(rawKey).push(label);
  }

  return { byDisplay, byCanonical, byAtlasRaw };
}

function buildCandidateIndex(candidateDocs) {
  const byCanonical = new Map();
  const candidates = [];
  for (const doc of candidateDocs) {
    for (const structure of doc.structures) {
      const item = {
        ...structure,
        candidateListKind: doc.kind,
        candidateSourceContext: doc.sourceContext,
      };
      candidates.push(item);
      const keys = new Set([canonical(item.preferredName)]);
      if (item.preferredName === "Cerebellar hemisphere") {
        keys.add("cerebellum");
      }
      if (item.preferredName === "Superior vermis of the cerebellum") {
        keys.add("vermis");
      }
      for (const key of keys) {
        if (!byCanonical.has(key)) {
          byCanonical.set(key, []);
        }
        byCanonical.get(key).push(item);
      }
    }
  }
  return { byCanonical, candidates };
}

function choosePreferredFreeSurfer(labels) {
  if (!labels || labels.length === 0) {
    return [];
  }
  const filtered = labels.filter((label) => label.laterality !== "right");
  const pool = filtered.length ? filtered : labels;
  const atlasPriority = new Map([
    ["aseg", 0],
    ["aparc", 1],
    ["aparc_a2009s", 2],
    ["aparc_dkt", 3],
    ["wmparc", 4],
    ["ba_exvivo_thresh", 5],
    ["ba_exvivo", 6],
    ["surface_label_files", 7],
  ]);
  return [...pool].sort((a, b) => {
    const atlasA = atlasPriority.get(a.atlasId) ?? 99;
    const atlasB = atlasPriority.get(b.atlasId) ?? 99;
    if (atlasA !== atlasB) {
      return atlasA - atlasB;
    }
    if (a.laterality === "left" && b.laterality !== "left") {
      return -1;
    }
    if (b.laterality === "left" && a.laterality !== "left") {
      return 1;
    }
    return a.displayName.localeCompare(b.displayName);
  });
}

function resolveSupportLabels(supportStrings, indexes) {
  const resolved = [];
  const unresolved = [];
  for (const support of supportStrings || []) {
    const [atlasId, rawLabel] = support.split(":").map((part) => part.trim());
    if (!atlasId || !rawLabel) {
      unresolved.push(support);
      continue;
    }
    const key = `${atlasId}:${normalize(rawLabel)}`;
    const matches = choosePreferredFreeSurfer(indexes.byAtlasRaw.get(key) || []);
    if (matches.length === 0) {
      unresolved.push(support);
      continue;
    }
    resolved.push(...matches);
  }
  return { resolved, unresolved };
}

function learnerName(targetName, candidateMatches) {
  if (LEARNER_NAME_OVERRIDES.has(targetName)) {
    return LEARNER_NAME_OVERRIDES.get(targetName);
  }
  if (candidateMatches.length > 0) {
    const candidate = candidateMatches[0];
    if (candidate.preferredName === "Cerebellar hemisphere") {
      return "Cerebellum";
    }
    if (candidate.preferredName === "Superior vermis of the cerebellum") {
      return "Vermis";
    }
    return candidate.preferredName;
  }
  return targetName.replace(/^Left\s+/, "").replace(/^Right\s+/, "");
}

function inferLaterality(targetName, fsLabels, candidateMatches) {
  if (/^left\b/i.test(targetName)) {
    return "left";
  }
  if (/^right\b/i.test(targetName)) {
    return "right";
  }
  const candidatePolicy = candidateMatches[0]?.lateralityPolicy;
  if (candidatePolicy === "left_reference") {
    return "left";
  }
  if (candidatePolicy === "midline") {
    return "midline";
  }
  if (candidatePolicy === "midline_or_bilateral") {
    return "bilateral";
  }
  if (candidatePolicy === "not_applicable") {
    return "not_applicable";
  }
  const firstFs = fsLabels[0];
  if (firstFs?.laterality) {
    return firstFs.laterality;
  }
  return "not_applicable";
}

function dedupe(values) {
  return [...new Set(values.filter(Boolean))];
}

function systemsFor(fsLabels, candidateMatches) {
  const values = [
    ...candidateMatches.flatMap((candidate) => candidate.systems || []),
    ...fsLabels.flatMap((label) => label.systemsSuggested || []),
  ].filter((system) => ALLOWED_SYSTEMS.has(system));
  return dedupe(values).length ? dedupe(values) : ["midline"];
}

function difficultyFor(fsLabels, candidateMatches) {
  return candidateMatches[0]?.difficultySuggested || fsLabels[0]?.difficultySuggested || "intermediate";
}

function sourceStrategyFor(fsLabels, candidateMatches) {
  if (candidateMatches[0]?.sourceStrategy) {
    return candidateMatches[0].sourceStrategy;
  }
  if (fsLabels.length > 0) {
    return "freesurfer_seed";
  }
  return "manual";
}

function toSourceLabel(label) {
  const sourceLabel = {
    source: label.sourceName || "FreeSurfer",
    label: label.name || label.displayName,
  };
  if (label.labelValue !== undefined && label.labelValue !== null) {
    sourceLabel.value = label.labelValue;
  } else if (label.labelIndex !== undefined && label.labelIndex !== null) {
    sourceLabel.value = String(label.labelIndex);
  }
  return sourceLabel;
}

function reviewFlagsFor({
  targetName,
  preferredName,
  sourceStrategy,
  freeSurferLabels,
  candidateMatches,
  unresolvedSupport,
}) {
  const flags = [];
  if (freeSurferLabels.length === 0 && candidateMatches.length === 0) {
    flags.push("unmatched_target");
  }
  if (sourceStrategy.includes("manual")) {
    flags.push("needs_manual_localization");
  }
  if (sourceStrategy.includes("external_atlas")) {
    flags.push("external_atlas_candidate");
  }
  if (sourceStrategy === "manual_qc_t1_visibility") {
    flags.push("t1_visibility_qc");
  }
  if (sourceStrategy === "freesurfer_support_manual_refine") {
    flags.push("needs_manual_refinement");
  }
  if (preferredName !== targetName.replace(/^Left\s+/, "").replace(/^Right\s+/, "")) {
    flags.push("viewer_name_review");
  }
  if (freeSurferLabels.length > 1) {
    flags.push("multiple_source_labels_review");
  }
  if (unresolvedSupport.length > 0) {
    flags.push("unresolved_support_reference");
  }
  return dedupe(flags);
}

function buildAcceptedAnswers(preferredName, targetName, aliases) {
  return dedupe([
    preferredName,
    preferredName.toLowerCase(),
    targetName,
    targetName.toLowerCase(),
    ...aliases,
  ]).filter((item) => item && item.trim());
}

function makeDraftStructure(entry) {
  const sourceLabels = entry.freeSurferLabels.map(toSourceLabel);
  if (sourceLabels.length === 0) {
    sourceLabels.push({
      source: "manual_t1_annotation",
      label: entry.preferredName,
    });
  }
  const aliases = dedupe([
    entry.targetName,
    ...entry.freeSurferLabels.map((label) => label.displayName),
    ...entry.freeSurferLabels.map((label) => label.name),
  ]).filter((item) => item !== entry.preferredName);
  const clinicalNotes = dedupe([
    `Source strategy: ${entry.sourceStrategy}.`,
    ...entry.candidateMatches.map((candidate) => candidate.reviewNotes),
    ...entry.reviewFlags.map((flag) => `Review flag: ${flag}.`),
  ]);

  return {
    id: entry.id,
    preferredName: entry.preferredName,
    aliases,
    acceptedAnswers: buildAcceptedAnswers(entry.preferredName, entry.targetName, aliases),
    difficulty: entry.difficulty,
    systems: entry.systems,
    laterality: entry.laterality,
    description: `Draft T1 MPRAGE annotation target for ${entry.preferredName}. This entry needs localization and QC before viewer release.`,
    clinicalNotes,
    sourceLabels,
    quizTargets: [
      {
        id: `${entry.id}_mpr_1`,
        view: "mpr",
        prompt: `Identify the ${entry.preferredName}.`,
        status: "needs_localization",
        hint: "Use the T1 MPRAGE anatomy and neighboring landmarks.",
      },
    ],
    references: dedupe([
      "Target tab curation workbook",
      entry.freeSurferLabels.length > 0 ? "FreeSurfer generated inventory" : null,
      ...entry.candidateMatches.map((candidate) => candidate.candidateListKind),
    ]).filter(Boolean),
  };
}

function buildReviewMarkdown(crosswalk) {
  const counts = crosswalk.summary;
  const byFlag = new Map();
  for (const target of crosswalk.targets) {
    for (const flag of target.reviewFlags) {
      if (!byFlag.has(flag)) {
        byFlag.set(flag, []);
      }
      byFlag.get(flag).push(target);
    }
  }
  const lines = [
    "# Target Review",
    "",
    "Generated from the workbook `Target` tab plus the FreeSurfer and curation inventories.",
    "",
    "## Summary",
    "",
    `- Workbook targets: ${counts.totalWorkbookTargets}`,
    `- Active T1 anatomy targets: ${counts.totalTargets}`,
    `- Deferred separate-study targets: ${counts.deferredTargets}`,
    `- FreeSurfer exact/seed matches: ${counts.withFreeSurferLabels}`,
    `- Curation/manual matches: ${counts.withCandidateMatches}`,
    `- Manual localization needed: ${counts.needsManualLocalization}`,
    `- T1 visibility QC needed: ${counts.needsT1VisibilityQc}`,
    `- Needs manual refinement from an atlas/support label: ${counts.needsManualRefinement}`,
    `- Unmatched targets: ${counts.unmatchedTargets}`,
    "",
    "## What To Review First",
    "",
    "1. Confirm the learner-facing names, especially where FreeSurfer names were converted into standard anatomy terms.",
    "2. Confirm whether skull-base, cisternal, and small manual targets are localizable enough on the current T1 to keep.",
    "3. Confirm composite structures that use FreeSurfer only as rough support, such as ventricle subregions, corpus callosum parts, lentiform nucleus, and internal capsule parts.",
    "4. Decide whether advanced small structures should remain in the first release or wait for a later module.",
    "",
  ];

  lines.push("## Deferred To Separate Study", "");
  if (!crosswalk.deferredTargets || crosswalk.deferredTargets.length === 0) {
    lines.push("- None", "");
  } else {
    for (const item of crosswalk.deferredTargets) {
      lines.push(
        `- ${item.preferredName} | target: \`${item.targetName}\` | deferred study: \`${item.deferredStudy.id}\` | reason: ${item.deferredStudy.reason}`,
      );
    }
    lines.push("");
  }

  const sections = [
    ["Unmatched", "unmatched_target"],
    ["Needs Manual Localization", "needs_manual_localization"],
    ["T1 Visibility QC", "t1_visibility_qc"],
    ["Needs Manual Refinement", "needs_manual_refinement"],
    ["Viewer Name Review", "viewer_name_review"],
    ["Multiple Source Labels", "multiple_source_labels_review"],
  ];

  for (const [heading, flag] of sections) {
    const items = byFlag.get(flag) || [];
    lines.push(`## ${heading}`, "");
    if (items.length === 0) {
      lines.push("- None", "");
      continue;
    }
    for (const item of items) {
      const support = item.freeSurferLabels
        .map((label) => `${label.atlasId}:${label.name}`)
        .join("; ");
      const notes = item.candidateMatches.map((candidate) => candidate.reviewNotes).join(" ");
      lines.push(
        `- ${item.preferredName} | target: \`${item.targetName}\` | strategy: \`${item.sourceStrategy}\`${support ? ` | support: ${support}` : ""}${notes ? ` | note: ${notes}` : ""}`,
      );
    }
    lines.push("");
  }

  lines.push("## All Targets", "");
  lines.push("| # | Preferred name | Target entry | Strategy | Laterality | Source support | Flags |");
  lines.push("|---:|---|---|---|---|---|---|");
  for (const item of crosswalk.targets) {
    const support = item.freeSurferLabels
      .map((label) => `${label.atlasId}:${label.name}`)
      .join("<br>");
    lines.push(
      `| ${item.targetIndex} | ${item.preferredName} | ${item.targetName} | ${item.sourceStrategy} | ${item.laterality} | ${support || "manual"} | ${item.reviewFlags.join(", ") || ""} |`,
    );
  }
  return `${lines.join("\n")}\n`;
}

function deferredStudyFor(target, deferredPolicy) {
  for (const study of deferredPolicy.deferredStudies || []) {
    const systems = new Set(study.systems || []);
    if (target.systems.some((system) => systems.has(system))) {
      return {
        id: study.id,
        title: study.title,
        reason: study.reason,
      };
    }
  }
  return null;
}

function summarize(targets, deferredTargets = []) {
  return {
    totalWorkbookTargets: targets.length + deferredTargets.length,
    totalTargets: targets.length,
    deferredTargets: deferredTargets.length,
    withFreeSurferLabels: targets.filter((target) => target.freeSurferLabels.length > 0).length,
    withCandidateMatches: targets.filter((target) => target.candidateMatches.length > 0).length,
    needsManualLocalization: targets.filter((target) =>
      target.reviewFlags.includes("needs_manual_localization"),
    ).length,
    needsT1VisibilityQc: targets.filter((target) => target.reviewFlags.includes("t1_visibility_qc")).length,
    needsManualRefinement: targets.filter((target) =>
      target.reviewFlags.includes("needs_manual_refinement"),
    ).length,
    unmatchedTargets: targets.filter((target) => target.reviewFlags.includes("unmatched_target")).length,
    byStrategy: Object.fromEntries(
      [...new Set(targets.map((target) => target.sourceStrategy))]
        .sort()
        .map((strategy) => [strategy, targets.filter((target) => target.sourceStrategy === strategy).length]),
    ),
  };
}

async function main() {
  const workbookPath = getArg("--workbook", DEFAULTS.workbook);
  const inventoryPath = getArg("--freesurfer-inventory", DEFAULTS.freesurferInventory);
  const deferredPolicyPath = getArg("--deferred-policy", DEFAULTS.deferredPolicy);
  const crosswalkOutput = getArg("--crosswalk-output", DEFAULTS.crosswalkOutput);
  const reviewOutput = getArg("--review-output", DEFAULTS.reviewOutput);
  const draftOutput = getArg("--draft-output", DEFAULTS.draftOutput);

  const targetNames = await readTargetNames(workbookPath);
  const inventory = await readJson(inventoryPath);
  const candidateDocs = await Promise.all(DEFAULTS.curationCandidates.map(readJson));
  const deferredPolicy = await readJson(deferredPolicyPath);
  const fsIndexes = buildFreeSurferIndexes(inventory);
  const candidateIndex = buildCandidateIndex(candidateDocs);

  const allTargets = targetNames.map((target, index) => {
    const exactMatches = choosePreferredFreeSurfer(fsIndexes.byDisplay.get(normalize(target.name)) || []);
    const canonicalMatches = choosePreferredFreeSurfer(fsIndexes.byCanonical.get(canonical(target.name)) || []);
    const fsLabels = exactMatches.length > 0 ? exactMatches.slice(0, 1) : canonicalMatches.slice(0, 3);
    const candidateMatches = candidateIndex.byCanonical.get(canonical(target.name)) || [];
    const support = resolveSupportLabels(
      candidateMatches.flatMap((candidate) => candidate.freeSurferSupport || []),
      fsIndexes,
    );
    const supportLabels = support.resolved.filter(
      (label) => !fsLabels.some((existing) => existing.id === label.id),
    );
    const freeSurferLabels = dedupe([...fsLabels, ...supportLabels].map((label) => label.id)).map(
      (id) => [...fsLabels, ...supportLabels].find((label) => label.id === id),
    );
    const preferredName = learnerName(target.name, candidateMatches);
    const sourceStrategy = sourceStrategyFor(freeSurferLabels, candidateMatches);
    const entry = {
      targetIndex: index + 1,
      workbookRow: target.row,
      targetName: target.name,
      id: slug(preferredName),
      preferredName,
      laterality: inferLaterality(target.name, freeSurferLabels, candidateMatches),
      systems: systemsFor(freeSurferLabels, candidateMatches),
      difficulty: difficultyFor(freeSurferLabels, candidateMatches),
      sourceStrategy,
      freeSurferLabels,
      candidateMatches,
      unresolvedSupport: support.unresolved,
    };
    entry.reviewFlags = reviewFlagsFor(entry);
    return entry;
  });
  const targets = [];
  const deferredTargets = [];
  for (const target of allTargets) {
    const deferredStudy = deferredStudyFor(target, deferredPolicy);
    if (deferredStudy) {
      deferredTargets.push({
        ...target,
        deferredStudy,
        reviewFlags: dedupe([...target.reviewFlags, "deferred_to_separate_study"]),
      });
    } else {
      targets.push(target);
    }
  }

  const crosswalk = {
    version: "0.1.0",
    kind: "target_crosswalk",
    generatedAt: new Date().toISOString(),
    sourceWorkbook: path.relative(repoRoot, workbookPath),
    sourceFreeSurferInventory: path.relative(repoRoot, inventoryPath),
    sourceCandidateLists: DEFAULTS.curationCandidates.map((candidatePath) =>
      path.relative(repoRoot, candidatePath),
    ),
    sourceDeferredPolicy: path.relative(repoRoot, deferredPolicyPath),
    summary: summarize(targets, deferredTargets),
    targets,
    deferredTargets,
  };

  const draft = {
    version: "0.1.0-draft",
    study: {
      id: "nki_a00039636_t1_mprage",
      title: "NKI Rockland sub-A00039636 T1 MPRAGE Draft Anatomy Targets",
      modality: "MR",
      sequence: "3D T1 MPRAGE",
    },
    structures: targets.map(makeDraftStructure),
  };

  await fs.mkdir(path.dirname(crosswalkOutput), { recursive: true });
  await fs.mkdir(path.dirname(draftOutput), { recursive: true });
  await fs.writeFile(crosswalkOutput, `${JSON.stringify(crosswalk, null, 2)}\n`);
  await fs.writeFile(draftOutput, `${JSON.stringify(draft, null, 2)}\n`);
  await fs.writeFile(reviewOutput, buildReviewMarkdown(crosswalk));

  console.log(`Wrote ${path.relative(repoRoot, crosswalkOutput)}`);
  console.log(`Wrote ${path.relative(repoRoot, reviewOutput)}`);
  console.log(`Wrote ${path.relative(repoRoot, draftOutput)}`);
  console.log(JSON.stringify(crosswalk.summary, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
