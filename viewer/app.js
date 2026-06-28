const DEFAULT_STUDY = "../public/studies/nki_a00039636_t1/study.json";
const APP_BUILD_VERSION = "20260628-03";
const NIVUE_MODULE_URL = "https://cdn.jsdelivr.net/npm/@niivue/niivue@latest/dist/index.js";
const VIEW_TYPES = {
  axial: 0,
  coronal: 1,
  sagittal: 2
};
const VIEW_LABELS = {
  axial: "Axial",
  coronal: "Coronal",
  sagittal: "Sagittal"
};
const VIEW_AXES = {
  sagittal: 0,
  coronal: 1,
  axial: 2
};

const state = {
  study: null,
  studyUrl: null,
  studyBaseUrl: null,
  level: "beginner",
  mode: "browse",
  system: "all",
  search: "",
  viewMode: "axial",
  selectedIds: new Set(),
  activeStructureId: null,
  quizStructureId: null,
  quizRevealed: false,
  quizOrder: [],
  quizCursor: 0,
  quizSignature: "",
  editStructureId: null,
  editTool: "paint",
  editPenSize: 2,
  overlayOpacity: 0.55,
  nv: null,
  niivueReady: false,
  viewerLoadId: 0,
  editLoadId: 0,
  colormaps: new Set()
};

const els = {
  studyTitle: document.querySelector("#studyTitle"),
  levelFilters: document.querySelector("#levelFilters"),
  systemFilters: document.querySelector("#systemFilters"),
  searchInput: document.querySelector("#searchInput"),
  visibleCount: document.querySelector("#visibleCount"),
  selectedCount: document.querySelector("#selectedCount"),
  viewerStatus: document.querySelector("#viewerStatus"),
  activeStructure: document.querySelector("#activeStructure"),
  activeSource: document.querySelector("#activeSource"),
  sliceLabel: document.querySelector("#sliceLabel"),
  sliceValue: document.querySelector("#sliceValue"),
  sliceSlider: document.querySelector("#sliceSlider"),
  viewControls: document.querySelector("#viewControls"),
  browsePanel: document.querySelector("#browsePanel"),
  quizPanel: document.querySelector("#quizPanel"),
  editPanel: document.querySelector("#editPanel"),
  browseTitle: document.querySelector("#browseTitle"),
  structureList: document.querySelector("#structureList"),
  emptyState: document.querySelector("#emptyState"),
  clearButton: document.querySelector("#clearButton"),
  opacitySlider: document.querySelector("#opacitySlider"),
  browseDetails: document.querySelector("#browseDetails"),
  quizMeta: document.querySelector("#quizMeta"),
  quizPrompt: document.querySelector("#quizPrompt"),
  quizInstruction: document.querySelector("#quizInstruction"),
  quizAnswer: document.querySelector("#quizAnswer"),
  quizDetails: document.querySelector("#quizDetails"),
  revealButton: document.querySelector("#revealButton"),
  nextButton: document.querySelector("#nextButton"),
  editTitle: document.querySelector("#editTitle"),
  editStructureSelect: document.querySelector("#editStructureSelect"),
  penSizeSlider: document.querySelector("#penSizeSlider"),
  penSizeValue: document.querySelector("#penSizeValue"),
  editDetails: document.querySelector("#editDetails"),
  undoEditButton: document.querySelector("#undoEditButton"),
  resetEditButton: document.querySelector("#resetEditButton"),
  saveEditButton: document.querySelector("#saveEditButton"),
  clearMaskButton: document.querySelector("#clearMaskButton"),
  clearSliceButton: document.querySelector("#clearSliceButton"),
  clearRangeButton: document.querySelector("#clearRangeButton"),
  fillSliceButton: document.querySelector("#fillSliceButton"),
  fillRangeButton: document.querySelector("#fillRangeButton"),
  sliceRangeStart: document.querySelector("#sliceRangeStart"),
  sliceRangeEnd: document.querySelector("#sliceRangeEnd"),
  canvas: document.querySelector("#niivueCanvas")
};

function getStudyUrl() {
  const params = new URLSearchParams(window.location.search);
  const studyUrl = new URL(params.get("study") || DEFAULT_STUDY, window.location.href);
  studyUrl.searchParams.set("_viewerVersion", APP_BUILD_VERSION);
  return studyUrl;
}

function assetUrl(path) {
  return new URL(path, state.studyBaseUrl).href;
}

function fileNameFromPath(path) {
  return path.split("/").pop() || path;
}

function randomIndex(maxExclusive) {
  if (maxExclusive <= 1) {
    return 0;
  }
  if (window.crypto?.getRandomValues) {
    const values = new Uint32Array(1);
    window.crypto.getRandomValues(values);
    return values[0] % maxExclusive;
  }
  return Math.floor(Math.random() * maxExclusive);
}

function shuffle(values) {
  const output = [...values];
  for (let index = output.length - 1; index > 0; index -= 1) {
    const swapIndex = randomIndex(index + 1);
    [output[index], output[swapIndex]] = [output[swapIndex], output[index]];
  }
  return output;
}

