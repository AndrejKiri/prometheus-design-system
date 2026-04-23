// Prometheus Design System — Figma Bootstrap Plugin
// Generated 2026-04-22 from tokens.json (source: visual-audit)
//
// Font rules:
//   "Semi Bold" (with space) not "SemiBold" — Figma crashes on the latter.
//   "Courier New" for monospace — DejaVu/Roboto Mono are not bundled.
//   "Inter" is the safe fallback — always available.
//   loadFontAsync wrapped in try/catch per weight/family.

// ─── Token Definitions ──────────────────────────────────────────────────────

const BRAND_COLORS = {
  "brand/brand-blue-light": { r: 0.133,  g: 0.545,  b: 0.902 },
  "brand/brand-blue-dark":  { r: 0.098,  g: 0.443,  b: 0.761 },
  "brand/nav-slate":        { r: 0.255,  g: 0.286,  b: 0.318 }
};

const STATUS_COLORS = {
  ok: {
    light: { bg: { r: 0.8275, g: 0.9765, b: 0.8471 }, text: { r: 0.1686, g: 0.5412, b: 0.2431 }, border: { r: 0, g: 0, b: 0 } },
    dark:  { bg: { r: 0.1686, g: 0.5412, b: 0.2431 }, text: { r: 0.8275, g: 0.9765, b: 0.8471 }, border: { r: 0, g: 0, b: 0 } }
  },
  error: {
    light: { bg: { r: 1.0,    g: 0.9608, b: 0.9608 }, text: { r: 0.7882, g: 0.1647, b: 0.1647 }, border: { r: 0, g: 0, b: 0 } },
    dark:  { bg: { r: 0.7882, g: 0.1647, b: 0.1647 }, text: { r: 1.0,    g: 0.9608, b: 0.9608 }, border: { r: 0, g: 0, b: 0 } }
  },
  info: {
    light: { bg: { r: 0.1333, g: 0.5451, b: 0.902  }, text: { r: 0.0941, g: 0.3922, b: 0.6706 }, border: { r: 0, g: 0, b: 0 } },
    dark:  { bg: { r: 0.1333, g: 0.5451, b: 0.902  }, text: { r: 0.4549, g: 0.7529, b: 0.9882 }, border: { r: 0, g: 0, b: 0 } }
  }
};

const SURFACE_COLORS = {
  "surface/page-bg":        { light: { r: 1.0,    g: 1.0,    b: 1.0    }, dark: { r: 0.1412, g: 0.1412, b: 0.1412 } },
  "surface/card-bg":        { light: { r: 1.0,    g: 1.0,    b: 1.0    }, dark: { r: 0.1804, g: 0.1804, b: 0.1804 } },
  "surface/nav-bg":         { light: { r: 0.2549, g: 0.2863, b: 0.3176 }, dark: { r: 0.2549, g: 0.2863, b: 0.3176 } },
  "surface/label-badge-bg": { light: { r: 0.9451, g: 0.9529, b: 0.9608 }, dark: { r: 0.2039, g: 0.2275, b: 0.2510 } },
  "surface/stats-badge-bg": { light: { r: 0.9451, g: 0.9529, b: 0.9608 }, dark: { r: 0.2039, g: 0.2275, b: 0.2510 } }
};

const TEXT_COLORS = {
  "text/primary":       { light: { r: 0.0,    g: 0.0,    b: 0.0    }, dark: { r: 0.7882, g: 0.7882, b: 0.7882 } },
  "text/inverted":      { light: { r: 1.0,    g: 1.0,    b: 1.0    }, dark: { r: 1.0,    g: 1.0,    b: 1.0    } },
  "text/muted":         { light: { r: 0.5255, g: 0.5569, b: 0.5882 }, dark: { r: 0.5255, g: 0.5569, b: 0.5882 } },
  "text/info-callout":  { light: { r: 0.0941, g: 0.3922, b: 0.6706 }, dark: { r: 0.4549, g: 0.7529, b: 0.9882 } },
  "text/label-badge":   { light: { r: 0.2039, g: 0.2275, b: 0.2510 }, dark: { r: 0.6784, g: 0.7098, b: 0.7412 } }
};

const SPACING = {
  "spacing/xs":    4,
  "spacing/sm":    8,
  "spacing/sm-lg": 12,
  "spacing/md":    16,
  "spacing/lg":    24
};

const RADIUS = {
  "radius/sm":       4,
  "radius/pill":     1000,
  "radius/pill-max": 16000
};

const TEXT_STYLES = [
  { name: "heading/card-title", family: "Inter",       size: 18, weight: 600, lineHeight: 1.4  },
  { name: "heading/section",    family: "Inter",       size: 16, weight: 600, lineHeight: 1.4  },
  { name: "body/default",       family: "Inter",       size: 14, weight: 400, lineHeight: 1.55 },
  { name: "label/button",       family: "Inter",       size: 14, weight: 600, lineHeight: 1.0  },
  { name: "label/badge",        family: "Inter",       size: 12, weight: 400, lineHeight: 1.0  },
  { name: "code/block",         family: "Courier New", size: 16, weight: 400, lineHeight: 1.5  },
  { name: "code/inline",        family: "Courier New", size: 14, weight: 400, lineHeight: 1.0  }
];

