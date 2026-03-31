// Prometheus DS Bootstrap Plugin
// Generates variables, color styles, text styles, and component scaffolds
// for the Prometheus Design System in Figma.
//
// Figma Plugin API Reference: https://www.figma.com/plugin-docs/

// ─── Token Definitions ──────────────────────────────────────────────────────

const BRAND_COLORS = {
  "brand/orange": { r: 0.902, g: 0.322, b: 0.173 },       // #e6522c
  "brand/header-bg": { r: 0.255, g: 0.286, b: 0.318 },    // rgb(65,73,81)
  "brand/primary": { r: 0.133, g: 0.545, b: 0.902 },      // #228be6
};

const HEALTH_COLORS = {
  ok: {
    light: { bg: { r: 0.922, g: 0.984, b: 0.933 }, text: { r: 0.169, g: 0.541, b: 0.243 }, border: { r: 0.549, g: 0.914, b: 0.604 } },
    dark:  { bg: { r: 0.169, g: 0.541, b: 0.243 }, text: { r: 0.922, g: 0.984, b: 0.933 }, border: { r: 0.184, g: 0.620, b: 0.267 } }
  },
  err: {
    light: { bg: { r: 1.0, g: 0.878, b: 0.878 },   text: { r: 0.788, g: 0.165, b: 0.165 }, border: { r: 1.0, g: 0.788, b: 0.788 } },
    dark:  { bg: { r: 0.455, g: 0.165, b: 0.165 },  text: { r: 1.0, g: 0.878, b: 0.878 },   border: { r: 0.788, g: 0.165, b: 0.165 } }
  },
  warn: {
    light: { bg: { r: 1.0, g: 0.976, b: 0.859 },   text: { r: 0.902, g: 0.467, b: 0.0 },   border: { r: 1.0, g: 0.847, b: 0.659 } },
    dark:  { bg: { r: 0.902, g: 0.467, b: 0.0 },    text: { r: 1.0, g: 0.976, b: 0.859 },   border: { r: 0.902, g: 0.467, b: 0.0 } }
  },
  info: {
    light: { bg: { r: 0.906, g: 0.961, b: 1.0 },   text: { r: 0.094, g: 0.392, b: 0.671 }, border: { r: 0.647, g: 0.847, b: 1.0 } },
    dark:  { bg: { r: 0.094, g: 0.392, b: 0.671 },  text: { r: 0.906, g: 0.961, b: 1.0 },   border: { r: 0.094, g: 0.392, b: 0.671 } }
  },
  unknown: {
    light: { bg: { r: 0.945, g: 0.953, b: 0.961 }, text: { r: 0.286, g: 0.314, b: 0.341 }, border: { r: 0.871, g: 0.886, b: 0.902 } },
    dark:  { bg: { r: 0.286, g: 0.314, b: 0.341 }, text: { r: 0.678, g: 0.714, b: 0.745 }, border: { r: 0.525, g: 0.557, b: 0.588 } }
  }
};

const SPACING = {
  "spacing/xs": 8,
  "spacing/sm": 12,
  "spacing/md": 16,
  "spacing/lg": 20,
  "spacing/xl": 32,
};

const RADIUS = {
  "radius/default": 4,
  "radius/sm": 2,
  "radius/md": 8,
  "radius/lg": 16,
  "radius/pill": 9999,
};

const TEXT_STYLES = [
  { name: "heading/page",    family: "Inter", size: 20, weight: 700, lineHeight: 1.25 },
  { name: "heading/section", family: "Inter", size: 18, weight: 600, lineHeight: 1.25 },
  { name: "heading/card",    family: "Inter", size: 16, weight: 600, lineHeight: 1.25 },
  { name: "body/default",    family: "Inter", size: 14, weight: 400, lineHeight: 1.5 },
  { name: "body/emphasis",   family: "Inter", size: 14, weight: 500, lineHeight: 1.5 },
  { name: "body/small",      family: "Inter", size: 12, weight: 400, lineHeight: 1.5 },
  { name: "label/badge",     family: "Inter", size: 11, weight: 600, lineHeight: 1.25 },
  { name: "label/section",   family: "Inter", size: 11, weight: 700, lineHeight: 1.25 },
  { name: "label/nav",       family: "Inter", size: 13, weight: 500, lineHeight: 1.5 },
  { name: "code/default",    family: "Courier New", size: 13, weight: 400, lineHeight: 1.6 },
  { name: "code/metric",     family: "Courier New", size: 13, weight: 400, lineHeight: 1.5 },
  { name: "code/label",      family: "Courier New", size: 11, weight: 400, lineHeight: 1.5 },
  { name: "stats/badge",     family: "Inter", size: 11, weight: 600, lineHeight: 1.25 },
];

const SHADOW_STYLES = [
  { name: "elevation/none", effects: [] },
  {
    name: "elevation/xs",
    effects: [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.05 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true, blendMode: "NORMAL" },
    ]
  },
  {
    name: "elevation/sm",
    effects: [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.08 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true, blendMode: "NORMAL" },
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.06 }, offset: { x: 0, y: 2 }, radius: 6, spread: 0, visible: true, blendMode: "NORMAL" },
    ]
  },
  {
    name: "elevation/md",
    effects: [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.09 }, offset: { x: 0, y: 2 }, radius: 8, spread: 0, visible: true, blendMode: "NORMAL" },
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.07 }, offset: { x: 0, y: 4 }, radius: 12, spread: 0, visible: true, blendMode: "NORMAL" },
    ]
  },
  {
    name: "elevation/lg",
    effects: [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.1 }, offset: { x: 0, y: 4 }, radius: 16, spread: 0, visible: true, blendMode: "NORMAL" },
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.08 }, offset: { x: 0, y: 8 }, radius: 24, spread: 0, visible: true, blendMode: "NORMAL" },
    ]
  },
  {
    name: "elevation/xl",
    effects: [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.12 }, offset: { x: 0, y: 8 }, radius: 32, spread: 0, visible: true, blendMode: "NORMAL" },
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.1 }, offset: { x: 0, y: 16 }, radius: 48, spread: 0, visible: true, blendMode: "NORMAL" },
    ]
  },
];

// ─── Variable Creation ──────────────────────────────────────────────────────