function titleCase(value) {
  return value
    .split("_")
    .map(part => (part.toLowerCase() === "csf" ? "CSF" : part.charAt(0).toUpperCase() + part.slice(1)))
    .join(" ");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function pluralize(count, singular, plural = `${singular}s`) {
  return count === 1 ? singular : plural;
}

function structureById(id) {
  return state.study?.structures.find(structure => structure.id === id) || null;
}

function hasUsableOverlay(structure) {
  return Boolean(structure?.hasOverlay && structure?.overlay?.url);
}

function availableStructures() {
  return (state.study?.structures || []).filter(hasUsableOverlay);
}

function matchesLevel(structure) {
  return structure.audienceLevel === state.level;
}

function matchesSystem(structure) {
  return state.system === "all" || structure.systems.includes(state.system);
}

function searchableText(structure) {
  return [
    structure.displayName,
    structure.targetName,
    structure.laterality,
    structure.difficulty,
    ...(structure.systems || []),
    ...(structure.aliases || []),
    ...(structure.acceptedAnswers || [])
  ]
    .join(" ")
    .toLowerCase();
}

function matchesSearch(structure) {
  if (!state.search) {
    return true;
  }
  return searchableText(structure).includes(state.search.toLowerCase());
}

function filteredStructures() {
  if (!state.study) {
    return [];
  }
  return availableStructures().filter(
    structure => matchesLevel(structure) && matchesSystem(structure) && matchesSearch(structure)
  ).sort((a, b) => a.displayName.localeCompare(b.displayName, undefined, { sensitivity: "base" }));
}

function quizPool() {
  return filteredStructures();
}

function selectedStructures() {
  return availableStructures().filter(structure => state.selectedIds.has(structure.id));
}

function editableStructures() {
  return filteredStructures();
}

async function loadStudy() {
  const url = getStudyUrl();
  const response = await fetch(url.href, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to load study manifest: ${response.status}`);
  }

  const study = await response.json();
  state.study = study;
  state.studyUrl = url;
  state.studyBaseUrl = new URL(".", url.href);
  els.studyTitle.textContent = `${study.study.title} | ${study.study.sequence}`;
}

async function initNiivue() {
  try {
    const module = await Promise.race([
      import(NIVUE_MODULE_URL),
      new Promise((_, reject) => {
        window.setTimeout(
          () => reject(new Error("NiiVue module timed out")),
          45000
        );
      })
    ]);
    const Niivue = module.Niivue || module.default?.Niivue;
    if (!Niivue) {
      throw new Error("NiiVue module did not expose Niivue");
    }

    const nv = new Niivue({
      backColor: [0, 0, 0, 1],
      crosshairWidth: 0,
      dragAndDropEnabled: false,
      isColorbar: false,
      isRadiologicalConvention: true,
      sagittalNoseLeft: true,
      show3Dcrosshair: false,
      textHeight: 0.025
    });

    if (typeof nv.attachToCanvas === "function") {
      await nv.attachToCanvas(els.canvas);
    } else if (typeof nv.attachTo === "function") {
      await nv.attachTo(els.canvas.id);
    }

    nv.onLocationChange = data => {
      updateSliceControls(data?.vox);
    };

    state.nv = nv;
    state.niivueReady = true;
    applyViewMode();
    updateSliceControls();
    setViewerStatus("Viewer ready");
  } catch (error) {
    state.niivueReady = false;
    setViewerStatus(`Viewer library unavailable: ${error.message}`);
  }
}

function setViewerStatus(message) {
  els.viewerStatus.textContent = message;
}

function currentViewerStatus() {
  const overlays = selectedStructures();
  const overlayPhrase = `${overlays.length} ${pluralize(overlays.length, "overlay")}`;
  return `${VIEW_LABELS[state.viewMode]} | ${overlays.length ? `Showing ${overlayPhrase}` : "T1 only"}`;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function volumeShape() {
  const dims = state.nv?.volumes?.[0]?.dimsRAS;
  if (Array.isArray(dims) && dims.length >= 4) {
    return [Number(dims[1]), Number(dims[2]), Number(dims[3])];
  }

  const imageShape = state.study?.image?.shape;
  if (Array.isArray(imageShape) && imageShape.length >= 3) {
    return imageShape.map(Number).slice(0, 3);
  }

  const structureWithShape = state.study?.structures.find(
    structure => structure.overlay?.bestSlices?.shape
  );
  return structureWithShape?.overlay?.bestSlices?.shape?.map(Number).slice(0, 3) || null;
}

function sliceAxis() {
  return VIEW_AXES[state.viewMode] ?? VIEW_AXES.axial;
}

function currentVoxel() {
  const shape = volumeShape();
  if (!shape) {
    return null;
  }

  let voxel = shape.map(value => Math.floor(value / 2));
  if (state.nv?.frac2vox && state.nv.scene?.crosshairPos) {
    try {
      voxel = Array.from(state.nv.frac2vox(state.nv.scene.crosshairPos)).map(value =>
        Math.round(Number(value))
      );
    } catch {
      // Fall back to volume center if NiiVue has not initialized the crosshair yet.
    }
  }

  return voxel.map((value, index) => clamp(value, 0, shape[index] - 1));
}

function updateSliceControls(voxel = null) {
  const shape = volumeShape();
  els.sliceLabel.textContent = `${VIEW_LABELS[state.viewMode]} slice`;

  if (!shape) {
    els.sliceSlider.disabled = true;
    els.sliceSlider.min = "0";
    els.sliceSlider.max = "0";
    els.sliceSlider.value = "0";
    els.sliceValue.textContent = "-";
    return;
  }

  const axis = sliceAxis();
  const maxIndex = Math.max(0, shape[axis] - 1);
  const nextVoxel = voxel ? Array.from(voxel).map(value => Math.round(Number(value))) : currentVoxel();
  const sliceIndex = clamp(nextVoxel?.[axis] ?? Math.floor(maxIndex / 2), 0, maxIndex);

  els.sliceSlider.disabled = false;
  els.sliceSlider.min = "0";
  els.sliceSlider.max = String(maxIndex);
  els.sliceSlider.value = String(sliceIndex);
  els.sliceValue.textContent = `${sliceIndex + 1} / ${maxIndex + 1}`;
  updateEditOperationRanges(shape, sliceIndex);
}

function updateEditOperationRanges(shape = volumeShape(), sliceIndex = null) {
  if (!els.sliceRangeStart || !els.sliceRangeEnd || !shape) {
    return;
  }

  const axis = sliceAxis();
  const max = Math.max(1, shape[axis]);
  const current = (sliceIndex ?? currentVoxel()?.[axis] ?? 0) + 1;
  for (const input of [els.sliceRangeStart, els.sliceRangeEnd]) {
    input.min = "1";
    input.max = String(max);
    input.placeholder = `1-${max}`;
    if (!input.value) {
      input.value = String(clamp(current, 1, max));
    } else {
      input.value = String(clamp(Number.parseInt(input.value, 10) || current, 1, max));
    }
  }
}

function moveCrosshairToVoxel(voxel) {
  if (!state.nv || !voxel) {
    return;
  }

  try {
    if (typeof state.nv.vox2frac === "function") {
      state.nv.scene.crosshairPos = state.nv.vox2frac(voxel);
      state.nv.createOnLocationChange?.();
      state.nv.drawScene?.();
      return;
    }

    if (
      typeof state.nv.moveCrosshairInVox === "function" &&
      typeof state.nv.frac2vox === "function"
    ) {
      const current = currentVoxel();
      state.nv.moveCrosshairInVox(
        voxel[0] - current[0],
        voxel[1] - current[1],
        voxel[2] - current[2]
      );
      return;
    }

    const shape = volumeShape();
    if (shape && typeof state.nv.scene?.crosshairPos === "object") {
      state.nv.scene.crosshairPos = [
        (voxel[0] + 0.5) / shape[0],
        (voxel[1] + 0.5) / shape[1],
        (voxel[2] + 0.5) / shape[2]
      ];
      state.nv.drawScene?.();
    }
  } catch {
    // Slice navigation is a convenience and should not break image display.
  }
}

function setSliceIndex(sliceIndex) {
  const shape = volumeShape();
  const voxel = currentVoxel();
  if (!shape || !voxel) {
    return;
  }

  const axis = sliceAxis();
  voxel[axis] = clamp(Math.round(sliceIndex), 0, shape[axis] - 1);
  moveCrosshairToVoxel(voxel);
  updateSliceControls(voxel);
}

function renderViewControls() {
  document.querySelectorAll("[data-view]").forEach(button => {
    button.classList.toggle("is-active", button.dataset.view === state.viewMode);
  });
}

function applyViewMode() {
  if (!state.nv?.setSliceType) {
    return;
  }
  state.nv.setSliceType(VIEW_TYPES[state.viewMode] ?? VIEW_TYPES.axial);
}

function setViewMode(viewMode, options = {}) {
  if (!(viewMode in VIEW_TYPES)) {
    return;
  }
  state.viewMode = viewMode;
  renderViewControls();
  applyViewMode();
  if (options.jump !== false) {
    jumpToActiveStructure();
  }
  updateSliceControls();
  if (state.niivueReady) {
    setViewerStatus(state.mode === "edit" ? editStatus() : currentViewerStatus());
  }
}

function hexToRgb(hex) {
  const clean = hex.replace("#", "");
  return {
    r: Number.parseInt(clean.slice(0, 2), 16),
    g: Number.parseInt(clean.slice(2, 4), 16),
    b: Number.parseInt(clean.slice(4, 6), 16)
  };
}

function colormapFor(structure) {
  const name = `mask_${structure.id}`;
  if (!state.nv || !state.nv.addColormap || state.colormaps.has(name)) {
    return state.colormaps.has(name) ? name : "red";
  }

  const rgb = hexToRgb(structure.color || "#f2594e");
  const colormap = {
    R: [0, rgb.r, rgb.r],
    G: [0, rgb.g, rgb.g],
    B: [0, rgb.b, rgb.b],
    A: [0, 255, 255],
    I: [0, 1, 255]
  };

  try {
    state.nv.addColormap(name, colormap);
    state.colormaps.add(name);
    return name;
  } catch {
    return "red";
  }
}

function baseVolumeList() {
  return [
    {
      url: assetUrl(state.study.image.url),
      name: fileNameFromPath(state.study.image.url),
      colormap: "gray",
      opacity: 1
    }
  ];
}

function volumeListForSelection() {
  const volumes = baseVolumeList();

  for (const structure of selectedStructures()) {
    volumes.push({
      url: assetUrl(structure.overlay.url),
      name: fileNameFromPath(structure.overlay.url),
      colormap: colormapFor(structure),
      opacity: state.overlayOpacity,
      cal_min: 0,
      cal_max: 1
    });
  }

  return volumes;
}

async function syncViewerVolumes() {
  if (!state.niivueReady || !state.nv || !state.study) {
    return;
  }

  const loadId = ++state.viewerLoadId;
  const overlays = selectedStructures();
  const overlayPhrase = `${overlays.length} ${pluralize(overlays.length, "overlay")}`;
  setViewerStatus(`Loading ${overlayPhrase}...`);

  try {
    await state.nv.loadVolumes(volumeListForSelection());
    if (loadId !== state.viewerLoadId) {
      return;
    }
    applyViewMode();
    jumpToActiveStructure();
    updateSliceControls();
    setViewerStatus(currentViewerStatus());
  } catch (error) {
    setViewerStatus(`Viewer load failed: ${error.message}`);
  }
}

function editStatus(structure = structureById(state.editStructureId)) {
  if (!structure) {
    return `${VIEW_LABELS[state.viewMode]} | No editable annotation`;
  }
  return `${VIEW_LABELS[state.viewMode]} | Editing ${structure.displayName}`;
}

function closeEditDrawing() {
  if (!state.nv) {
    return;
  }

  try {
    state.nv.setDrawingEnabled?.(false);
  } catch {
    // Drawing cleanup should not block changing viewer modes.
  }

  try {
    state.nv.closeDrawing?.();
  } catch {
    // NiiVue may throw if no drawing is currently open.
  }
}

function applyEditTool() {
  if (!state.nv) {
    return;
  }
  state.nv.opts.penSize = state.editPenSize;
  state.nv.setPenValue?.(state.editTool === "erase" ? 0 : 1);
  state.nv.setDrawingEnabled?.(true);
}

function editFileName(structure) {
  const sourceName = fileNameFromPath(structure.overlay?.url || `${structure.id}.nii.gz`);
  const editedName = sourceName.replace(/\.nii(?:\.gz)?$/i, ".edited.nii.gz");
  return editedName === sourceName ? `${sourceName}.edited.nii.gz` : editedName;
}

function ensureEditStructure() {
  const structures = editableStructures();
  if (!structures.length) {
    state.editStructureId = null;
    return null;
  }

  const current = structures.find(structure => structure.id === state.editStructureId);
  if (current) {
    return current;
  }

  const active = structures.find(structure => structure.id === state.activeStructureId);
  state.editStructureId = (active || structures[0]).id;
  return structureById(state.editStructureId);
}

async function syncEditDrawing() {
  if (!state.niivueReady || !state.nv || !state.study) {
    return;
  }

  const structure = ensureEditStructure();
  const loadId = ++state.editLoadId;
  state.viewerLoadId += 1;
  closeEditDrawing();

  if (!structure) {
    setViewerStatus("Loading T1...");
    try {
      await state.nv.loadVolumes(baseVolumeList());
      if (loadId === state.editLoadId && state.mode === "edit") {
        applyViewMode();
        updateSliceControls();
        setViewerStatus(editStatus(null));
      }
    } catch (error) {
      setViewerStatus(`Viewer load failed: ${error.message}`);
    }
    return;
  }

  state.activeStructureId = structure.id;
  setViewerStatus(`Loading editable mask for ${structure.displayName}...`);

  try {
    await state.nv.loadVolumes(baseVolumeList());
    if (loadId !== state.editLoadId || state.mode !== "edit") {
      return;
    }
    applyViewMode();
    const loaded = await state.nv.loadDrawingFromUrl(assetUrl(structure.overlay.url), true);
    if (loadId !== state.editLoadId || state.mode !== "edit") {
      return;
    }
    if (loaded === false) {
      throw new Error("Mask dimensions do not match the T1 volume");
    }
    state.nv.setDrawOpacity?.(0.72);
    applyEditTool();
    jumpToActiveStructure();
    updateSliceControls();
    setViewerStatus(editStatus(structure));
  } catch (error) {
    setViewerStatus(`Edit load failed: ${error.message}`);
  }
}

async function syncActiveViewer() {
  if (state.mode === "edit") {
    await syncEditDrawing();
    return;
  }
  state.editLoadId += 1;
  closeEditDrawing();
  await syncViewerVolumes();
}

function bestVoxelForStructure(structure) {
  const bestSlice = structure?.overlay?.bestSlices?.[state.viewMode];
  if (bestSlice?.voxel) {
    return bestSlice.voxel;
  }
  const centroid = structure?.overlay?.bestSlices?.centroidVoxel;
  if (centroid) {
    return centroid;
  }
  return structure?.quizTargets?.[0]?.voxel || null;
}

function jumpToActiveStructure() {
  const structure = structureById(state.activeStructureId);
  const voxel = bestVoxelForStructure(structure);
  if (!voxel || !state.nv) {
    updateSliceControls();
    return;
  }

  try {
    const targetVox = [voxel.i, voxel.j, voxel.k];
    if (typeof state.nv.vox2frac === "function") {
      state.nv.scene.crosshairPos = state.nv.vox2frac(targetVox);
      state.nv.createOnLocationChange?.();
      state.nv.drawScene?.();
    } else if (
      typeof state.nv.moveCrosshairInVox === "function" &&
      typeof state.nv.frac2vox === "function"
    ) {
      const currentVox = Array.from(state.nv.frac2vox(state.nv.scene.crosshairPos));
      state.nv.moveCrosshairInVox(
        targetVox[0] - currentVox[0],
        targetVox[1] - currentVox[1],
        targetVox[2] - currentVox[2]
      );
    } else if (typeof state.nv.scene?.crosshairPos === "object") {
      const shape = volumeShape() || [256, 256, 256];
      state.nv.scene.crosshairPos = [
        (voxel.i + 0.5) / shape[0],
        (voxel.j + 0.5) / shape[1],
        (voxel.k + 0.5) / shape[2]
      ];
      state.nv.drawScene?.();
    }
    updateSliceControls(targetVox);
  } catch {
    // Crosshair movement is a convenience, so viewer loading should not depend on it.
  }
}

function renderSystemFilters() {
  const structuresForLevel = availableStructures().filter(matchesLevel);
  const systems = Array.from(new Set(structuresForLevel.flatMap(structure => structure.systems))).sort();

  if (state.system !== "all" && !systems.includes(state.system)) {
    state.system = "all";
  }

  els.systemFilters.innerHTML = "";

  const allButton = document.createElement("button");
  allButton.type = "button";
  allButton.dataset.system = "all";
  allButton.textContent = "All systems";
  allButton.classList.toggle("is-active", state.system === "all");
  els.systemFilters.append(allButton);

  for (const system of systems) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.system = system;
    button.textContent = titleCase(system);
    button.classList.toggle("is-active", state.system === system);
    els.systemFilters.append(button);
  }
}

function renderCounts() {
  const visible = filteredStructures();
  els.visibleCount.textContent = visible.length.toString();
  els.selectedCount.textContent = selectedStructures().length.toString();
}

function renderMode() {
  document.querySelectorAll(".mode-button").forEach(button => {
    button.classList.toggle("is-active", button.dataset.mode === state.mode);
  });
  els.browsePanel.classList.toggle("is-hidden", state.mode !== "browse");
  els.quizPanel.classList.toggle("is-hidden", state.mode !== "quiz");
  els.editPanel.classList.toggle("is-hidden", state.mode !== "edit");
}

function renderBrowse() {
  const structures = filteredStructures();
  els.browseTitle.textContent = `${structures.length} ${pluralize(structures.length, "structure")}`;
  els.emptyState.hidden = structures.length > 0;
  els.structureList.innerHTML = "";

  for (const structure of structures) {
    const item = document.createElement("article");
    item.className = "structure-item";
    item.classList.toggle("is-selected", state.selectedIds.has(structure.id));

    const checked = state.selectedIds.has(structure.id) ? "checked" : "";

    item.innerHTML = `
      <label class="structure-toggle">
        <input type="checkbox" data-toggle-id="${escapeHtml(structure.id)}" ${checked} />
        <span class="color-chip" style="--chip-color: ${escapeHtml(structure.color)}"></span>
        <span class="structure-main">
          <span class="structure-name">${escapeHtml(structure.displayName)}</span>
        </span>
      </label>
    `;

    els.structureList.append(item);
  }

  renderBrowseDetails();
}

function renderBrowseDetails() {
  const active = structureById(state.activeStructureId) || selectedStructures()[0] || filteredStructures()[0];
  if (!active) {
    els.browseDetails.innerHTML = "";
    return;
  }
  els.browseDetails.innerHTML = detailsHtml(active, true);
  els.activeStructure.textContent = active.displayName;
  els.activeSource.textContent = "";
}

function detailsHtml(structure, revealName) {
  const title = revealName ? structure.displayName : "Answer hidden";

  return `
    <div class="detail-header">
      <span class="color-chip large" style="--chip-color: ${escapeHtml(structure.color)}"></span>
      <div>
        <h3>${escapeHtml(title)}</h3>
      </div>
    </div>
  `;
}

function ensureQuizStructure() {
  const pool = quizPool();
  if (!pool.length) {
    state.quizStructureId = null;
    return null;
  }

  const order = ensureQuizOrder(pool);
  if (!order.includes(state.quizStructureId)) {
    state.quizCursor = 0;
    state.quizStructureId = order[0];
  }

  return structureById(state.quizStructureId);
}

function quizSignature(pool) {
  return [
    state.level,
    state.system,
    state.search,
    pool.map(structure => structure.id).join(",")
  ].join("|");
}

function ensureQuizOrder(pool = quizPool()) {
  const signature = quizSignature(pool);
  if (signature !== state.quizSignature) {
    state.quizOrder = shuffle(pool.map(structure => structure.id));
    state.quizCursor = 0;
    state.quizSignature = signature;
    state.quizStructureId = null;
  }
  return state.quizOrder;
}

function renderQuiz() {
  const structure = ensureQuizStructure();
  const pool = quizPool();

  if (!structure) {
    els.quizMeta.textContent = "No quiz targets";
    els.quizPrompt.textContent = "Adjust the filters to continue.";
    els.quizAnswer.hidden = true;
    els.quizDetails.innerHTML = "";
    els.revealButton.disabled = true;
    els.nextButton.disabled = true;
    return;
  }

  const order = ensureQuizOrder(pool);
  const orderIndex = Math.max(0, order.findIndex(id => id === structure.id));
  state.quizCursor = orderIndex;
  state.selectedIds = new Set([structure.id]);
  state.activeStructureId = structure.id;
  els.quizMeta.textContent = `${titleCase(state.level)} | ${orderIndex + 1} of ${pool.length}`;
  els.quizPrompt.textContent = "What is the highlighted structure?";
  els.quizInstruction.textContent = "Look at the overlay, decide what it is, then reveal the answer.";
  els.quizAnswer.hidden = !state.quizRevealed;
  els.quizAnswer.textContent = state.quizRevealed ? structure.displayName : "";
  els.quizDetails.innerHTML = state.quizRevealed ? detailsHtml(structure, true) : detailsHtml(structure, false);
  els.revealButton.disabled = false;
  els.nextButton.disabled = false;
  els.activeStructure.textContent = state.quizRevealed ? structure.displayName : "Quiz target";
  els.activeSource.textContent = "";
}

function renderEditToolControls() {
  document.querySelectorAll("[data-edit-tool]").forEach(button => {
    button.classList.toggle("is-active", button.dataset.editTool === state.editTool);
  });
  els.penSizeSlider.value = String(state.editPenSize);
  els.penSizeValue.textContent = String(state.editPenSize);
}

function renderEdit() {
  const structures = editableStructures();
  const structure = ensureEditStructure();
  els.editTitle.textContent = `${structures.length} editable ${pluralize(structures.length, "mask")}`;
  els.editStructureSelect.innerHTML = "";

  for (const item of structures) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.displayName;
    option.selected = item.id === state.editStructureId;
    els.editStructureSelect.append(option);
  }

  const hasStructure = Boolean(structure);
  els.editStructureSelect.disabled = !hasStructure;
  els.undoEditButton.disabled = !hasStructure;
  els.resetEditButton.disabled = !hasStructure;
  els.saveEditButton.disabled = !hasStructure;
  for (const button of [
    els.clearMaskButton,
    els.clearSliceButton,
    els.clearRangeButton,
    els.fillSliceButton,
    els.fillRangeButton
  ]) {
    button.disabled = !hasStructure;
  }
  els.sliceRangeStart.disabled = !hasStructure;
  els.sliceRangeEnd.disabled = !hasStructure;
  document.querySelectorAll("[data-edit-tool]").forEach(button => {
    button.disabled = !hasStructure;
  });
  els.penSizeSlider.disabled = !hasStructure;
  renderEditToolControls();
  updateEditOperationRanges();

  if (!structure) {
    els.editDetails.innerHTML = '<div class="empty-state">No editable masks match these filters.</div>';
    els.activeStructure.textContent = "No annotation selected";
    els.activeSource.textContent = "";
    return;
  }

  state.activeStructureId = structure.id;
  els.editDetails.innerHTML = detailsHtml(structure, true);
  els.activeStructure.textContent = structure.displayName;
  els.activeSource.textContent = "Editing mask";
}

function render() {
  if (!state.study) {
    return;
  }

  renderSystemFilters();
  renderViewControls();
  renderMode();

  if (state.mode === "quiz") {
    renderQuiz();
  } else if (state.mode === "edit") {
    renderEdit();
  } else {
    renderBrowse();
  }

  renderCounts();

  document.querySelectorAll("[data-level]").forEach(button => {
    button.classList.toggle("is-active", button.dataset.level === state.level);
  });
}

function resetForFilterChange() {
  state.selectedIds.clear();
  state.activeStructureId = null;
  state.quizStructureId = null;
  state.quizRevealed = false;
  state.quizOrder = [];
  state.quizCursor = 0;
  state.quizSignature = "";
  state.editStructureId = null;
}

function enterMode(mode) {
  state.mode = mode;
  if (mode === "quiz") {
    const structure = ensureQuizStructure();
    if (structure) {
      state.selectedIds = new Set([structure.id]);
      state.activeStructureId = structure.id;
      state.quizRevealed = false;
    }
  } else if (mode === "edit") {
    const structure = ensureEditStructure();
    if (structure) {
      state.activeStructureId = structure.id;
    }
  }
  render();
  syncActiveViewer();
}

function selectQuizStructure(id) {
  state.quizStructureId = id;
  state.quizCursor = Math.max(0, state.quizOrder.findIndex(item => item === id));
  state.quizRevealed = false;
  state.selectedIds = new Set([id]);
  state.activeStructureId = id;
  render();
  syncActiveViewer();
}

async function saveEditedNifti() {
  const structure = structureById(state.editStructureId);
  if (!structure || !state.nv?.saveImage) {
    return;
  }

  const filename = editFileName(structure);
  setViewerStatus(`Saving ${filename}...`);

  try {
    const saved = await state.nv.saveImage({ filename, isSaveDrawing: true });
    if (saved === false) {
      throw new Error("No editable drawing is open");
    }
    setViewerStatus(`Downloaded ${filename}`);
  } catch (error) {
    setViewerStatus(`Save failed: ${error.message}`);
  }
}

function drawingBitmapAndShape() {
  const bitmap = state.nv?.drawBitmap;
  const shape = volumeShape();
  if (!bitmap || !shape) {
    return null;
  }
  const expectedLength = shape[0] * shape[1] * shape[2];
  if (bitmap.length !== expectedLength) {
    throw new Error(`Drawing size ${bitmap.length} does not match volume size ${expectedLength}`);
  }
  return { bitmap, shape };
}

function voxelIndex(x, y, z, shape) {
  return x + y * shape[0] + z * shape[0] * shape[1];
}

function planeDimensions(axis, shape) {
  if (axis === 0) {
    return [shape[1], shape[2]];
  }
  if (axis === 1) {
    return [shape[0], shape[2]];
  }
  return [shape[0], shape[1]];
}

function planeVoxel(axis, slice, a, b) {
  if (axis === 0) {
    return [slice, a, b];
  }
  if (axis === 1) {
    return [a, slice, b];
  }
  return [a, b, slice];
}

function setDrawingVoxel(bitmap, shape, x, y, z, value) {
  const index = voxelIndex(x, y, z, shape);
  const previous = bitmap[index];
  if (previous === value) {
    return 0;
  }
  bitmap[index] = value;
  return 1;
}

function clearDrawingSlice(bitmap, shape, axis, slice) {
  const [width, height] = planeDimensions(axis, shape);
  let changed = 0;
  for (let b = 0; b < height; b += 1) {
    for (let a = 0; a < width; a += 1) {
      const [x, y, z] = planeVoxel(axis, slice, a, b);
      changed += setDrawingVoxel(bitmap, shape, x, y, z, 0);
    }
  }
  return changed;
}

function fillDrawingSliceHoles(bitmap, shape, axis, slice) {
  const [width, height] = planeDimensions(axis, shape);
  const visited = new Uint8Array(width * height);
  const queue = [];

  const enqueueZero = (a, b) => {
    if (a < 0 || b < 0 || a >= width || b >= height) {
      return;
    }
    const planeIndex = a + b * width;
    if (visited[planeIndex]) {
      return;
    }
    const [x, y, z] = planeVoxel(axis, slice, a, b);
    if (bitmap[voxelIndex(x, y, z, shape)] !== 0) {
      return;
    }
    visited[planeIndex] = 1;
    queue.push([a, b]);
  };

  for (let a = 0; a < width; a += 1) {
    enqueueZero(a, 0);
    enqueueZero(a, height - 1);
  }
  for (let b = 1; b < height - 1; b += 1) {
    enqueueZero(0, b);
    enqueueZero(width - 1, b);
  }

  for (let cursor = 0; cursor < queue.length; cursor += 1) {
    const [a, b] = queue[cursor];
    enqueueZero(a + 1, b);
    enqueueZero(a - 1, b);
    enqueueZero(a, b + 1);
    enqueueZero(a, b - 1);
  }

  let changed = 0;
  for (let b = 0; b < height; b += 1) {
    for (let a = 0; a < width; a += 1) {
      const planeIndex = a + b * width;
      if (visited[planeIndex]) {
        continue;
      }
      const [x, y, z] = planeVoxel(axis, slice, a, b);
      const index = voxelIndex(x, y, z, shape);
      if (bitmap[index] === 0) {
        bitmap[index] = 1;
        changed += 1;
      }
    }
  }
  return changed;
}

function selectedSliceRange(singleSlice = false) {
  const shape = volumeShape();
  const voxel = currentVoxel();
  if (!shape || !voxel) {
    throw new Error("No active slice");
  }
  const axis = sliceAxis();
  const max = shape[axis] - 1;
  const current = clamp(voxel[axis], 0, max);
  if (singleSlice) {
    return { axis, start: current, end: current };
  }

  const fallback = current + 1;
  const startInput = Number.parseInt(els.sliceRangeStart.value, 10) || fallback;
  const endInput = Number.parseInt(els.sliceRangeEnd.value, 10) || startInput;
  const start = clamp(Math.min(startInput, endInput) - 1, 0, max);
  const end = clamp(Math.max(startInput, endInput) - 1, 0, max);
  return { axis, start, end };
}

function applyDrawingOperation(label, operation) {
  try {
    const drawing = drawingBitmapAndShape();
    if (!drawing) {
      setViewerStatus("No editable drawing is loaded");
      return;
    }
    const changed = operation(drawing.bitmap, drawing.shape);
    if (!changed) {
      setViewerStatus(`${label}: no voxels changed`);
      return;
    }
    state.nv.drawBitmap = drawing.bitmap;
    state.nv.drawAddUndoBitmap?.();
    state.nv.refreshDrawing?.(true);
    setViewerStatus(`${label}: changed ${changed} ${pluralize(changed, "voxel")}`);
  } catch (error) {
    setViewerStatus(`${label} failed: ${error.message}`);
  }
}

function clearAllDrawing() {
  applyDrawingOperation("Clear all", bitmap => {
    let changed = 0;
    for (let index = 0; index < bitmap.length; index += 1) {
      if (bitmap[index] !== 0) {
        bitmap[index] = 0;
        changed += 1;
      }
    }
    return changed;
  });
}

function clearDrawingRange(singleSlice = false) {
  const label = singleSlice ? "Clear slice" : "Clear range";
  try {
    const range = selectedSliceRange(singleSlice);
    applyDrawingOperation(label, (bitmap, shape) => {
      let changed = 0;
      for (let slice = range.start; slice <= range.end; slice += 1) {
        changed += clearDrawingSlice(bitmap, shape, range.axis, slice);
      }
      return changed;
    });
  } catch (error) {
    setViewerStatus(`${label} failed: ${error.message}`);
  }
}

function fillDrawingRange(singleSlice = false) {
  const label = singleSlice ? "Fill slice" : "Fill range";
  try {
    const range = selectedSliceRange(singleSlice);
    applyDrawingOperation(label, (bitmap, shape) => {
      let changed = 0;
      for (let slice = range.start; slice <= range.end; slice += 1) {
        changed += fillDrawingSliceHoles(bitmap, shape, range.axis, slice);
      }
      return changed;
    });
  } catch (error) {
    setViewerStatus(`${label} failed: ${error.message}`);
  }
}

els.levelFilters.addEventListener("click", event => {
  const button = event.target.closest("button[data-level]");
  if (!button) {
    return;
  }
  state.level = button.dataset.level;
  resetForFilterChange();
  render();
  syncActiveViewer();
});

els.systemFilters.addEventListener("click", event => {
  const button = event.target.closest("button[data-system]");
  if (!button) {
    return;
  }
  state.system = button.dataset.system;
  resetForFilterChange();
  render();
  syncActiveViewer();
});

els.searchInput.addEventListener("input", event => {
  state.search = event.target.value.trim();
  resetForFilterChange();
  render();
  syncActiveViewer();
});

document.querySelectorAll(".mode-button").forEach(button => {
  button.addEventListener("click", () => enterMode(button.dataset.mode));
});

els.viewControls.addEventListener("click", event => {
  const button = event.target.closest("button[data-view]");
  if (!button) {
    return;
  }
  setViewMode(button.dataset.view);
});

els.sliceSlider.addEventListener("input", event => {
  setSliceIndex(Number.parseInt(event.target.value, 10));
});

els.structureList.addEventListener("change", event => {
  const input = event.target.closest("input[data-toggle-id]");
  if (!input) {
    return;
  }

  const id = input.dataset.toggleId;
  if (input.checked) {
    state.selectedIds.add(id);
    state.activeStructureId = id;
  } else {
    state.selectedIds.delete(id);
    if (state.activeStructureId === id) {
      state.activeStructureId = selectedStructures()[0]?.id || null;
    }
  }

  render();
  syncActiveViewer();
});

els.clearButton.addEventListener("click", () => {
  state.selectedIds.clear();
  state.activeStructureId = null;
  render();
  syncActiveViewer();
});

els.opacitySlider.addEventListener("input", event => {
  state.overlayOpacity = Number.parseFloat(event.target.value);
  syncActiveViewer();
});

els.editStructureSelect.addEventListener("change", event => {
  state.editStructureId = event.target.value;
  state.activeStructureId = state.editStructureId;
  render();
  syncActiveViewer();
});

document.querySelectorAll("[data-edit-tool]").forEach(button => {
  button.addEventListener("click", () => {
    state.editTool = button.dataset.editTool;
    renderEditToolControls();
    applyEditTool();
  });
});

els.penSizeSlider.addEventListener("input", event => {
  state.editPenSize = Number.parseInt(event.target.value, 10);
  renderEditToolControls();
  applyEditTool();
});

els.undoEditButton.addEventListener("click", () => {
  try {
    state.nv?.drawUndo?.();
    setViewerStatus(editStatus());
  } catch (error) {
    setViewerStatus(`Undo failed: ${error.message}`);
  }
});

els.resetEditButton.addEventListener("click", () => {
  syncEditDrawing();
});

els.saveEditButton.addEventListener("click", () => {
  saveEditedNifti();
});

els.clearMaskButton.addEventListener("click", () => {
  clearAllDrawing();
});

els.clearSliceButton.addEventListener("click", () => {
  clearDrawingRange(true);
});

els.clearRangeButton.addEventListener("click", () => {
  clearDrawingRange(false);
});

els.fillSliceButton.addEventListener("click", () => {
  fillDrawingRange(true);
});

els.fillRangeButton.addEventListener("click", () => {
  fillDrawingRange(false);
});

els.revealButton.addEventListener("click", () => {
  state.quizRevealed = true;
  render();
});

els.nextButton.addEventListener("click", () => {
  const pool = quizPool();
  if (!pool.length) {
    return;
  }
  let order = ensureQuizOrder(pool);
  const nextCursor = state.quizCursor + 1;
  if (nextCursor >= order.length) {
    order = shuffle(pool.map(structure => structure.id));
    state.quizOrder = order;
    state.quizCursor = 0;
  } else {
    state.quizCursor = nextCursor;
  }
  selectQuizStructure(order[state.quizCursor]);
});

loadStudy()
  .then(async () => {
    render();
    await initNiivue();
    await syncActiveViewer();
  })
  .catch(error => {
    els.studyTitle.textContent = "Unable to load study";
    setViewerStatus(error.message);
  });
