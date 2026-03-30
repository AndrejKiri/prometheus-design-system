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
  { name: "code/default",    family: "DejaVu Sans Mono", size: 13, weight: 400, lineHeight: 1.6 },
  { name: "code/metric",     family: "DejaVu Sans Mono", size: 13, weight: 500, lineHeight: 1.5 },
  { name: "code/label",      family: "DejaVu Sans Mono", size: 11, weight: 400, lineHeight: 1.5 },
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
    const style = figma.createTextStyle();
    style.name = def.name;

    await figma.loadFontAsync({ family: def.family, style: def.weight >= 700 ? "Bold" : def.weight >= 600 ? "SemiBold" : def.weight >= 500 ? "Medium" : "Regular" });

    style.fontName = {
      family: def.family,
      style: def.weight >= 700 ? "Bold" : def.weight >= 600 ? "SemiBold" : def.weight >= 500 ? "Medium" : "Regular"
    };
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

// ─── Component Scaffold Creation ────────────────────────────────────────────

async function createComponentScaffolds() {
  figma.notify("Creating component scaffolds...");

  const page = figma.createPage();
  page.name = "Components";

  const componentNames = [
    "StatusBadge", "HealthPanel", "LabelBadge", "FilterToolbar",
    "InfoCard", "InfoPageLayout", "DataTable", "KeyValueTable",
    "CodeBlock", "SeriesName", "EndpointLink", "EmptyState",
    "ErrorAlert", "PoolAccordion", "NavButton", "StateMultiSelect",
    "SettingsPanel", "ThemeToggle", "PrometheusAppShell"
  ];

  let xOffset = 0;
  for (const name of componentNames) {
    const component = figma.createComponent();
    component.name = name;
    component.resize(200, 100);
    component.x = xOffset;
    component.y = 0;

    // Add placeholder text
    await figma.loadFontAsync({ family: "Inter", style: "Regular" });
    const text = figma.createText();
    text.characters = name;
    text.fontSize = 14;
    text.fontName = { family: "Inter", style: "Regular" };
    component.appendChild(text);
    text.x = 16;
    text.y = 40;

    // Set auto-layout
    component.layoutMode = "VERTICAL";
    component.paddingTop = 16;
    component.paddingBottom = 16;
    component.paddingLeft = 16;
    component.paddingRight = 16;
    component.itemSpacing = 8;
    component.primaryAxisSizingMode = "AUTO";
    component.counterAxisSizingMode = "AUTO";

    xOffset += 240;
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
    figma.notify("❌ Error: " + error.message, { error: true, timeout: 5000 });
    console.error(error);
  } finally {
    figma.closePlugin();
  }
}

main();