async function createVariableCollections() {
  figma.notify("Creating variable collections...");

  // Brand collection
  const brandCollection = figma.variables.createVariableCollection("Brand");
  const brandMode = brandCollection.modes[0].modeId;
  for (const [name, rgb] of Object.entries(BRAND_COLORS)) {
    const v = figma.variables.createVariable(name, brandCollection, "COLOR");
    v.setValueForMode(brandMode, rgb);
  }

  // Spacing collection
  const spacingCollection = figma.variables.createVariableCollection("Spacing");
  const spacingMode = spacingCollection.modes[0].modeId;
  for (const [name, value] of Object.entries(SPACING)) {
    const v = figma.variables.createVariable(name, spacingCollection, "FLOAT");
    v.setValueForMode(spacingMode, value);
  }

  // Radius collection
  const radiusCollection = figma.variables.createVariableCollection("Radius");
  const radiusMode = radiusCollection.modes[0].modeId;
  for (const [name, value] of Object.entries(RADIUS)) {
    const v = figma.variables.createVariable(name, radiusCollection, "FLOAT");
    v.setValueForMode(radiusMode, value);
  }

  // Health Status collection (with Light/Dark modes)
  const healthCollection = figma.variables.createVariableCollection("Health Status");
  const lightModeId = healthCollection.modes[0].modeId;
  healthCollection.renameMode(lightModeId, "Light");
  const darkModeId = healthCollection.addMode("Dark");

  for (const [status, modes] of Object.entries(HEALTH_COLORS)) {
    for (const suffix of ["bg", "text", "border"]) {
      const varName = `health/${status}-${suffix}`;
      const v = figma.variables.createVariable(varName, healthCollection, "COLOR");
      v.setValueForMode(lightModeId, modes.light[suffix]);
      v.setValueForMode(darkModeId, modes.dark[suffix]);
    }
  }

  // Surface collection (with Light/Dark modes)
  const surfaceCollection = figma.variables.createVariableCollection("Surface");
  const surfLightId = surfaceCollection.modes[0].modeId;
  surfaceCollection.renameMode(surfLightId, "Light");
  const surfDarkId = surfaceCollection.addMode("Dark");

  const surfaces = {
    "surface/card-bg":      { light: { r: 1, g: 1, b: 1 },           dark: { r: 0.145, g: 0.149, b: 0.169 } },
    "surface/codebox-bg":   { light: { r: 0.945, g: 0.953, b: 0.961 }, dark: { r: 0.129, g: 0.145, b: 0.161 } },
    "surface/accordion-bg": { light: { r: 0.973, g: 0.976, b: 0.98 },  dark: { r: 0.173, g: 0.176, b: 0.196 } },
  };

  for (const [name, vals] of Object.entries(surfaces)) {
    const v = figma.variables.createVariable(name, surfaceCollection, "COLOR");
    v.setValueForMode(surfLightId, vals.light);
    v.setValueForMode(surfDarkId, vals.dark);
  }

  return { brandCollection, spacingCollection, radiusCollection, healthCollection, surfaceCollection };
}

// ─── Text Style Creation ────────────────────────────────────────────────────

async function createTextStyles() {
  figma.notify("Creating text styles...");

  for (const def of TEXT_STYLES) {
    const weightStyle = def.weight >= 700 ? "Bold" : def.weight >= 600 ? "Semi Bold" : def.weight >= 500 ? "Medium" : "Regular";
    let resolvedStyle = weightStyle;

    try {
      await figma.loadFontAsync({ family: def.family, style: weightStyle });
    } catch (_e) {
      // Fall back to Regular if the requested weight isn't available
      try {
        await figma.loadFontAsync({ family: def.family, style: "Regular" });
        resolvedStyle = "Regular";
      } catch (fallbackErr) {
        console.error(`Skipping text style "${def.name}": font "${def.family}" unavailable.`, fallbackErr);
        continue;
      }
    }

    const style = figma.createTextStyle();
    style.name = def.name;
    style.fontName = { family: def.family, style: resolvedStyle };
    style.fontSize = def.size;
    style.lineHeight = { value: def.lineHeight * 100, unit: "PERCENT" };
  }
}

// ─── Effect Style Creation ──────────────────────────────────────────────────

async function createEffectStyles() {
  figma.notify("Creating elevation styles...");

  for (const def of SHADOW_STYLES) {
    const style = figma.createEffectStyle();
    style.name = def.name;
    style.effects = def.effects;
  }
}

// ─── Component Creation ─────────────────────────────────────────────────────
// All values sourced directly from /components/*.html + tokens.html