const SHADOW_STYLES = [
  {
    name: "elevation/card",
    effects: [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.05 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true, blendMode: "NORMAL" },
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.10 }, offset: { x: 0, y: 1 }, radius: 2, spread: 0, visible: true, blendMode: "NORMAL" }
    ]
  }
];

// ─── Variable Collections ───────────────────────────────────────────────────

async function createVariableCollections() {
  figma.notify("Creating variable collections...");

  const brandColl = figma.variables.createVariableCollection("Brand");
  const brandMode = brandColl.modes[0].modeId;
  for (const [name, rgb] of Object.entries(BRAND_COLORS)) {
    const v = figma.variables.createVariable(name, brandColl, "COLOR");
    v.setValueForMode(brandMode, rgb);
  }

  const spacingColl = figma.variables.createVariableCollection("Spacing");
  const spacingMode = spacingColl.modes[0].modeId;
  for (const [name, value] of Object.entries(SPACING)) {
    const v = figma.variables.createVariable(name, spacingColl, "FLOAT");
    v.setValueForMode(spacingMode, value);
  }

  const radiusColl = figma.variables.createVariableCollection("Radius");
  const radiusMode = radiusColl.modes[0].modeId;
  for (const [name, value] of Object.entries(RADIUS)) {
    const v = figma.variables.createVariable(name, radiusColl, "FLOAT");
    v.setValueForMode(radiusMode, value);
  }

  const statusColl = figma.variables.createVariableCollection("Status Colors");
  const lightId = statusColl.modes[0].modeId;
  statusColl.renameMode(lightId, "Light");
  const darkId = statusColl.addMode("Dark");
  for (const [status, modes] of Object.entries(STATUS_COLORS)) {
    for (const suffix of ["bg", "text", "border"]) {
      const v = figma.variables.createVariable(`status/${status}-${suffix}`, statusColl, "COLOR");
      v.setValueForMode(lightId, modes.light[suffix]);
      v.setValueForMode(darkId,  modes.dark[suffix]);
    }
  }

  for (const [collName, tokenMap] of [["Surface", SURFACE_COLORS], ["Text", TEXT_COLORS]]) {
    const coll = figma.variables.createVariableCollection(collName);
    const lId = coll.modes[0].modeId;
    coll.renameMode(lId, "Light");
    const dId = coll.addMode("Dark");
    for (const [name, modes] of Object.entries(tokenMap)) {
      const v = figma.variables.createVariable(name, coll, "COLOR");
      v.setValueForMode(lId, modes.light);
      v.setValueForMode(dId, modes.dark);
    }
  }
}

// ─── Text Styles (with font fallback) ───────────────────────────────────────

async function createTextStyles() {
  figma.notify("Creating text styles...");
  for (const def of TEXT_STYLES) {
    const weightStyle = def.weight >= 700 ? "Bold"
      : def.weight >= 600 ? "Semi Bold"
      : def.weight >= 500 ? "Medium"
      : "Regular";

    let resolvedFamily = def.family;
    let resolvedStyle  = weightStyle;

    try {
      await figma.loadFontAsync({ family: def.family, style: weightStyle });
    } catch (_e) {
      try {
        await figma.loadFontAsync({ family: def.family, style: "Regular" });
        resolvedStyle = "Regular";
      } catch (_e2) {
        try {
          await figma.loadFontAsync({ family: "Inter", style: weightStyle });
          resolvedFamily = "Inter";
        } catch (_e3) {
          await figma.loadFontAsync({ family: "Inter", style: "Regular" });
          resolvedFamily = "Inter";
          resolvedStyle  = "Regular";
        }
      }
    }

    const style = figma.createTextStyle();
    style.name     = def.name;
    style.fontName = { family: resolvedFamily, style: resolvedStyle };
    style.fontSize = def.size;
    style.lineHeight = { value: def.lineHeight * 100, unit: "PERCENT" };
  }
}

// ─── Effect Styles ──────────────────────────────────────────────────────────

async function createEffectStyles() {
  figma.notify("Creating elevation styles...");
  for (const def of SHADOW_STYLES) {
    const style = figma.createEffectStyle();
    style.name    = def.name;
    style.effects = def.effects;
  }
}

// ─── Main ───────────────────────────────────────────────────────────────────

async function main() {
  try {
    figma.notify("Prometheus DS Bootstrap starting...", { timeout: 2000 });
    await createVariableCollections();
    await createTextStyles();
    await createEffectStyles();
    figma.notify("Bootstrap complete! 3 brand colors, 5 surface, 5 text, 3 status, 5 spacing, 3 radius, 7 text styles, 1 shadow.", { timeout: 5000 });
  } catch (error) {
    const msg = error && error.message ? error.message : String(error);
    figma.notify("Error: " + msg, { error: true, timeout: 8000 });
    console.error("Plugin error:", error);
  } finally {
    figma.closePlugin();
  }
}

main();