async function createComponentScaffolds() {
  figma.notify("Creating components...");

  await figma.loadFontAsync({ family: "Inter",       style: "Regular"  });
  await figma.loadFontAsync({ family: "Inter",       style: "Medium"   });
  await figma.loadFontAsync({ family: "Inter",       style: "Semi Bold" });
  await figma.loadFontAsync({ family: "Inter",       style: "Bold"     });
  await figma.loadFontAsync({ family: "Courier New", style: "Regular"  });

  const page = figma.createPage();
  page.name = "Components";

  // ── Color palette (exact values from tokens.html) ──────────────────────
  const COL = {
    // Brand
    orange:      { r: 0.902, g: 0.322, b: 0.173 }, // #e6522c
    blue:        { r: 0.133, g: 0.545, b: 0.902 }, // #228be6
    headerBg:    { r: 0.255, g: 0.286, b: 0.318 }, // rgb(65,73,81)
    // Health step-5 (badge text / border accent)
    green:       { r: 0.318, g: 0.812, b: 0.400 }, // #51cf66
    red:         { r: 1.000, g: 0.420, b: 0.420 }, // #ff6b6b
    yellow:      { r: 1.000, g: 0.831, b: 0.231 }, // #ffd43b
    gray:        { r: 0.678, g: 0.710, b: 0.741 }, // #adb5bd
    // Health step-0 (badge bg, light mode)
    greenBg:     { r: 0.922, g: 0.984, b: 0.933 }, // #ebfbee
    redBg:       { r: 1.000, g: 0.961, b: 0.961 }, // #fff5f5
    yellowBg:    { r: 1.000, g: 0.984, b: 0.922 }, // #fffbeb
    blueBg:      { r: 0.906, g: 0.961, b: 1.000 }, // #e7f5ff
    grayBg:      { r: 0.973, g: 0.976, b: 0.980 }, // #f8f9fa
    // Health step-8 (dark text on light bg)
    greenFg:     { r: 0.184, g: 0.620, b: 0.267 }, // #2f9e44
    redFg:       { r: 0.980, g: 0.322, b: 0.322 }, // #fa5252
    yellowFg:    { r: 0.902, g: 0.467, b: 0.000 }, // #e67700
    blueFg:      { r: 0.098, g: 0.443, b: 0.761 }, // #1971c2
    grayFg:      { r: 0.286, g: 0.314, b: 0.341 }, // #495057
    // Label syntax colours (light mode)
    labelName:   { r: 0.502, g: 0.000, b: 0.000 }, // #800000
    labelValue:  { r: 0.639, g: 0.082, b: 0.082 }, // #a31515
    // Neutral surface
    white:       { r: 1.000, g: 1.000, b: 1.000 },
    pageBg:      { r: 0.961, g: 0.965, b: 0.969 },
    surface:     { r: 0.973, g: 0.976, b: 0.980 }, // #f8f9fa
    border:      { r: 0.871, g: 0.886, b: 0.902 }, // ~#dee2e6
    borderMid:   { r: 0.718, g: 0.745, b: 0.773 },
    textPrimary: { r: 0.133, g: 0.149, b: 0.169 },
    textSecond:  { r: 0.286, g: 0.314, b: 0.341 }, // #495057
    textMuted:   { r: 0.447, g: 0.475, b: 0.502 },
    textSubtle:  { r: 0.600, g: 0.630, b: 0.670 },
    navText:     { r: 0.800, g: 0.820, b: 0.850 },
  };

  // ── Helpers ─────────────────────────────────────────────────────────────

  function sf(col) { return [{ type: "SOLID", color: col }]; }

  function setFill(node, col) { node.fills = sf(col); }

  function noFill(node) { node.fills = []; }

  function setStroke(node, col, w) {
    node.strokes = sf(col);
    node.strokeWeight = w || 1;
    node.strokeAlign = "INSIDE";
  }

  // Left-border accent: wraps content in a HORIZONTAL frame with a coloured bar on the left.
  // Returns the inner content frame to append children to.
  // Usage: const inner = wrapWithLeftBorder(comp, COL.green, 5);
  function wrapWithLeftBorder(parent, col, w) {
    parent.layoutMode = "HORIZONTAL";
    parent.itemSpacing = 0;
    parent.paddingTop = 0; parent.paddingBottom = 0;
    parent.paddingLeft = 0; parent.paddingRight = 0;

    const bar = figma.createRectangle();
    bar.resize(w || 5, 8);
    bar.fills = sf(col);
    parent.appendChild(bar);
    bar.layoutSizingVertical = "FILL"; // must be set after appending to auto-layout parent

    const inner = figma.createFrame();
    inner.layoutMode = "VERTICAL";
    inner.primaryAxisSizingMode = "AUTO";
    noFill(inner);
    parent.appendChild(inner);
    inner.counterAxisSizingMode = "FILL"; // must be set after appending to auto-layout parent
    return inner;
  }

  function autoFrame(dir) {
    const f = figma.createFrame();
    f.layoutMode = dir || "HORIZONTAL";
    f.primaryAxisSizingMode = "AUTO";
    f.counterAxisSizingMode = "AUTO";
    noFill(f);
    return f;
  }

  function txt(chars, family, style, size, col, extra) {
    const t = figma.createText();
    t.fontName  = { family, style };
    t.fontSize  = size;
    t.characters = chars;
    t.fills     = sf(col);
    if (extra && extra.lineHeight)      t.lineHeight      = extra.lineHeight;
    if (extra && extra.letterSpacing)   t.letterSpacing   = extra.letterSpacing;
    if (extra && extra.textDecoration)  t.textDecoration  = extra.textDecoration;
    return t;
  }

  function inter(chars, style, size, col, extra) {
    return txt(chars, "Inter", style, size, col, extra);
  }

  function mono(chars, size, col, extra) {
    return txt(chars, "Courier New", "Regular", size, col, extra);
  }

  function divRect(w, col) {
    const r = figma.createRectangle();
    r.resize(w, 1);
    r.fills = sf(col);
    return r;
  }

  function shadowXS() {
    return [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.05 },
              offset: { x: 0, y: 1 }, radius: 3, spread: 0,
              visible: true, blendMode: "NORMAL" }];
  }

  function shadowMD() {
    return [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.09 },
        offset: { x: 0, y: 2 }, radius: 8,  spread: 0, visible: true, blendMode: "NORMAL" },
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.07 },
        offset: { x: 0, y: 4 }, radius: 12, spread: 0, visible: true, blendMode: "NORMAL" },
    ];
  }

  // Layout cursor
  let cx = 0, cy = 0;
  const GAP = 40;

  function nextRow() {
    let bottom = 0;
    for (const n of page.children) {
      const b = n.y + n.height + GAP;
      if (b > bottom) bottom = b;
    }
    cy = bottom;
    cx = 0;
  }

  function place(comp) {
    comp.x = cx;
    comp.y = cy;
    page.appendChild(comp);
    cx += comp.width + GAP;
  }

  // ── Row 1: Atoms ─────────────────────────────────────────────────────────

  // 1. StatusBadge
  // Pill (999px radius), light bg + dark fg for each health state
  // 11px Semi Bold, 0.02em letter-spacing, 10px h-pad, 3px v-pad
  {
    const comp = figma.createComponent();
    comp.name = "StatusBadge";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.itemSpacing = 8;
    comp.counterAxisAlignItems = "CENTER";
    noFill(comp);

    const STATES = [
      { label: "OK",      bg: COL.greenBg,  fg: COL.greenFg  },
      { label: "Error",   bg: COL.redBg,    fg: COL.redFg    },
      { label: "Warning", bg: COL.yellowBg, fg: COL.yellowFg },
      { label: "Info",    bg: COL.blueBg,   fg: COL.blueFg   },
      { label: "Unknown", bg: COL.grayBg,   fg: COL.grayFg   },
    ];

    for (const s of STATES) {
      const pill = figma.createFrame();
      pill.layoutMode = "HORIZONTAL";
      pill.primaryAxisSizingMode = "AUTO";
      pill.counterAxisSizingMode = "AUTO";
      pill.paddingTop = 3; pill.paddingBottom = 3;
      pill.paddingLeft = 10; pill.paddingRight = 10;
      pill.cornerRadius = 999;
      pill.counterAxisAlignItems = "CENTER";
      setFill(pill, s.bg);

      pill.appendChild(inter(s.label, "Semi Bold", 11, s.fg,
        { letterSpacing: { value: 0.22, unit: "PIXELS" } })); // ~0.02em
      comp.appendChild(pill);
    }
    place(comp);
  }

  // 2. LabelBadge
  // Courier New 11px, 999px radius, 22px height, 8px h-pad
  // Label name: #800000, label value: #a31515, separator muted
  {
    const comp = figma.createComponent();
    comp.name = "LabelBadge";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.paddingTop = 3; comp.paddingBottom = 3;
    comp.paddingLeft = 8; comp.paddingRight = 8;
    comp.itemSpacing = 0;
    comp.cornerRadius = 999;
    comp.counterAxisAlignItems = "CENTER";
    setFill(comp, COL.grayBg);
    setStroke(comp, COL.border, 1);

    comp.appendChild(mono("job",          11, COL.labelName));
    comp.appendChild(mono("=",            11, COL.textMuted));
    comp.appendChild(mono('"prometheus"', 11, COL.labelValue));
    place(comp);
  }

  // 3. NavButton
  // 6px 12px padding, 4px radius, 13px Regular, active=blue bg, text white
  {
    const comp = figma.createComponent();
    comp.name = "NavButton";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.paddingTop = 6; comp.paddingBottom = 6;
    comp.paddingLeft = 12; comp.paddingRight = 12;
    comp.itemSpacing = 6;
    comp.cornerRadius = 4;
    comp.counterAxisAlignItems = "CENTER";
    setFill(comp, COL.blue);   // active state

    comp.appendChild(inter("Targets", "Regular", 13, COL.white));
    place(comp);
  }

  // 4. ThemeToggle
  // 32×32px, 4px radius, 1px border, 16px icon, rgba(255,255,255,0.1) bg
  {
    const comp = figma.createComponent();
    comp.name = "ThemeToggle";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "FIXED";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(32, 32);
    comp.cornerRadius = 4;
    comp.primaryAxisAlignItems = "CENTER";
    comp.counterAxisAlignItems = "CENTER";
    comp.fills = [{ type: "SOLID", color: COL.white, opacity: 0.1 }];
    setStroke(comp, COL.borderMid, 1);

    comp.appendChild(inter("D", "Bold", 13, COL.white)); // moon = light-mode icon
    place(comp);
  }

  // 5. SeriesName
  // Courier New 13px, syntax-coloured metric_name{label="value"}
  {
    const comp = figma.createComponent();
    comp.name = "SeriesName";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.itemSpacing = 0;
    noFill(comp);

    comp.appendChild(mono("up",               13, COL.textPrimary));
    comp.appendChild(mono("{",                13, COL.textMuted));
    comp.appendChild(mono("job",              13, COL.labelName));
    comp.appendChild(mono('="prometheus"',    13, COL.labelValue));
    comp.appendChild(mono(",",               13, COL.textMuted));
    comp.appendChild(mono("instance",         13, COL.labelName));
    comp.appendChild(mono('="localhost:9090"',13, COL.labelValue));
    comp.appendChild(mono("}",               13, COL.textMuted));
    place(comp);
  }

  // 6. EndpointLink
  // 13px underlined link + 10px pill query-param badges, 6px gap, 18px badge h
  {
    const comp = figma.createComponent();
    comp.name = "EndpointLink";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.itemSpacing = 6;
    comp.counterAxisAlignItems = "CENTER";
    noFill(comp);

    comp.appendChild(inter("http://localhost:9090/metrics", "Regular", 13, COL.blue,
      { textDecoration: "UNDERLINE" }));

    const qBadge = figma.createFrame();
    qBadge.layoutMode = "HORIZONTAL";
    qBadge.primaryAxisSizingMode = "AUTO";
    qBadge.counterAxisSizingMode = "AUTO";
    qBadge.paddingTop = 2; qBadge.paddingBottom = 2;
    qBadge.paddingLeft = 6; qBadge.paddingRight = 6;
    qBadge.cornerRadius = 999;
    qBadge.counterAxisAlignItems = "CENTER";
    setFill(qBadge, COL.grayBg);
    setStroke(qBadge, COL.border, 1);
    qBadge.appendChild(inter("debug=true", "Regular", 10, COL.textSecond));
    comp.appendChild(qBadge);
    place(comp);
  }

  // ── Row 2 ────────────────────────────────────────────────────────────────
  nextRow();

  // 7. ErrorAlert
  // 12px 16px padding, 6px radius, 1px border, max 500px
  // Title 13px Semi Bold, body 13px Regular, red severity
  {
    const comp = figma.createComponent();
    comp.name = "ErrorAlert";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "FIXED";
    comp.counterAxisSizingMode = "AUTO";
    comp.resize(500, 10);
    comp.paddingTop = 12; comp.paddingBottom = 12;
    comp.paddingLeft = 16; comp.paddingRight = 16;
    comp.itemSpacing = 10;
    comp.counterAxisAlignItems = "MIN";
    comp.cornerRadius = 6;
    setFill(comp, COL.redBg);
    setStroke(comp, COL.red, 1);

    comp.appendChild(inter("⚠", "Bold", 14, COL.redFg));

    const col = autoFrame("VERTICAL");
    col.itemSpacing = 2;
    col.appendChild(inter("Error loading targets",              "Semi Bold", 13, COL.redFg));
    col.appendChild(inter("connection refused: localhost:9090", "Regular",  13, COL.textSecond));
    comp.appendChild(col);
    place(comp);
  }

  // 8. CodeBlock
  // 16px padding, 8px radius, 1px border, Courier New 13px, lh 1.6
  {
    const comp = figma.createComponent();
    comp.name = "CodeBlock";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(540, 10);
    comp.paddingTop = 16; comp.paddingBottom = 16;
    comp.paddingLeft = 16; comp.paddingRight = 16;
    comp.itemSpacing = 0;
    comp.cornerRadius = 8;
    setFill(comp, COL.grayBg);
    setStroke(comp, COL.border, 1);

    const LH = { lineHeight: { value: 160, unit: "PERCENT" } };
    comp.appendChild(mono('up{job="prometheus",instance="localhost:9090"} 1',    13, COL.textPrimary, LH));
    comp.appendChild(mono('scrape_duration_seconds{job="prometheus"} 0.002',     13, COL.textPrimary, LH));
    comp.appendChild(mono('scrape_samples_scraped{job="prometheus"} 731',        13, COL.textPrimary, LH));
    place(comp);
  }

  // 9. KeyValueTable
  // 6px 12px cell padding, 13px, key col 40% width Semi Bold, value Regular
  {
    const comp = figma.createComponent();
    comp.name = "KeyValueTable";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.itemSpacing = 0;
    comp.cornerRadius = 4;
    setFill(comp, COL.white);
    setStroke(comp, COL.border, 1);

    const TOTAL = 340;
    const KEY_W = Math.round(TOTAL * 0.4); // 136
    const VAL_W = TOTAL - KEY_W;           // 204

    const rows = [
      ["job",      "prometheus"    ],
      ["instance", "localhost:9090"],
      ["env",      "production"    ],
      ["region",   "us-east-1"     ],
    ];

    for (let i = 0; i < rows.length; i++) {
      if (i > 0) comp.appendChild(divRect(TOTAL, COL.border));

      const row = figma.createFrame();
      row.layoutMode = "HORIZONTAL";
      row.primaryAxisSizingMode = "AUTO";
      row.counterAxisSizingMode = "AUTO";
      row.counterAxisAlignItems = "CENTER";
      row.itemSpacing = 0;
      row.fills = i % 2 === 0 ? sf(COL.white) : sf(COL.surface);

      const kCell = figma.createFrame();
      kCell.layoutMode = "HORIZONTAL"; kCell.counterAxisAlignItems = "CENTER";
      kCell.primaryAxisSizingMode = "FIXED"; kCell.counterAxisSizingMode = "AUTO";
      kCell.resize(KEY_W, 10);
      kCell.paddingTop = 6; kCell.paddingBottom = 6;
      kCell.paddingLeft = 12; kCell.paddingRight = 12;
      noFill(kCell);
      kCell.appendChild(inter(rows[i][0], "Semi Bold", 13, COL.textPrimary));

      const vCell = figma.createFrame();
      vCell.layoutMode = "HORIZONTAL"; vCell.counterAxisAlignItems = "CENTER";
      vCell.primaryAxisSizingMode = "FIXED"; vCell.counterAxisSizingMode = "AUTO";
      vCell.resize(VAL_W, 10);
      vCell.paddingTop = 6; vCell.paddingBottom = 6;
      vCell.paddingLeft = 12; vCell.paddingRight = 12;
      noFill(vCell);
      vCell.appendChild(inter(rows[i][1], "Regular", 13, COL.textSecond));

      row.appendChild(kCell);
      row.appendChild(vCell);
      comp.appendChild(row);
    }
    place(comp);
  }

  // 10. EmptyState
  // 32px v-pad, 12px gap, 40px icon @ 0.3 opacity, centered
  // Message 14px Medium, description 13px Regular
  {
    const comp = figma.createComponent();
    comp.name = "EmptyState";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "FIXED";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(340, 220);
    comp.paddingTop = 32; comp.paddingBottom = 32;
    comp.paddingLeft = 32; comp.paddingRight = 32;
    comp.itemSpacing = 12;
    comp.primaryAxisAlignItems = "CENTER";
    comp.counterAxisAlignItems = "CENTER";
    setFill(comp, COL.surface);
    setStroke(comp, COL.border, 1);

    // Icon wrapper at 0.3 opacity
    const iconWrap = figma.createFrame();
    iconWrap.layoutMode = "HORIZONTAL";
    iconWrap.primaryAxisSizingMode = "FIXED";
    iconWrap.counterAxisSizingMode = "FIXED";
    iconWrap.resize(40, 40);
    iconWrap.primaryAxisAlignItems = "CENTER";
    iconWrap.counterAxisAlignItems = "CENTER";
    iconWrap.opacity = 0.3;
    noFill(iconWrap);
    iconWrap.appendChild(inter("o", "Regular", 32, COL.textMuted));
    comp.appendChild(iconWrap);

    comp.appendChild(inter("No targets found",                    "Medium",  14, COL.textSecond));
    comp.appendChild(inter("No scrape targets match this filter.", "Regular", 13, COL.textMuted));
    place(comp);
  }

  // ── Row 3 ────────────────────────────────────────────────────────────────
  nextRow();

  // 11. HealthPanel
  // Accordion item: 5px LEFT border colour-coded by health state
  // 12px 16px padding, 8px radius, 8px internal gap
  // Shows: title row (endpoint + status badge) + meta line + endpoint link
  {
    const comp = figma.createComponent();
    comp.name = "HealthPanel";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.cornerRadius = 8;
    setFill(comp, COL.white);
    setStroke(comp, COL.border, 1);

    const inner = wrapWithLeftBorder(comp, COL.green, 5);
    inner.paddingTop = 12; inner.paddingBottom = 12;
    inner.paddingLeft = 16; inner.paddingRight = 16;
    inner.itemSpacing = 8;

    // Title row
    const titleRow = figma.createFrame();
    titleRow.layoutMode = "HORIZONTAL";
    titleRow.primaryAxisSizingMode = "FIXED";
    titleRow.counterAxisSizingMode = "AUTO";
    titleRow.resize(330, 10);
    titleRow.primaryAxisAlignItems = "SPACE_BETWEEN";
    titleRow.counterAxisAlignItems = "CENTER";
    noFill(titleRow);

    titleRow.appendChild(inter("prometheus / localhost:9090", "Semi Bold", 14, COL.textPrimary));

    const upPill = figma.createFrame();
    upPill.layoutMode = "HORIZONTAL";
    upPill.primaryAxisSizingMode = "AUTO";
    upPill.counterAxisSizingMode = "AUTO";
    upPill.paddingTop = 3; upPill.paddingBottom = 3;
    upPill.paddingLeft = 10; upPill.paddingRight = 10;
    upPill.cornerRadius = 999;
    setFill(upPill, COL.greenBg);
    upPill.appendChild(inter("UP", "Semi Bold", 11, COL.greenFg,
      { letterSpacing: { value: 0.22, unit: "PIXELS" } }));
    titleRow.appendChild(upPill);
    inner.appendChild(titleRow);

    inner.appendChild(inter("Last scrape: 2.3s ago  •  731 samples", "Regular", 13, COL.textMuted));
    inner.appendChild(mono("http://localhost:9090/metrics", 12, COL.blue,
      { textDecoration: "UNDERLINE" }));

    place(comp);
  }

  // 12. InfoCard
  // 16px padding, 8px radius, 1px border, xs shadow
  // Header: 18px icon + 18px Semi Bold title, then content rows
  {
    const comp = figma.createComponent();
    comp.name = "InfoCard";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "FIXED";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(320, 210);
    comp.paddingTop = 16; comp.paddingBottom = 16;
    comp.paddingLeft = 16; comp.paddingRight = 16;
    comp.itemSpacing = 12;
    comp.cornerRadius = 8;
    setFill(comp, COL.white);
    setStroke(comp, COL.border, 1);
    comp.effects = shadowXS();

    const header = autoFrame("HORIZONTAL");
    header.itemSpacing = 8;
    header.counterAxisAlignItems = "CENTER";
    header.appendChild(inter("#", "Bold", 18, COL.blue));
    header.appendChild(inter("Scrape Pool Summary", "Semi Bold", 18, COL.textPrimary));
    comp.appendChild(header);

    comp.appendChild(divRect(288, COL.border));

    for (const [k, v] of [["Active targets", "3"], ["Dropped targets", "0"], ["Scrape interval", "15s"]]) {
      const row = autoFrame("HORIZONTAL");
      row.primaryAxisSizingMode = "FIXED";
      row.resize(288, 10);
      row.primaryAxisAlignItems = "SPACE_BETWEEN";
      row.counterAxisAlignItems = "CENTER";
      row.appendChild(inter(k, "Regular",  13, COL.textMuted));
      row.appendChild(inter(v, "Semi Bold", 13, COL.textPrimary));
      comp.appendChild(row);
    }
    place(comp);
  }

  // 13. PoolAccordion
  // Each item: 6px radius, 1px border, 8px margin-between items
  // Header: 10px 16px pad, title 14px Semi Bold, chevron
  // Open panel shows HealthPanel-style 5px left border + target rows
  {
    const comp = figma.createComponent();
    comp.name = "PoolAccordion";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(460, 10);
    comp.itemSpacing = 8;
    noFill(comp);

    const POOLS = [
      { title: "prometheus (3 / 3 up)",   border: COL.green,  targets: ["http://localhost:9090/metrics", "http://localhost:9091/metrics", "http://localhost:9092/metrics"] },
      { title: "alertmanager (1 / 2 up)", border: COL.yellow, targets: ["http://localhost:9093/metrics"] },
    ];

    for (const pool of POOLS) {
      const item = figma.createFrame();
      item.primaryAxisSizingMode = "AUTO";
      item.counterAxisSizingMode = "AUTO";
      item.cornerRadius = 6;
      setFill(item, COL.white);
      setStroke(item, COL.border, 1);

      const itemInner = wrapWithLeftBorder(item, pool.border, 5);
      itemInner.itemSpacing = 0;

      const hdr = figma.createFrame();
      hdr.layoutMode = "HORIZONTAL";
      hdr.primaryAxisSizingMode = "FIXED";
      hdr.counterAxisSizingMode = "AUTO";
      hdr.resize(455, 10);
      hdr.paddingTop = 10; hdr.paddingBottom = 10;
      hdr.paddingLeft = 16; hdr.paddingRight = 16;
      hdr.primaryAxisAlignItems = "SPACE_BETWEEN";
      hdr.counterAxisAlignItems = "CENTER";
      noFill(hdr);
      hdr.appendChild(inter(pool.title, "Semi Bold", 14, COL.textPrimary));
      hdr.appendChild(inter("▾", "Regular", 12, COL.textMuted));
      itemInner.appendChild(hdr);
      itemInner.appendChild(divRect(455, COL.border));

      for (let ti = 0; ti < pool.targets.length; ti++) {
        const tRow = figma.createFrame();
        tRow.layoutMode = "HORIZONTAL";
        tRow.primaryAxisSizingMode = "FIXED";
        tRow.counterAxisSizingMode = "AUTO";
        tRow.resize(460, 10);
        tRow.paddingTop = 8; tRow.paddingBottom = 8;
        tRow.paddingLeft = 16; tRow.paddingRight = 16;
        tRow.itemSpacing = 12;
        tRow.counterAxisAlignItems = "CENTER";
        tRow.fills = ti % 2 === 0 ? sf(COL.white) : sf(COL.surface);

        tRow.appendChild(mono(pool.targets[ti], 12, COL.blue, { textDecoration: "UNDERLINE" }));

        const pill = figma.createFrame();
        pill.layoutMode = "HORIZONTAL";
        pill.primaryAxisSizingMode = "AUTO"; pill.counterAxisSizingMode = "AUTO";
        pill.paddingTop = 2; pill.paddingBottom = 2;
        pill.paddingLeft = 6; pill.paddingRight = 6;
        pill.cornerRadius = 999;
        setFill(pill, COL.greenBg);
        pill.appendChild(inter("UP", "Semi Bold", 10, COL.greenFg));
        tRow.appendChild(pill);

        itemInner.appendChild(tRow);
        if (ti < pool.targets.length - 1) itemInner.appendChild(divRect(455, COL.border));
      }
      comp.appendChild(item);
    }
    place(comp);
  }

  // 14. SettingsPanel
  // 16px padding, 320px max-width, 8px radius, 1px border, md shadow
  // Group title 12px, item 13px, checkbox 16px
  {
    const comp = figma.createComponent();
    comp.name = "SettingsPanel";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "FIXED";
    comp.counterAxisSizingMode = "AUTO";
    comp.resize(320, 10);
    comp.paddingTop = 16; comp.paddingBottom = 16;
    comp.paddingLeft = 16; comp.paddingRight = 16;
    comp.itemSpacing = 12;
    comp.cornerRadius = 8;
    setFill(comp, COL.white);
    setStroke(comp, COL.border, 1);
    comp.effects = shadowMD();

    comp.appendChild(inter("DISPLAY", "Semi Bold", 12, COL.textMuted));

    for (const [label, checked] of [
      ["Show scrape duration", true ],
      ["Show sample count",    true ],
      ["Show dropped targets", false],
    ]) {
      const row = autoFrame("HORIZONTAL");
      row.itemSpacing = 8;
      row.counterAxisAlignItems = "CENTER";

      const box = figma.createFrame();
      box.resize(16, 16);
      box.cornerRadius = 2;
      if (checked) { setFill(box, COL.blue); }
      else         { setFill(box, COL.white); setStroke(box, COL.borderMid, 1); }
      row.appendChild(box);
      row.appendChild(inter(label, "Regular", 13, COL.textPrimary));
      comp.appendChild(row);
    }

    comp.appendChild(divRect(288, COL.border));
    comp.appendChild(inter("PAGINATION", "Semi Bold", 12, COL.textMuted));

    const inputRow = autoFrame("HORIZONTAL");
    inputRow.itemSpacing = 8;
    inputRow.counterAxisAlignItems = "CENTER";
    inputRow.appendChild(inter("Targets per page", "Regular", 13, COL.textPrimary));

    const numInput = figma.createFrame();
    numInput.layoutMode = "HORIZONTAL";
    numInput.primaryAxisSizingMode = "FIXED"; numInput.counterAxisSizingMode = "AUTO";
    numInput.resize(60, 10);
    numInput.paddingTop = 5; numInput.paddingBottom = 5;
    numInput.paddingLeft = 8; numInput.paddingRight = 8;
    numInput.counterAxisAlignItems = "CENTER";
    numInput.cornerRadius = 4;
    setFill(numInput, COL.white);
    setStroke(numInput, COL.borderMid, 1);
    numInput.appendChild(inter("20", "Regular", 13, COL.textPrimary));
    inputRow.appendChild(numInput);
    comp.appendChild(inputRow);
    place(comp);
  }

  // ── Row 4 ────────────────────────────────────────────────────────────────
  nextRow();

  // 15. FilterToolbar
  // Search input (32px h) + StateMultiSelect trigger (180px min-width, 32px h) + collapse btn (32x32)
  // 12px gap, 4px radius, 1px border
  {
    const comp = figma.createComponent();
    comp.name = "FilterToolbar";
    comp.layoutMode = "HORIZONTAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.itemSpacing = 12;
    comp.counterAxisAlignItems = "CENTER";
    noFill(comp);

    // Search input
    const search = figma.createFrame();
    search.layoutMode = "HORIZONTAL";
    search.primaryAxisSizingMode = "FIXED"; search.counterAxisSizingMode = "FIXED";
    search.resize(240, 32);
    search.paddingLeft = 10; search.paddingRight = 10;
    search.itemSpacing = 6;
    search.counterAxisAlignItems = "CENTER";
    search.cornerRadius = 4;
    setFill(search, COL.white);
    setStroke(search, COL.borderMid, 1);
    search.appendChild(inter("S",               "Regular", 14, COL.textSubtle));
    search.appendChild(inter("Filter by label...", "Regular", 13, COL.textSubtle));
    comp.appendChild(search);

    // State select (180px min-width)
    const sel = figma.createFrame();
    sel.layoutMode = "HORIZONTAL";
    sel.primaryAxisSizingMode = "FIXED"; sel.counterAxisSizingMode = "FIXED";
    sel.resize(180, 32);
    sel.paddingLeft = 10; sel.paddingRight = 8;
    sel.primaryAxisAlignItems = "SPACE_BETWEEN";
    sel.counterAxisAlignItems = "CENTER";
    sel.cornerRadius = 4;
    setFill(sel, COL.white);
    setStroke(sel, COL.borderMid, 1);
    sel.appendChild(inter("Any state", "Regular", 13, COL.textSecond));
    sel.appendChild(inter("▾",         "Regular", 12, COL.textSubtle));
    comp.appendChild(sel);

    // Collapse-all button (32×32 icon btn)
    const colBtn = figma.createFrame();
    colBtn.layoutMode = "HORIZONTAL";
    colBtn.primaryAxisSizingMode = "FIXED"; colBtn.counterAxisSizingMode = "FIXED";
    colBtn.resize(32, 32);
    colBtn.cornerRadius = 4;
    colBtn.primaryAxisAlignItems = "CENTER";
    colBtn.counterAxisAlignItems = "CENTER";
    setFill(colBtn, COL.white);
    setStroke(colBtn, COL.borderMid, 1);
    colBtn.appendChild(inter("-", "Bold", 14, COL.textSecond));
    comp.appendChild(colBtn);

    place(comp);
  }

  // 16. StateMultiSelect
  // 32px row h, 180px width, 4px radius, health-coloured pills per option
  // md shadow (open dropdown)
  {
    const comp = figma.createComponent();
    comp.name = "StateMultiSelect";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(180, 10);
    comp.paddingTop = 4; comp.paddingBottom = 4;
    comp.itemSpacing = 0;
    comp.cornerRadius = 4;
    setFill(comp, COL.white);
    setStroke(comp, COL.borderMid, 1);
    comp.effects = shadowMD();

    const OPTS = [
      { label: "Active",  bg: COL.greenBg,  fg: COL.greenFg  },
      { label: "Dropped", bg: COL.grayBg,   fg: COL.grayFg   },
      { label: "Unknown", bg: COL.yellowBg, fg: COL.yellowFg },
    ];

    for (const opt of OPTS) {
      const row = figma.createFrame();
      row.layoutMode = "HORIZONTAL";
      row.primaryAxisSizingMode = "FIXED"; row.counterAxisSizingMode = "FIXED";
      row.resize(180, 32);
      row.paddingLeft = 10; row.paddingRight = 10;
      row.itemSpacing = 8;
      row.counterAxisAlignItems = "CENTER";
      setFill(row, COL.white);

      const pill = figma.createFrame();
      pill.layoutMode = "HORIZONTAL";
      pill.primaryAxisSizingMode = "AUTO"; pill.counterAxisSizingMode = "AUTO";
      pill.paddingTop = 2; pill.paddingBottom = 2;
      pill.paddingLeft = 6; pill.paddingRight = 6;
      pill.cornerRadius = 999;
      pill.counterAxisAlignItems = "CENTER";
      setFill(pill, opt.bg);
      pill.appendChild(inter(opt.label, "Semi Bold", 11, opt.fg));
      row.appendChild(pill);
      comp.appendChild(row);
    }
    place(comp);
  }

  // ── Row 5 ────────────────────────────────────────────────────────────────
  nextRow();

  // 17. DataTable
  // Header: 8px 12px pad, border-bottom 2px, 11px Semi Bold uppercase
  // Cells: 6px 12px pad, border-bottom 1px, 12px Regular
  // State column: StatusBadge pill; endpoint column: monospace underlined link
  {
    const comp = figma.createComponent();
    comp.name = "DataTable";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "AUTO";
    comp.counterAxisSizingMode = "AUTO";
    comp.itemSpacing = 0;
    comp.cornerRadius = 4;
    setFill(comp, COL.white);
    setStroke(comp, COL.border, 1);

    const COL_W  = [220, 80, 180, 100]; // Endpoint, State, Labels, Scrape
    const TOTAL_W = COL_W.reduce((a, b) => a + b, 0);
    const HEADS   = ["Endpoint", "State", "Labels", "Last Scrape"];

    // Header row
    const hdrRow = figma.createFrame();
    hdrRow.layoutMode = "HORIZONTAL";
    hdrRow.primaryAxisSizingMode = "AUTO"; hdrRow.counterAxisSizingMode = "AUTO";
    hdrRow.itemSpacing = 0;
    setFill(hdrRow, COL.surface);

    HEADS.forEach((h, i) => {
      const cell = figma.createFrame();
      cell.layoutMode = "HORIZONTAL";
      cell.primaryAxisSizingMode = "FIXED"; cell.counterAxisSizingMode = "AUTO";
      cell.resize(COL_W[i], 10);
      cell.paddingTop = 8; cell.paddingBottom = 8;
      cell.paddingLeft = 12; cell.paddingRight = 12;
      cell.counterAxisAlignItems = "CENTER";
      noFill(cell);
      cell.appendChild(inter(h.toUpperCase(), "Semi Bold", 11, COL.textMuted));
      hdrRow.appendChild(cell);
    });
    comp.appendChild(hdrRow);

    // 2px divider after header
    const hdrDiv = figma.createRectangle();
    hdrDiv.resize(TOTAL_W, 2);
    hdrDiv.fills = sf(COL.border);
    comp.appendChild(hdrDiv);

    const DATA = [
      { ep: "localhost:9090/metrics", state: "UP",   stateOk: true,  labels: "job=prometheus", scrape: "2.3s ago" },
      { ep: "localhost:9091/metrics", state: "UP",   stateOk: true,  labels: "job=alertmgr",   scrape: "4.1s ago" },
      { ep: "localhost:9100/metrics", state: "DOWN", stateOk: false, labels: "job=node",       scrape: "32s ago"  },
    ];

    for (let ri = 0; ri < DATA.length; ri++) {
      const d = DATA[ri];

      const dataRow = figma.createFrame();
      dataRow.layoutMode = "HORIZONTAL";
      dataRow.primaryAxisSizingMode = "AUTO"; dataRow.counterAxisSizingMode = "AUTO";
      dataRow.itemSpacing = 0;
      dataRow.fills = ri % 2 === 0 ? sf(COL.white) : sf(COL.surface);

      // Endpoint cell
      const epCell = figma.createFrame();
      epCell.layoutMode = "HORIZONTAL";
      epCell.primaryAxisSizingMode = "FIXED"; epCell.counterAxisSizingMode = "AUTO";
      epCell.resize(COL_W[0], 10);
      epCell.paddingTop = 6; epCell.paddingBottom = 6;
      epCell.paddingLeft = 12; epCell.paddingRight = 12;
      epCell.counterAxisAlignItems = "CENTER";
      noFill(epCell);
      epCell.appendChild(mono(d.ep, 12, COL.blue, { textDecoration: "UNDERLINE" }));

      // State cell (pill badge)
      const stCell = figma.createFrame();
      stCell.layoutMode = "HORIZONTAL";
      stCell.primaryAxisSizingMode = "FIXED"; stCell.counterAxisSizingMode = "AUTO";
      stCell.resize(COL_W[1], 10);
      stCell.paddingTop = 6; stCell.paddingBottom = 6;
      stCell.paddingLeft = 12; stCell.paddingRight = 12;
      stCell.counterAxisAlignItems = "CENTER";
      noFill(stCell);
      const stPill = figma.createFrame();
      stPill.layoutMode = "HORIZONTAL";
      stPill.primaryAxisSizingMode = "AUTO"; stPill.counterAxisSizingMode = "AUTO";
      stPill.paddingTop = 2; stPill.paddingBottom = 2;
      stPill.paddingLeft = 6; stPill.paddingRight = 6;
      stPill.cornerRadius = 999;
      setFill(stPill, d.stateOk ? COL.greenBg : COL.redBg);
      stPill.appendChild(inter(d.state, "Semi Bold", 10, d.stateOk ? COL.greenFg : COL.redFg));
      stCell.appendChild(stPill);

      // Labels cell
      const lblCell = figma.createFrame();
      lblCell.layoutMode = "HORIZONTAL";
      lblCell.primaryAxisSizingMode = "FIXED"; lblCell.counterAxisSizingMode = "AUTO";
      lblCell.resize(COL_W[2], 10);
      lblCell.paddingTop = 6; lblCell.paddingBottom = 6;
      lblCell.paddingLeft = 12; lblCell.paddingRight = 12;
      lblCell.counterAxisAlignItems = "CENTER";
      noFill(lblCell);
      lblCell.appendChild(inter(d.labels, "Regular", 12, COL.textSecond));

      // Scrape cell
      const scrCell = figma.createFrame();
      scrCell.layoutMode = "HORIZONTAL";
      scrCell.primaryAxisSizingMode = "FIXED"; scrCell.counterAxisSizingMode = "AUTO";
      scrCell.resize(COL_W[3], 10);
      scrCell.paddingTop = 6; scrCell.paddingBottom = 6;
      scrCell.paddingLeft = 12; scrCell.paddingRight = 12;
      scrCell.counterAxisAlignItems = "CENTER";
      noFill(scrCell);
      scrCell.appendChild(inter(d.scrape, "Regular", 12, COL.textMuted));

      dataRow.appendChild(epCell);
      dataRow.appendChild(stCell);
      dataRow.appendChild(lblCell);
      dataRow.appendChild(scrCell);
      comp.appendChild(dataRow);
      if (ri < DATA.length - 1) comp.appendChild(divRect(TOTAL_W, COL.border));
    }
    place(comp);
  }

  // 18. InfoPageLayout
  // Max-width 1000px, gap 20px, mt 8px — centered stack of HealthPanel cards
  {
    const comp = figma.createComponent();
    comp.name = "InfoPageLayout";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "FIXED";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(1000, 580);
    comp.paddingTop = 8; comp.paddingBottom = 24;
    comp.paddingLeft = 24; comp.paddingRight = 24;
    comp.itemSpacing = 20;
    setFill(comp, COL.pageBg);

    comp.appendChild(inter("Targets", "Bold", 20, COL.textPrimary));

    // FilterToolbar strip
    const tb = figma.createFrame();
    tb.layoutMode = "HORIZONTAL";
    tb.primaryAxisSizingMode = "FIXED"; tb.counterAxisSizingMode = "FIXED";
    tb.resize(952, 32);
    tb.paddingLeft = 10; tb.paddingRight = 10;
    tb.itemSpacing = 12;
    tb.counterAxisAlignItems = "CENTER";
    tb.cornerRadius = 4;
    setFill(tb, COL.white);
    setStroke(tb, COL.border, 1);
    tb.appendChild(inter("Filter by label...", "Regular", 13, COL.textSubtle));
    comp.appendChild(tb);

    // Two HealthPanel-style accordion items
    const PANELS = [
      { title: "prometheus (3 / 3 up)",  border: COL.green  },
      { title: "node (1 / 3 up)",        border: COL.yellow },
    ];
    for (const p of PANELS) {
      const card = figma.createFrame();
      card.primaryAxisSizingMode = "AUTO";
      card.counterAxisSizingMode = "FIXED";
      card.resize(952, 10);
      card.cornerRadius = 8;
      setFill(card, COL.white);
      setStroke(card, COL.border, 1);

      const cardInner = wrapWithLeftBorder(card, p.border, 5);
      cardInner.primaryAxisSizingMode = "AUTO";
      cardInner.counterAxisSizingMode = "FILL";
      cardInner.paddingTop = 12; cardInner.paddingBottom = 12;
      cardInner.paddingLeft = 16; cardInner.paddingRight = 16;
      cardInner.itemSpacing = 6;
      cardInner.appendChild(inter(p.title, "Semi Bold", 14, COL.textPrimary));
      cardInner.appendChild(inter("3 targets  •  last scrape 2s ago", "Regular", 13, COL.textMuted));
      comp.appendChild(card);
    }
    place(comp);
  }

  // 19. PrometheusAppShell
  // Header: 56px, always-dark rgb(65,73,81), 0 20px h-pad
  // Logo gap 8px, logo-to-nav gap 32px, nav links gap 12px
  // Active NavButton = blue; ThemeToggle top-right; main padding 16px
  {
    const comp = figma.createComponent();
    comp.name = "PrometheusAppShell";
    comp.layoutMode = "VERTICAL";
    comp.primaryAxisSizingMode = "FIXED";
    comp.counterAxisSizingMode = "FIXED";
    comp.resize(1280, 800);
    comp.itemSpacing = 0;
    setFill(comp, COL.pageBg);

    // ── Header (always dark) ───────────────────────────
    const header = figma.createFrame();
    header.layoutMode = "HORIZONTAL";
    header.primaryAxisSizingMode = "FIXED"; header.counterAxisSizingMode = "FIXED";
    header.resize(1280, 56);
    header.paddingLeft = 20; header.paddingRight = 20;
    header.itemSpacing = 12;
    header.counterAxisAlignItems = "CENTER";
    setFill(header, COL.headerBg);

    // Logo group (icon + wordmark, 8px gap)
    const logoGrp = autoFrame("HORIZONTAL");
    logoGrp.itemSpacing = 8;
    logoGrp.counterAxisAlignItems = "CENTER";
    logoGrp.appendChild(inter("P", "Bold", 18, COL.orange));
    logoGrp.appendChild(inter("Prometheus", "Bold", 15, COL.white));
    header.appendChild(logoGrp);

    // 32px spacer between logo and nav links
    const spacer = figma.createFrame();
    spacer.layoutMode = "HORIZONTAL";
    spacer.primaryAxisSizingMode = "FIXED"; spacer.counterAxisSizingMode = "FIXED";
    spacer.resize(32, 1);
    noFill(spacer);
    header.appendChild(spacer);

    // Nav links (12px gap between items = itemSpacing on header)
    for (const [label, active] of [["Status", true], ["Alerts", false], ["Graph", false], ["Config", false], ["Help", false]]) {
      const btn = figma.createFrame();
      btn.layoutMode = "HORIZONTAL";
      btn.primaryAxisSizingMode = "AUTO"; btn.counterAxisSizingMode = "AUTO";
      btn.paddingTop = 6; btn.paddingBottom = 6;
      btn.paddingLeft = 12; btn.paddingRight = 12;
      btn.cornerRadius = 4;
      btn.counterAxisAlignItems = "CENTER";
      if (active) {
        setFill(btn, COL.blue);
      } else {
        btn.fills = [{ type: "SOLID", color: COL.white, opacity: 0.0 }];
      }
      btn.appendChild(inter(label, "Regular", 13, COL.navText));
      header.appendChild(btn);
    }

    // Right-side ThemeToggle (32×32)
    const themeBtn = figma.createFrame();
    themeBtn.layoutMode = "HORIZONTAL";
    themeBtn.primaryAxisSizingMode = "FIXED"; themeBtn.counterAxisSizingMode = "FIXED";
    themeBtn.resize(32, 32);
    themeBtn.cornerRadius = 4;
    themeBtn.primaryAxisAlignItems = "CENTER";
    themeBtn.counterAxisAlignItems = "CENTER";
    themeBtn.fills = [{ type: "SOLID", color: COL.white, opacity: 0.1 }];
    themeBtn.appendChild(inter("D", "Bold", 13, COL.white));
    header.appendChild(themeBtn);

    comp.appendChild(header);

    // ── Main content area ──────────────────────────────
    const main = figma.createFrame();
    main.layoutMode = "VERTICAL";
    main.primaryAxisSizingMode = "FIXED"; main.counterAxisSizingMode = "FIXED";
    main.resize(1280, 744);
    main.paddingTop = 16; main.paddingBottom = 16;
    main.paddingLeft = 16; main.paddingRight = 16;
    main.itemSpacing = 16;
    setFill(main, COL.pageBg);

    main.appendChild(inter("Targets", "Bold", 20, COL.textPrimary));

    const toolStrip = figma.createFrame();
    toolStrip.resize(1248, 32);
    toolStrip.cornerRadius = 4;
    setFill(toolStrip, COL.white);
    setStroke(toolStrip, COL.border, 1);
    main.appendChild(toolStrip);

    const content = figma.createFrame();
    content.resize(1248, 636);
    content.cornerRadius = 4;
    setFill(content, COL.white);
    setStroke(content, COL.border, 1);
    main.appendChild(content);

    comp.appendChild(main);
    place(comp);
  }
}

// ─── Main ───────────────────────────────────────────────────────────────────

async function main() {
  try {
    figma.notify("🔥 Prometheus DS Bootstrap starting...", { timeout: 2000 });

    await createVariableCollections();
    await createTextStyles();
    await createEffectStyles();
    await createComponentScaffolds();

    figma.notify("✅ Prometheus DS Bootstrap complete!", { timeout: 5000 });
  } catch (error) {
    const msg = (error && error.message) ? error.message : String(error);
    figma.notify("❌ " + msg, { error: true, timeout: 8000 });
    console.error("Plugin error:", error);
  } finally {
    figma.closePlugin();
  }
}

main();
