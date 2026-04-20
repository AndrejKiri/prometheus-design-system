---
name: reverse-engineer-design-system
description: >
  Reverse-engineer a design system from any existing web application. Use when asked to audit
  a website or web app, extract its design tokens, components, and patterns, document
  inconsistencies, and produce a complete static documentation site plus a Figma bootstrap
  plugin. Covers scope assessment, authentication, multi-tool workflows (Perplexity Computer,
  Claude Code, Claude Cowork), browsing pages, cataloging UI elements, spotting inconsistencies,
  extracting tokens, and generating a deployable design system site. Also covers Figma plugin
  creation with tested font-fallback patterns.
metadata:
  author: AndrejKiri
  version: '2.1'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
---

# Reverse-Engineer a Design System

## When to Use This Skill

Use when asked to:
- Audit a website or web app's UI for patterns, tokens, and inconsistencies
- Extract a design system from an existing codebase or live site
- Produce a design system documentation site from an existing UI
- Create a Figma bootstrap plugin from extracted design tokens

## Core Principle

**Derive, not invent.** Every token, component, and pattern must come from the actual application being audited. Never invent design decisions — extract and document what exists, then resolve inconsistencies with documented reasoning and a canonical choice.

---

## Multi-Tool Workflow

This skill can be executed by different tools. Each has different strengths. Before starting, identify which tool you are and follow the appropriate path.

### If you are Perplexity Computer

You can execute the full workflow end-to-end. You have Playwright (headless browser), web search, file generation, deployment, and visual QA. Follow all phases sequentially.

### If you are Claude Code

You have strong filesystem access and code generation but **no built-in browser**. You need Playwright configured as an MCP server, or you must work from source code only.

**If Playwright MCP is available:** Follow all phases, using the Playwright MCP for browsing and screenshots.

**If no browser access:** You cannot do Phase 1 (visual audit) yourself. Instead:
1. Tell the user: *"I don't have browser access. To complete the visual audit, you have two options: (a) Run Phase 1 in Claude Cowork or Perplexity Computer, which can browse the live site, then come back to me with the results saved to `audit-results.json` in the project folder. (b) Give me access to the source code repository, and I'll do a source-only audit — I can extract tokens and component structure from code, but I won't be able to spot visual inconsistencies or take screenshots."*
2. If the user provides source code, skip to Phase 1-Source (below) and then continue from Phase 2.
3. If the user provides an `audit-results.json` from another tool, read it and continue from Phase 2.

### If you are Claude Cowork

You can browse via Computer Use (screen interaction) or the Chrome extension, and you can create files in the project folder. However:

- **You cannot run headless Playwright** — you interact with the browser visually, which is slower
- **You cannot run Python batch scripts** to edit 30+ HTML files simultaneously
- **You are best suited for Phase 0 (scope assessment) and Phase 1 (visual audit)**

Tell the user: *"I can audit the website and catalog all patterns, take screenshots, and identify inconsistencies. For generating the full documentation site (30+ HTML files), Claude Code is better suited. Here's how to hand off: I'll save my audit findings to `audit-results.json` and screenshots to `screenshots/` in the project folder. Then open Claude Code pointed at the same folder and ask it to continue from Phase 2."*

### Shared Project Folder Pattern

When using multiple tools together, all tools must point at the **same project folder**. Create a `CLAUDE.md` file in the project root with:

```markdown
# Design System Project

## Target Application
- URL: <app-url>
- Source repo: <repo-url or "N/A">
- Auth: <see auth section below>

## Scope
- Focus areas: <selected areas from Phase 0>
- Estimated pages: <count>

## Progress
- [ ] Phase 0: Scope assessment
- [ ] Phase 1: Visual audit (tool: ___)
- [ ] Phase 1b: Source audit (tool: ___)
- [ ] Phase 2: Token extraction
- [ ] Phase 3: Component extraction
- [ ] Phase 4: Documentation site
- [ ] Phase 5: Figma plugin
- [ ] Phase 6: Deploy + QA

## Handoff Files
- `audit-results.json` — structured audit findings (schema: [Appendix A — audit-results.json](#audit-resultsjson))
- `tokens.json` — extracted design tokens (schema: [Appendix A — tokens.json](#tokensjson))
- `components.json` — component inventory (schema: [Appendix A — components.json](#componentsjson))
- `source-audit.json` — source code findings, optional (schema: [Appendix A — source-audit.json](#source-auditjson-optional))
- `screenshots/` — reference screenshots
```

Update the progress checkboxes as you complete each phase. The next tool reads this file to know where to pick up.

### Validating Handoff Files

After producing any handoff file, run the validator script:

Save the validator script from [Appendix B](#appendix-b-handoff-validator-script) to `validate-handoff.py` in your project directory, then run:

```bash
python validate-handoff.py <project-directory>
```

The validator checks all three JSON files for:
- Required fields and correct types/enums
- Cross-reference integrity: INC IDs, token names, pattern names, slugs
- Dark mode consistency: if audit says `has_dark_mode: true`, tokens must have `dark` values
- Screenshot file existence
- Duplicate detection (IDs, slugs)

The script is progressive — it validates whatever files exist. Run it after Phase 1 with just `audit-results.json`, after Phase 2 with audit + tokens, and after Phase 3 with all three. Exit code 0 = pass, 1 = fail, 2 = missing required files.

---

## Phase 0: Scope Assessment and Authentication

**This phase MUST run before anything else.** Do not skip it.

### 0.1 Gather Authentication Info

Ask the user:

1. **URL:** "What is the URL of the application to audit?"
2. **Authentication:** "Does this application require login? If yes, please provide credentials (username/password, SSO details, or API token). I need these to access all pages."
3. **Source code:** "Do you have access to the source code repository? If yes, what is the repo URL? This helps extract exact token values instead of approximating from the rendered UI."
4. **GitHub repo (for action items):** "Do you want action items linked to a GitHub repository? If yes, provide the repo URL (e.g., `https://github.com/org/repo`)."

If authentication is required, test it immediately:

```javascript
// Test login before proceeding
await page.goto(loginUrl);
await page.fill('input[name="username"]', username);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
// Verify login succeeded by checking for a known authenticated element
await page.waitForSelector('<authenticated-element>', { timeout: 10000 });
```

If login fails, stop and ask the user for corrected credentials. Do not proceed with a partial audit.

### 0.2 Discover All Routes

Before committing to a full audit, discover the scope of the application:

```javascript
// Strategy 1: Crawl navigation links from the authenticated home page
const navLinks = await page.evaluate(() => {
  const links = document.querySelectorAll('a[href], nav a, [role="navigation"] a');
  return [...new Set([...links].map(a => a.href))].filter(h => h.startsWith(window.location.origin));
});

// Strategy 2: If source code is available, parse route definitions
// React Router: grep -r "path=" src/ --include="*.tsx" --include="*.jsx"
// Next.js: ls pages/ or app/
// Vue Router: grep -r "path:" src/router/
```

### 0.3 Assess Scope and Present Options

Count the discovered routes and categorize them. Present the user with a scope assessment:

```
I found [N] distinct routes in the application:

CORE UI (always included):
- Main navigation pages: [list with URLs]
- Settings/config pages: [list]

DATA VIEWS (include if data is populated):
- Dashboard/list pages: [list]
- Detail/item pages: [list]

ADMIN/SYSTEM (optional — often less UI-rich):
- Admin panels: [list]
- System status pages: [list]

EDGE CASES (can skip for first pass):
- Error pages, empty states, onboarding flows: [list]

Estimated effort by scope:
- Core only (~[N] pages): ~[X] components, manageable in one pass
- Core + Data views (~[N] pages): ~[X] components, recommended scope
- Full application (~[N] pages): ~[X] components, comprehensive but large

Which scope would you like me to focus on?
```

**Guidelines for scope tiers:**
- **< 15 pages:** Audit everything. No scoping needed.
- **15-30 pages:** Recommend "Core + Data views." Flag admin/system pages as optional.
- **30+ pages:** Strongly recommend focusing on a subset. Let the user choose which areas matter most. You can always expand later.

Wait for the user's response before proceeding. The selected scope defines which pages you visit in Phase 1.

### 0.4 Check for Pre-Seeded Data

Some applications show empty states when there's no data. Ask the user:

*"Some pages may look different or empty without sample data (e.g., dashboards need data sources, alert pages need configured alerts). Is this instance populated with representative data? If not, which pages might show empty states?"*

Document which pages have empty states vs. populated views — both are worth screenshotting, as empty states are a component too.

---

## Phase 1: Audit the Application (Visual)

This phase requires browser access (Playwright, Computer Use, or Chrome extension).

### 1.1 Browse Every Page in Scope

Use Playwright to systematically visit every page within the selected scope. Take screenshots of each page.

```javascript
const { chromium } = await import("playwright");
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1400, height: 900 } });
const page = await context.newPage();

// If authentication is needed, log in first
// <insert login steps from 0.1>

// Visit each route, screenshot, and catalog what you see
for (const url of scopedRoutes) {
  await page.goto(url, { waitUntil: "networkidle" });
  const screenshot = await page.screenshot({ type: "jpeg", quality: 85 });
  // Save to screenshots/ directory with page name
}
```

For each page, document:
- The URL and page name
- Every visible UI element type (badges, cards, tables, buttons, inputs, panels, accordions, etc.)
- Color values, font sizes, spacing, border radii you observe
- Interactive patterns (filters, sorts, collapses, toggles)
- Interactive states: expand every accordion, click every tab, hover buttons, trigger dropdowns. Screenshot each state.

### 1.2 Catalog Every UI Pattern

Create a comprehensive inventory. For each pattern, record:

| Pattern | Pages Found | Count | Variations |
|---------|-------------|-------|------------|
| Status badge | Alerts, Targets, Rules | 4 pages | 3 different implementations |
| Filter toolbar | Alerts, Targets, Rules, SD | 4 pages | Different prop combinations |
| Sortable table | Flags, TSDB Status | 2 pages | One with search, one without |

This is the most important step — you must be exhaustive within the selected scope. Visit every page, scroll to the bottom, expand every accordion, click every tab. Miss nothing.

### 1.3 Identify Inconsistencies

This is where the real value is. Compare how the same pattern is implemented across different pages:

- **Same concept, different implementation** — e.g., status badges using different CSS classes on different pages
- **Hardcoded values vs. tokens** — inline colors/spacing instead of variables
- **Missing normalization** — same status displayed differently (e.g., "UP" vs "up" vs "active")
- **Style drift** — panels with borders on one page, without on another
- **Duplicated logic** — filter bars rebuilt from scratch on each page instead of shared

For each inconsistency, document:
1. What is inconsistent (with exact file paths/line numbers if source available)
2. Table showing the variants across pages
3. Which variant should be canonical and why
4. The concrete fix (code diff if possible)

### 1.4 Save Audit Results

Save structured findings to `audit-results.json` in the project folder. **See [Appendix A](#appendix-a-handoff-file-schemas) for the full JSON schema with all required fields, types, and enums.** The key sections are:

- `scope` (required) — tier (`core`, `core-plus-data`, `full`, `custom`), route counts
- `pages_audited` (required) — one entry per page with URL, name, screenshot path, elements list, `has_data` boolean
- `patterns` (required) — every UI pattern with PascalCase name, pages, instance_count, variation_count, category enum (`navigation`, `data-display`, `input`, `feedback`, `layout`, `overlay`, `media`, `utility`), observed styles
- `inconsistencies` (required) — each with unique ID (e.g., `INC-001`), severity enum (`critical`, `major`, `minor`, `cosmetic`), type enum (`implementation-drift`, `hardcoded-values`, `missing-normalization`, `style-drift`, `duplicated-logic`, `accessibility`, `responsive`), variants array (min 2), canonical choice with reasoning
- `raw_observations` (required) — all colors, fonts, spacing values observed across the app, plus `has_dark_mode` and `theming_approach`

**Cross-reference checks before saving:**
- Every element name in `pages_audited[].elements` must have a matching `patterns[]` entry
- Every screenshot path must point to an actual file in `screenshots/`
- Every inconsistency must reference pages that exist in `pages_audited`

Save screenshots to `screenshots/` directory. **Run `python validate-handoff.py .` and fix any errors before handing off.** This file is the handoff artifact — any tool can read it to continue from Phase 2.

---

## Phase 1-Source: Source Code Audit (Alternative/Supplement)

Use this when you have access to the source repository. This can supplement the visual audit or replace it when no browser is available.

```bash
git clone --depth 1 <repo-url> source-code
```

Read component files, CSS modules, and theme configurations. Map each UI element to its source file. Extract exact token values from:
- CSS custom properties / CSS-in-JS theme objects
- CSS module files (`.module.css`)
- Shared style constants
- Theme configuration files (e.g., Mantine theme, MUI theme, Tailwind config)
- Package.json for framework/library versions

**Priority reading order for large codebases (1000+ files):**
1. `package.json` — framework, UI library, CSS approach
2. Theme config file (search for `theme`, `tokens`, `colors` in config files)
3. Route definitions (React Router config, pages directory, etc.)
4. Shared/common components directory
5. Layout/shell components (header, sidebar, footer)
6. Page-level components (one per route in scope)

Save source findings to `source-audit.json`. **See [Appendix A — source-audit.json](#source-auditjson-optional) for the full schema.** Must include: `tech_stack` (framework, CSS approach, versions), `theme_config` (file path, format enum, raw values), `route_definitions`, and `component_files` mapping pattern names to source file paths.

---

## Phase 2: Extract Tokens

Read `audit-results.json` (and `source-audit.json` if available). Extract every design token into structured categories.

### Color Tokens
- **Brand colors** — logo, header, primary accent
- **Health/status colors** — the semantic color system (ok/error/warning/info/unknown or equivalent) with light AND dark mode variants for background, text, and border
- **Surface colors** — page background, card background, code block background
- **Text colors** — primary, secondary, tertiary, muted

### Spacing Tokens
- Named scale (xs, sm, md, lg, xl) with pixel values
- Specific layout measurements (header height, sidebar width, card padding, gap sizes)

### Typography Tokens
- Font families (body, monospace, display)
- Font size scale
- Font weight usage
- Line height values
- Categorized: headings, body, labels, code

### Border Radius Tokens
- Named scale (sm, default, md, lg, pill)

### Elevation Tokens
- Shadow definitions at each level, with light AND dark mode variants

Save to `tokens.json` in the project folder. **See [Appendix A — tokens.json](#tokensjson) for the full schema.** Key requirements:

- All color categories are required: `brand`, `status`, `surface`, `text`, `border`
- Status colors must have `light` object with `bg`, `text`, `border` — plus `dark` if the app has dark mode
- Typography requires both `families` (font stacks + Figma-safe names) and `styles` (each with slash-separated name, category enum, weight as integer, unitless line-height)
- Pre-compute `figma_rgb` (0-1 range) for brand colors and `figma_effects` for shadows — this saves Phase 5 from doing conversions
- `source` field must be `visual-audit`, `source-code`, or `both` — this tells Phase 4 whether values are exact or approximate

**Run `python validate-handoff.py .` after saving.** It checks:
- `app_url` matches `audit-results.json`
- If `audit-results.json` reports `has_dark_mode: true`, status/surface/text entries must have `dark` values
- All figma_rgb values are in 0-1 range
- Typography styles have heading, body, and code categories
- Font family references resolve

---

## Phase 3: Extract Components

Read `audit-results.json` and `tokens.json`. Group the UI patterns into reusable components. For each component, document:

1. **Name** — clear, PascalCase (e.g., StatusBadge, FilterToolbar, HealthPanel)
2. **Description** — what it does, where it appears
3. **Source files** — which files in the codebase implement it (if source available)
4. **Props/API** — the properties it accepts (name, type, default, description)
5. **Variants** — all visual states (with mock renders)
6. **Layout specs** — pixel measurements for height, padding, font size, border radius
7. **Do/Don't** — usage guidelines
8. **Accessibility** — ARIA labels, contrast, keyboard support
9. **Code example** — how to use it

### Categorize by Complexity

- **Simple** — stateless, few props, thin wrapper (EmptyState, ErrorAlert, InfoCard)
- **Medium** — some internal state or composition (CodeBlock, KeyValueTable, HealthPanel)
- **Complex** — significant interactivity (DataTable, FilterToolbar, AppShell)

Save to `components.json` in the project folder. **See [Appendix A — components.json](#componentsjson) for the full schema.** Key requirements:

- Each component needs: `name` (PascalCase), `slug` (lowercase-hyphenated, used for filename), `complexity` enum, `category` enum
- `variants` array (min 1) with optional `mock_css_class` and `mock_html` for Phase 4 to render visual examples
- `layout.specs` array (min 1) with CSS property/value pairs and optional token cross-references
- `dos_and_donts` array (min 1) with `type` enum (`do`/`dont`)
- `related_inconsistencies` links to IDs from `audit-results.json`
- `action_items` array for the PR-style task cards page — each with `priority` enum (`p0-critical` through `p3-low`), `effort` enum (`easy`/`medium`/`hard`), and `labels` array

**Run `python validate-handoff.py .` after saving.** It checks:
- Every component `name` matches a pattern in `audit-results.json`
- `tokens_used` in variants reference names that exist in `tokens.json`
- All `slug` values are unique (no duplicates)
- `related_inconsistency` IDs exist in `audit-results.json`
- Action item IDs are unique, enums are valid

---

## Phase 4: Build the Documentation Site

Read `tokens.json`, `components.json`, and `audit-results.json`. Produce a static HTML/CSS/JS documentation site — no frameworks, no build step, no dependencies. Every page is a self-contained HTML file.

### File Structure

```
design-system/
├── index.html                      # Home page with card grid
├── tokens.html                     # Token documentation with visual swatches
├── icons.html                      # Icon inventory (if applicable)
├── components.html                 # Component catalog overview
├── components/                     # Individual component pages
│   └── component-name.html
├── patterns.html                   # Composition patterns
├── action-items.html               # PR-style task cards for fixes
├── audit-report.html               # Full audit findings
├── inconsistencies.html            # Inconsistency resolution log
├── changelog.html                  # Version history
├── figma.html                      # Figma plugin documentation
├── figma-plugin/                   # Figma bootstrap plugin
│   ├── code.js
│   └── manifest.json
├── screenshots/                    # Reference screenshots from the live app
├── styles.css                      # Single global stylesheet
├── main.js                         # Vanilla JS for interactivity
└── README.md
```

### CSS Architecture

Use a single stylesheet with CSS custom properties for light/dark theming:

```css
:root {
  /* Brand — derived from the target app */
  --doc-header-bg: <extracted header color>;
  --doc-accent: <extracted accent color>;
  --doc-brand-primary: <extracted brand color>;

  /* Fonts */
  --doc-font-body: <system font stack>;
  --doc-font-mono: <monospace stack>;

  /* Light mode surfaces */
  --doc-bg: #ffffff;
  --doc-bg-secondary: #f8f9fa;
  --doc-text: #212529;
  --doc-text-secondary: #495057;
  --doc-border: #dee2e6;
  --doc-code-bg: #f1f3f5;
  --doc-code-text: #e03131;
  --doc-sidebar-bg: #f8f9fa;
  --doc-sidebar-active: <accent-light>;
  --doc-sidebar-active-text: <accent-dark>;
  --doc-card-bg: #ffffff;
  --doc-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

[data-theme="dark"] {
  --doc-bg: #1a1b1e;
  --doc-bg-secondary: #25262b;
  --doc-text: #c1c2c5;
  --doc-border: #373a40;
  --doc-code-bg: #2c2e33;
  --doc-code-text: #ff6b6b;
  --doc-card-bg: #25262b;
  --doc-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
```

Organize CSS sections with clear comment delimiters:
- CSS Custom Properties
- Reset & Base
- Layout (header, sidebar, main, responsive)
- Typography
- Code blocks
- Tables
- Cards / component cards
- Visual examples (mock-* classes for component previews)
- Color swatches
- Do/Don't grid
- Callouts (warn, info, success, error)
- PR task cards (for action items)
- Responsive breakpoints

### JavaScript (main.js)

All interactivity in a single vanilla JS IIFE:

1. **Theme toggle** — light/dark, respects `prefers-color-scheme`
2. **Active nav highlighting** — matches pathname to nav links
3. **Mobile sidebar** — burger button toggles sidebar + overlay
4. **Copy buttons** — auto-generated on all `<pre>` elements
5. **Collapsible sidebar** — toggle with localStorage persistence
6. **GitHub issue links** — auto-generated on action item cards (if repo URL is provided)

### Navigation

The sidebar nav is identical on every page. It is hardcoded in each HTML file (no includes).

**CRITICAL:** When adding or removing a page, you MUST update the nav in ALL HTML files. Always use a batch Python script:

```python
import glob
OLD_NAV = '...'  # The current nav HTML block
NEW_NAV = '...'  # The updated nav HTML block
for f in sorted(glob.glob("*.html") + glob.glob("components/*.html")):
    content = open(f).read()
    content = content.replace(OLD_NAV, NEW_NAV)
    open(f, "w").write(content)
```

**Path conventions:**
- Top-level pages: `href="tokens.html"`
- Component pages: `href="../tokens.html"` (prefix with `../`)

### Component Page Template

Every component page follows this section order:

1. **Title + subtitle** (`<h1>` + `<p class="doc-subtitle">`)
2. **Description** (`<h2 id="description">`)
3. **Do/Don't grid** (`.do-dont-grid` with `.do-box` and `.dont-box`)
4. **Design / Visual Examples** (`<h2 id="design">`) — mock renders using CSS classes
5. **Component Reference** — collapsible `<details class="component-reference">` with screenshots and links to the live app
6. **Implementation** (`<h2 id="implementation">`) — source code with syntax-highlighted spans
7. **Layout Specs** (`<h2 id="layout">`) — pixel measurements table
8. **Accessibility** (`<h2 id="accessibility">`) — ARIA, contrast, keyboard notes

### Action Items Page

Use PR-style task cards for concrete fixes. Each card includes:
- Number, title, labels (inconsistency/tokens/component/easy/medium/hard)
- Problem description
- Before/After visual mockups
- Code diff
- Files changed

### Mock Component CSS

For visual examples on component pages, create `mock-*` CSS classes that render static previews of each component. These are pure CSS mockups, not functional components. Examples:

- `mock-badge` + `mock-badge-ok/err/warn/info/unknown` — status badges
- `mock-panel` + `mock-panel-ok/err/warn` — panels with colored borders
- `mock-app-shell`, `mock-app-header` — app layout mockups

### Syntax Highlighting

Use inline `<span>` elements in code blocks:
- `.cmt` — comments (gray italic)
- `.kw` — keywords (blue/purple)
- `.str` — strings (green)
- `.num` — numbers (orange)
- `.tag` — JSX/HTML tags (red)
- `.attr` — attributes (orange)

---

## Phase 5: Create the Figma Plugin

Generate a Figma bootstrap plugin that seeds a Figma file with all extracted tokens. Read `tokens.json` for values.

### Plugin Structure

```
figma-plugin/
├── manifest.json
└── code.js
```

**manifest.json:**
```json
{
  "name": "<Project Name> DS Bootstrap",
  "id": "<unique-id>",
  "api": "1.0.0",
  "main": "code.js",
  "editorType": ["figma"],
  "capabilities": [],
  "permissions": []
}
```

### Plugin Architecture (code.js)

The plugin is a single JS file organized into sections:

#### 1. Token Definitions

Define all tokens as JS constants at the top of the file. Colors use Figma's 0-1 RGB range (divide hex values by 255).

```javascript
const BRAND_COLORS = {
  "brand/primary": { r: 0.902, g: 0.322, b: 0.173 },  // #e6522c
  // ...
};

const HEALTH_COLORS = {
  ok: {
    light: { bg: { r: ..., g: ..., b: ... }, text: { r: ..., g: ..., b: ... }, border: { r: ..., g: ..., b: ... } },
    dark:  { bg: { r: ..., g: ..., b: ... }, text: { r: ..., g: ..., b: ... }, border: { r: ..., g: ..., b: ... } }
  },
  // ...
};

const SPACING = {
  "spacing/xs": 8,
  "spacing/sm": 12,
  // ...
};

const RADIUS = {
  "radius/default": 4,
  "radius/sm": 2,
  // ...
};

const TEXT_STYLES = [
  { name: "heading/page", family: "Inter", size: 20, weight: 700, lineHeight: 1.25 },
  // For monospace, use "Courier New" — it's universally available in Figma.
  // Do NOT use "DejaVu Sans Mono", "Roboto Mono", or other fonts that may not be installed.
  { name: "code/default", family: "Courier New", size: 13, weight: 400, lineHeight: 1.6 },
  // ...
];

const SHADOW_STYLES = [
  {
    name: "elevation/sm",
    effects: [
      { type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.08 },
        offset: { x: 0, y: 1 }, radius: 3, spread: 0,
        visible: true, blendMode: "NORMAL" },
    ]
  },
  // ...
];
```

#### 2. Variable Collections

Create Figma variable collections for tokens that need mode support (light/dark):

```javascript
async function createVariableCollections() {
  figma.notify("Creating variable collections...");

  // Brand — single mode
  const brandColl = figma.variables.createVariableCollection("Brand");
  const brandMode = brandColl.modes[0].modeId;
  for (const [name, rgb] of Object.entries(BRAND_COLORS)) {
    const v = figma.variables.createVariable(name, brandColl, "COLOR");
    v.setValueForMode(brandMode, rgb);
  }

  // Spacing — single mode, FLOAT type
  const spacingColl = figma.variables.createVariableCollection("Spacing");
  const spacingMode = spacingColl.modes[0].modeId;
  for (const [name, value] of Object.entries(SPACING)) {
    const v = figma.variables.createVariable(name, spacingColl, "FLOAT");
    v.setValueForMode(spacingMode, value);
  }

  // Status Colors — Light + Dark modes
  const statusColl = figma.variables.createVariableCollection("Status Colors");
  const lightId = statusColl.modes[0].modeId;
  statusColl.renameMode(lightId, "Light");
  const darkId = statusColl.addMode("Dark");

  for (const [status, modes] of Object.entries(HEALTH_COLORS)) {
    for (const suffix of ["bg", "text", "border"]) {
      const v = figma.variables.createVariable(
        `status/${status}-${suffix}`, statusColl, "COLOR"
      );
      v.setValueForMode(lightId, modes.light[suffix]);
      v.setValueForMode(darkId, modes.dark[suffix]);
    }
  }
}
```

#### 3. Text Styles

**CRITICAL — Font handling:** Fonts may not be available. Always wrap `loadFontAsync` in try/catch with a fallback:

```javascript
async function createTextStyles() {
  figma.notify("Creating text styles...");

  for (const def of TEXT_STYLES) {
    const weightStyle = def.weight >= 700 ? "Bold"
      : def.weight >= 600 ? "Semi Bold"  // NOTE: Figma uses "Semi Bold", not "SemiBold"
      : def.weight >= 500 ? "Medium"
      : "Regular";

    let resolvedFamily = def.family;
    let resolvedStyle = weightStyle;

    try {
      await figma.loadFontAsync({ family: def.family, style: weightStyle });
    } catch (_e) {
      // Font or weight unavailable — fall back
      try {
        await figma.loadFontAsync({ family: def.family, style: "Regular" });
        resolvedStyle = "Regular";
      } catch (_e2) {
        // Font entirely unavailable — fall back to Inter
        try {
          await figma.loadFontAsync({ family: "Inter", style: weightStyle });
          resolvedFamily = "Inter";
        } catch (_e3) {
          await figma.loadFontAsync({ family: "Inter", style: "Regular" });
          resolvedFamily = "Inter";
          resolvedStyle = "Regular";
        }
      }
    }

    const style = figma.createTextStyle();
    style.name = def.name;
    style.fontName = { family: resolvedFamily, style: resolvedStyle };
    style.fontSize = def.size;
    style.lineHeight = { value: def.lineHeight * 100, unit: "PERCENT" };
  }
}
```

**Common Figma font pitfalls (bugs found during development):**
- Figma uses `"Semi Bold"` (with space), not `"SemiBold"` — this WILL crash if wrong
- `"DejaVu Sans Mono"` and `"Roboto Mono"` are NOT available in Figma by default — use `"Courier New"` for monospace
- Always fall back to `"Inter"` as the ultimate safe font — it's built into Figma
- Some font families only have `"Regular"` — requesting `"Medium"` or `"Bold"` will throw

#### 4. Effect Styles

```javascript
async function createEffectStyles() {
  figma.notify("Creating elevation styles...");
  for (const def of SHADOW_STYLES) {
    const style = figma.createEffectStyle();
    style.name = def.name;
    style.effects = def.effects;
  }
}
```

#### 5. Component Scaffolds (Optional)

Create visual component frames on a dedicated page. Use helper functions:

```javascript
// Helper: create auto-layout frame
function autoFrame(dir) {
  const f = figma.createFrame();
  f.layoutMode = dir === "h" ? "HORIZONTAL" : "VERTICAL";
  f.primaryAxisSizingMode = "AUTO";
  f.counterAxisSizingMode = "AUTO";
  f.fills = [];
  return f;
}

// Helper: create text node
async function txt(chars, family, style, size, col) {
  const t = figma.createText();
  try {
    await figma.loadFontAsync({ family, style });
  } catch (_e) {
    await figma.loadFontAsync({ family: "Inter", style: "Regular" });
    family = "Inter";
    style = "Regular";
  }
  t.fontName = { family, style };
  t.fontSize = size;
  t.characters = chars;
  t.fills = [{ type: "SOLID", color: col }];
  return t;
}
```

Layout components on a "Components" page in rows with consistent spacing.

#### 6. Main Entry Point

```javascript
async function main() {
  try {
    figma.notify("Design System Bootstrap starting...", { timeout: 2000 });
    await createVariableCollections();
    await createTextStyles();
    await createEffectStyles();
    // await createComponentScaffolds();  // Optional
    figma.notify("Bootstrap complete!", { timeout: 5000 });
  } catch (error) {
    const msg = error && error.message ? error.message : String(error);
    figma.notify("Error: " + msg, { error: true, timeout: 8000 });
    console.error("Plugin error:", error);
  } finally {
    figma.closePlugin();
  }
}

main();
```

### Distributing the Plugin

Zip the `figma-plugin/` directory into `figma-plugin.zip` for easy distribution. Users import via Figma > Plugins > Development > Import plugin from manifest.

---

## Phase 6: Deploy and QA

The documentation site is pure static HTML — deploy by:
- **GitHub Pages:** push to `main`, enable Pages in repo settings
- **Any static host:** upload the directory (Netlify, Vercel, S3, etc.)
- **Local:** `npx serve . -l 3000`

No build step needed.

### Visual QA

After deployment, visually inspect every page. If you are Claude Cowork with Computer Use, open the deployed site in Chrome and check each page. If you are Perplexity Computer, deploy and screenshot every page. If you are Claude Code without browser access, tell the user:

*"The site is generated and ready to deploy. I recommend opening it locally (`npx serve . -l 3000`) and checking: (a) light and dark mode on every page, (b) mobile responsiveness with the burger menu, (c) all screenshots load in collapsible sections, (d) copy buttons work on code blocks, (e) navigation links aren't broken."*

---

## Quality Checklist

Before delivering:

- [ ] Every page within the selected scope was visited and screenshotted
- [ ] All inconsistencies identified and documented with resolution reasoning
- [ ] Token values match the actual source (not approximated)
- [ ] All component pages follow the same section order
- [ ] Light and dark mode both render correctly on the documentation site
- [ ] Navigation is identical across all HTML files
- [ ] No broken links (check `../` vs direct paths)
- [ ] Mobile responsive — burger menu works
- [ ] Screenshots load in collapsible component references
- [ ] Figma plugin runs without crashing (test font fallbacks)
- [ ] Copy buttons work on all code blocks
- [ ] `CLAUDE.md` progress checklist is fully checked off

---

## Reference Implementation

The Prometheus Design System (https://github.com/AndrejKiri/prometheus-design-system) was built using this exact process. It documents 19 components extracted from the Prometheus monitoring UI, with a working Figma plugin, 11 screenshots, and PR-style action items. Use it as a structural reference for the documentation site layout, CSS patterns, and Figma plugin architecture.

---
---

# APPENDICES

The following appendices contain the full JSON schemas for handoff files and a validator script. They are integral to the skill — do not skip them.

---

## Appendix A: Handoff File Schemas

These JSON schemas define the exact structure of the intermediate files passed between tools. Every producing tool MUST output files that conform to these schemas. Every consuming tool MUST validate the file before processing.

---

### audit-results.json

Produced by: Phase 1 (Visual Audit) — typically Cowork or Perplexity Computer
Consumed by: Phase 2 (Token Extraction), Phase 3 (Component Extraction), Phase 4 (Documentation Site)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AuditResults",
  "description": "Structured findings from the visual audit of a web application.",
  "type": "object",
  "required": ["app_url", "audit_date", "tool", "scope", "pages_audited", "patterns", "inconsistencies", "raw_observations"],
  "properties": {
    "app_url": {
      "type": "string",
      "format": "uri",
      "description": "Base URL of the audited application."
    },
    "source_repo": {
      "type": ["string", "null"],
      "description": "URL of the source code repository, or null if unavailable."
    },
    "audit_date": {
      "type": "string",
      "format": "date",
      "description": "ISO 8601 date when the audit was performed (YYYY-MM-DD)."
    },
    "tool": {
      "type": "string",
      "enum": ["perplexity-computer", "claude-code", "claude-cowork", "manual"],
      "description": "Which tool performed the audit."
    },
    "scope": {
      "type": "object",
      "required": ["tier", "description", "total_routes_discovered", "routes_audited"],
      "properties": {
        "tier": {
          "type": "string",
          "enum": ["core", "core-plus-data", "full", "custom"],
          "description": "The scope tier selected by the user in Phase 0."
        },
        "description": {
          "type": "string",
          "description": "Human-readable description of what was included/excluded."
        },
        "total_routes_discovered": {
          "type": "integer",
          "minimum": 1,
          "description": "Total number of routes found during route discovery."
        },
        "routes_audited": {
          "type": "integer",
          "minimum": 1,
          "description": "Number of routes actually visited and audited."
        }
      }
    },
    "auth": {
      "type": "object",
      "description": "Authentication details (credentials stripped — only method recorded).",
      "properties": {
        "required": {
          "type": "boolean",
          "description": "Whether the app required login."
        },
        "method": {
          "type": ["string", "null"],
          "enum": ["username-password", "sso", "api-token", "oauth", "none", null],
          "description": "Authentication method used."
        }
      }
    },
    "tech_stack": {
      "type": "object",
      "description": "Detected technology stack (from source or inspection).",
      "properties": {
        "framework": { "type": ["string", "null"], "description": "e.g., React, Vue, Angular, Svelte" },
        "ui_library": { "type": ["string", "null"], "description": "e.g., Mantine, MUI, Chakra, Ant Design" },
        "css_approach": { "type": ["string", "null"], "description": "e.g., CSS Modules, Tailwind, Emotion, styled-components, vanilla CSS" },
        "language": { "type": ["string", "null"], "description": "e.g., TypeScript, JavaScript" },
        "build_tool": { "type": ["string", "null"], "description": "e.g., Vite, Webpack, Next.js" }
      }
    },
    "pages_audited": {
      "type": "array",
      "minItems": 1,
      "description": "One entry per page/route visited.",
      "items": {
        "type": "object",
        "required": ["url", "name", "screenshot", "elements"],
        "properties": {
          "url": {
            "type": "string",
            "description": "Route path relative to app_url (e.g., '/alerts')."
          },
          "name": {
            "type": "string",
            "description": "Human-readable page name (e.g., 'Alerts')."
          },
          "screenshot": {
            "type": "string",
            "description": "Relative path to screenshot file (e.g., 'screenshots/alerts.jpg')."
          },
          "additional_screenshots": {
            "type": "array",
            "description": "Screenshots of interactive states (expanded accordions, modals, tabs, hover states).",
            "items": {
              "type": "object",
              "required": ["path", "state"],
              "properties": {
                "path": { "type": "string", "description": "Relative path to screenshot." },
                "state": { "type": "string", "description": "What state is shown (e.g., 'filter-expanded', 'modal-open', 'dark-mode')." }
              }
            }
          },
          "elements": {
            "type": "array",
            "items": { "type": "string" },
            "description": "PascalCase names of UI patterns found on this page (e.g., ['StatusBadge', 'FilterToolbar', 'DataTable'])."
          },
          "has_data": {
            "type": "boolean",
            "description": "Whether the page had representative data (true) or showed empty state (false)."
          },
          "notes": {
            "type": "string",
            "description": "Free-text observations about the page."
          }
        }
      }
    },
    "patterns": {
      "type": "array",
      "minItems": 1,
      "description": "Inventory of every distinct UI pattern found across all pages.",
      "items": {
        "type": "object",
        "required": ["name", "pages", "instance_count", "variation_count", "description", "category"],
        "properties": {
          "name": {
            "type": "string",
            "description": "PascalCase name (e.g., 'StatusBadge'). Must match names used in pages_audited.elements."
          },
          "pages": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Route paths where this pattern appears."
          },
          "instance_count": {
            "type": "integer",
            "minimum": 1,
            "description": "Total instances across all pages."
          },
          "variation_count": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of visually distinct implementations found."
          },
          "description": {
            "type": "string",
            "description": "What this pattern does and how users interact with it."
          },
          "category": {
            "type": "string",
            "enum": ["navigation", "data-display", "input", "feedback", "layout", "overlay", "media", "utility"],
            "description": "Functional category of the pattern."
          },
          "observed_styles": {
            "type": "object",
            "description": "Visual properties observed (approximate if from visual audit, exact if from source).",
            "properties": {
              "colors": {
                "type": "array",
                "items": { "type": "string" },
                "description": "CSS color values observed (e.g., ['#e6522c', 'rgb(40, 167, 69)'])."
              },
              "font_sizes": {
                "type": "array",
                "items": { "type": "string" },
                "description": "Font sizes observed (e.g., ['13px', '0.85rem'])."
              },
              "spacing": {
                "type": "array",
                "items": { "type": "string" },
                "description": "Padding/margin values observed (e.g., ['4px 8px', '12px'])."
              },
              "border_radius": {
                "type": ["string", "null"],
                "description": "Border radius observed (e.g., '4px')."
              }
            }
          },
          "source_files": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Paths to source files implementing this pattern (if source available)."
          }
        }
      }
    },
    "inconsistencies": {
      "type": "array",
      "description": "Every inconsistency found during the audit. May be empty for very consistent apps.",
      "items": {
        "type": "object",
        "required": ["id", "title", "severity", "type", "pages", "variants", "canonical", "reasoning"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique identifier (e.g., 'INC-001'). Used to reference in action items."
          },
          "title": {
            "type": "string",
            "description": "Short description of the inconsistency."
          },
          "severity": {
            "type": "string",
            "enum": ["critical", "major", "minor", "cosmetic"],
            "description": "critical: breaks UX or accessibility. major: visible to users, confusing. minor: noticeable on close inspection. cosmetic: pixel-level, low impact."
          },
          "type": {
            "type": "string",
            "enum": ["implementation-drift", "hardcoded-values", "missing-normalization", "style-drift", "duplicated-logic", "accessibility", "responsive"],
            "description": "Category of inconsistency."
          },
          "pages": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Route paths affected."
          },
          "pattern": {
            "type": ["string", "null"],
            "description": "PascalCase pattern name this inconsistency relates to, or null if it's a general issue."
          },
          "variants": {
            "type": "array",
            "minItems": 2,
            "description": "The different implementations found.",
            "items": {
              "type": "object",
              "required": ["page", "implementation"],
              "properties": {
                "page": { "type": "string", "description": "Route path." },
                "implementation": { "type": "string", "description": "How it's implemented on this page." },
                "source_file": { "type": ["string", "null"], "description": "Source file path if available." },
                "source_line": { "type": ["integer", "null"], "description": "Line number if available." }
              }
            }
          },
          "canonical": {
            "type": "string",
            "description": "Which variant should be the canonical implementation."
          },
          "reasoning": {
            "type": "string",
            "description": "Why this variant was chosen as canonical."
          },
          "fix": {
            "type": ["string", "null"],
            "description": "Concrete fix description or code diff, if determinable."
          }
        }
      }
    },
    "raw_observations": {
      "type": "object",
      "description": "Raw visual observations useful for token extraction. Best-effort — provide what you can observe.",
      "properties": {
        "colors_observed": {
          "type": "array",
          "description": "All distinct color values observed across the app.",
          "items": {
            "type": "object",
            "required": ["value", "usage"],
            "properties": {
              "value": { "type": "string", "description": "CSS color value (hex, rgb, hsl)." },
              "usage": { "type": "string", "description": "Where/how this color is used (e.g., 'header background', 'success badge bg', 'body text')." },
              "pages": { "type": "array", "items": { "type": "string" }, "description": "Pages where observed." }
            }
          }
        },
        "fonts_observed": {
          "type": "array",
          "description": "Font families detected.",
          "items": {
            "type": "object",
            "required": ["family", "usage"],
            "properties": {
              "family": { "type": "string", "description": "Font family name." },
              "usage": { "type": "string", "description": "Where used (e.g., 'body text', 'code blocks', 'headings')." }
            }
          }
        },
        "spacing_observed": {
          "type": "array",
          "description": "Recurring spacing values.",
          "items": {
            "type": "object",
            "properties": {
              "value": { "type": "string" },
              "usage": { "type": "string" }
            }
          }
        },
        "has_dark_mode": {
          "type": "boolean",
          "description": "Whether the app supports a dark mode/theme."
        },
        "theming_approach": {
          "type": ["string", "null"],
          "description": "How theming is implemented (e.g., 'CSS custom properties', 'CSS light-dark()', 'data-theme attribute', 'class-based')."
        }
      }
    }
  }
}
```

#### Validation checklist for audit-results.json

Before saving, verify:
- [ ] Every page in the selected scope has an entry in `pages_audited`
- [ ] Every element name in `pages_audited[].elements` has a matching entry in `patterns`
- [ ] Every inconsistency references pages that exist in `pages_audited`
- [ ] Every screenshot path in `pages_audited[].screenshot` points to an actual file in `screenshots/`
- [ ] `raw_observations.colors_observed` has at least the header, background, and text colors

---

### tokens.json

Produced by: Phase 2 (Token Extraction)
Consumed by: Phase 3 (Component Extraction), Phase 4 (Documentation Site), Phase 5 (Figma Plugin)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DesignTokens",
  "description": "All design tokens extracted from the target application, organized by category.",
  "type": "object",
  "required": ["app_url", "extraction_date", "source", "colors", "spacing", "typography", "border_radius"],
  "properties": {
    "app_url": {
      "type": "string",
      "format": "uri",
      "description": "Base URL of the target application. Must match audit-results.json."
    },
    "extraction_date": {
      "type": "string",
      "format": "date",
      "description": "ISO 8601 date of extraction."
    },
    "source": {
      "type": "string",
      "enum": ["visual-audit", "source-code", "both"],
      "description": "Whether tokens were extracted from visual observation, source code, or both."
    },
    "colors": {
      "type": "object",
      "required": ["brand", "status", "surface", "text", "border"],
      "properties": {
        "brand": {
          "type": "array",
          "minItems": 1,
          "description": "Brand/accent colors (logo, header, primary action).",
          "items": {
            "type": "object",
            "required": ["name", "value", "usage"],
            "properties": {
              "name": { "type": "string", "description": "Token name (e.g., 'brand-primary', 'brand-header-bg')." },
              "value": { "type": "string", "description": "CSS color value." },
              "usage": { "type": "string", "description": "Where this color is used." },
              "figma_rgb": {
                "type": "object",
                "description": "Pre-computed Figma 0-1 RGB. Optional but saves Phase 5 computation.",
                "properties": {
                  "r": { "type": "number", "minimum": 0, "maximum": 1 },
                  "g": { "type": "number", "minimum": 0, "maximum": 1 },
                  "b": { "type": "number", "minimum": 0, "maximum": 1 }
                }
              }
            }
          }
        },
        "status": {
          "type": "array",
          "minItems": 1,
          "description": "Semantic status/health colors with light and dark mode variants.",
          "items": {
            "type": "object",
            "required": ["name", "light"],
            "properties": {
              "name": {
                "type": "string",
                "description": "Status name (e.g., 'ok', 'error', 'warning', 'info', 'unknown', 'pending')."
              },
              "light": {
                "type": "object",
                "required": ["bg", "text", "border"],
                "properties": {
                  "bg": { "type": "string", "description": "Background color in light mode." },
                  "text": { "type": "string", "description": "Text color in light mode." },
                  "border": { "type": "string", "description": "Border color in light mode." }
                }
              },
              "dark": {
                "type": "object",
                "description": "Dark mode variants. Omit if app has no dark mode.",
                "properties": {
                  "bg": { "type": "string" },
                  "text": { "type": "string" },
                  "border": { "type": "string" }
                }
              }
            }
          }
        },
        "surface": {
          "type": "array",
          "minItems": 1,
          "description": "Background/surface colors.",
          "items": {
            "type": "object",
            "required": ["name", "light"],
            "properties": {
              "name": { "type": "string", "description": "e.g., 'page-bg', 'card-bg', 'code-bg', 'sidebar-bg'." },
              "light": { "type": "string", "description": "Light mode value." },
              "dark": { "type": ["string", "null"], "description": "Dark mode value." }
            }
          }
        },
        "text": {
          "type": "array",
          "minItems": 1,
          "description": "Text colors.",
          "items": {
            "type": "object",
            "required": ["name", "light"],
            "properties": {
              "name": { "type": "string", "description": "e.g., 'text-primary', 'text-secondary', 'text-muted'." },
              "light": { "type": "string" },
              "dark": { "type": ["string", "null"] }
            }
          }
        },
        "border": {
          "type": "array",
          "description": "Border colors.",
          "items": {
            "type": "object",
            "required": ["name", "light"],
            "properties": {
              "name": { "type": "string" },
              "light": { "type": "string" },
              "dark": { "type": ["string", "null"] }
            }
          }
        }
      }
    },
    "spacing": {
      "type": "object",
      "required": ["scale"],
      "properties": {
        "scale": {
          "type": "array",
          "minItems": 1,
          "description": "Named spacing scale.",
          "items": {
            "type": "object",
            "required": ["name", "value_px"],
            "properties": {
              "name": { "type": "string", "description": "Token name (e.g., 'xs', 'sm', 'md', 'lg', 'xl')." },
              "value_px": { "type": "number", "description": "Value in pixels." },
              "value_rem": { "type": ["number", "null"], "description": "Value in rem, if known." }
            }
          }
        },
        "layout": {
          "type": "array",
          "description": "Fixed layout measurements.",
          "items": {
            "type": "object",
            "required": ["name", "value_px"],
            "properties": {
              "name": { "type": "string", "description": "e.g., 'header-height', 'sidebar-width', 'card-padding'." },
              "value_px": { "type": "number" }
            }
          }
        }
      }
    },
    "typography": {
      "type": "object",
      "required": ["families", "styles"],
      "properties": {
        "families": {
          "type": "array",
          "minItems": 1,
          "description": "Font families used in the application.",
          "items": {
            "type": "object",
            "required": ["name", "family", "usage"],
            "properties": {
              "name": { "type": "string", "description": "Token name (e.g., 'font-body', 'font-mono', 'font-display')." },
              "family": { "type": "string", "description": "CSS font-family value (e.g., 'Inter, system-ui, sans-serif')." },
              "usage": { "type": "string", "description": "Where this font is used." },
              "figma_family": {
                "type": ["string", "null"],
                "description": "Figma-safe font name. Use 'Courier New' for monospace, 'Inter' for sans-serif. Never use fonts that aren't bundled with Figma."
              }
            }
          }
        },
        "styles": {
          "type": "array",
          "minItems": 1,
          "description": "All distinct text styles (heading levels, body, labels, code).",
          "items": {
            "type": "object",
            "required": ["name", "category", "font_family", "size_px", "weight", "line_height"],
            "properties": {
              "name": {
                "type": "string",
                "description": "Slash-separated style name for Figma (e.g., 'heading/page', 'body/default', 'code/inline')."
              },
              "category": {
                "type": "string",
                "enum": ["heading", "body", "label", "code", "display"],
                "description": "Typography category."
              },
              "font_family": {
                "type": "string",
                "description": "Token name from families array (e.g., 'font-body')."
              },
              "size_px": { "type": "number", "description": "Font size in pixels." },
              "size_rem": { "type": ["number", "null"], "description": "Font size in rem, if known." },
              "weight": {
                "type": "integer",
                "enum": [100, 200, 300, 400, 500, 600, 700, 800, 900],
                "description": "CSS font-weight numeric value."
              },
              "line_height": {
                "type": "number",
                "description": "Unitless line-height multiplier (e.g., 1.5, 1.25)."
              },
              "letter_spacing": {
                "type": ["string", "null"],
                "description": "CSS letter-spacing value if non-default."
              }
            }
          }
        }
      }
    },
    "border_radius": {
      "type": "array",
      "minItems": 1,
      "description": "Border radius scale.",
      "items": {
        "type": "object",
        "required": ["name", "value_px"],
        "properties": {
          "name": { "type": "string", "description": "Token name (e.g., 'radius-sm', 'radius-default', 'radius-pill')." },
          "value_px": { "type": "number" }
        }
      }
    },
    "elevation": {
      "type": "array",
      "description": "Shadow/elevation definitions. May be empty if app uses no shadows.",
      "items": {
        "type": "object",
        "required": ["name", "light"],
        "properties": {
          "name": { "type": "string", "description": "Token name (e.g., 'elevation-sm', 'elevation-md')." },
          "light": {
            "type": "object",
            "required": ["css"],
            "properties": {
              "css": { "type": "string", "description": "CSS box-shadow value." },
              "figma_effects": {
                "type": "array",
                "description": "Pre-computed Figma effect objects for Phase 5.",
                "items": {
                  "type": "object",
                  "required": ["type", "color", "offset", "radius"],
                  "properties": {
                    "type": { "type": "string", "enum": ["DROP_SHADOW", "INNER_SHADOW"] },
                    "color": {
                      "type": "object",
                      "required": ["r", "g", "b", "a"],
                      "properties": {
                        "r": { "type": "number" }, "g": { "type": "number" },
                        "b": { "type": "number" }, "a": { "type": "number" }
                      }
                    },
                    "offset": {
                      "type": "object",
                      "required": ["x", "y"],
                      "properties": { "x": { "type": "number" }, "y": { "type": "number" } }
                    },
                    "radius": { "type": "number" },
                    "spread": { "type": "number", "default": 0 }
                  }
                }
              }
            }
          },
          "dark": {
            "type": "object",
            "description": "Dark mode shadow. Omit if same as light or no dark mode.",
            "properties": {
              "css": { "type": "string" },
              "figma_effects": { "type": "array" }
            }
          }
        }
      }
    },
    "icons": {
      "type": "object",
      "description": "Icon system information. Optional — omit if app has no icon system.",
      "properties": {
        "library": { "type": ["string", "null"], "description": "Icon library used (e.g., 'Lucide', 'Material Icons', 'custom SVG')." },
        "count": { "type": "integer", "description": "Number of distinct icons found." },
        "default_size_px": { "type": ["number", "null"] },
        "icons": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "usage"],
            "properties": {
              "name": { "type": "string" },
              "usage": { "type": "string" },
              "svg": { "type": ["string", "null"], "description": "SVG markup if extractable." }
            }
          }
        }
      }
    }
  }
}
```

#### Validation checklist for tokens.json

Before saving, verify:
- [ ] `app_url` matches `audit-results.json`
- [ ] `colors.brand` has at least one entry (header/accent color)
- [ ] `colors.status` has at least 2 entries (typically ok + error at minimum)
- [ ] `colors.surface` has page-bg and card-bg at minimum
- [ ] `colors.text` has at least primary and secondary
- [ ] `typography.families` has at least body font
- [ ] `typography.styles` has at least one heading, one body, and one code style
- [ ] Every `figma_rgb` value has r/g/b between 0 and 1
- [ ] If `audit-results.json` reports `has_dark_mode: true`, then status/surface/text entries have `dark` values

---

### components.json

Produced by: Phase 3 (Component Extraction)
Consumed by: Phase 4 (Documentation Site)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ComponentInventory",
  "description": "All UI components extracted and documented from the target application.",
  "type": "object",
  "required": ["app_url", "extraction_date", "components"],
  "properties": {
    "app_url": {
      "type": "string",
      "format": "uri",
      "description": "Must match audit-results.json and tokens.json."
    },
    "extraction_date": {
      "type": "string",
      "format": "date"
    },
    "component_count": {
      "type": "integer",
      "description": "Total number of components documented."
    },
    "components": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name", "slug", "description", "complexity", "category", "pages", "variants", "layout", "dos_and_donts"],
        "properties": {
          "name": {
            "type": "string",
            "description": "PascalCase component name (e.g., 'StatusBadge'). Must match pattern names from audit-results.json."
          },
          "slug": {
            "type": "string",
            "pattern": "^[a-z0-9-]+$",
            "description": "URL-safe slug for the component page filename (e.g., 'status-badge'). Used as components/{slug}.html."
          },
          "description": {
            "type": "string",
            "description": "What this component does and when to use it. 1-3 sentences."
          },
          "subtitle": {
            "type": "string",
            "description": "Short tagline for the component page header (e.g., 'Visual indicator for health and operational status')."
          },
          "complexity": {
            "type": "string",
            "enum": ["simple", "medium", "complex"],
            "description": "simple: stateless, few props. medium: some state or composition. complex: significant interactivity."
          },
          "category": {
            "type": "string",
            "enum": ["navigation", "data-display", "input", "feedback", "layout", "overlay", "media", "utility"],
            "description": "Must match the category from the pattern in audit-results.json."
          },
          "pages": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Route paths where this component is used."
          },
          "source_files": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Source file paths (if source available)."
          },
          "props": {
            "type": "array",
            "description": "Component props/API. May be empty for purely visual patterns.",
            "items": {
              "type": "object",
              "required": ["name", "type", "description"],
              "properties": {
                "name": { "type": "string", "description": "Prop name (e.g., 'status', 'variant', 'size')." },
                "type": { "type": "string", "description": "TypeScript-style type (e.g., 'string', 'boolean', \"'ok' | 'error' | 'warning'\")." },
                "default": { "type": ["string", "null"], "description": "Default value, or null if required." },
                "required": { "type": "boolean", "default": false },
                "description": { "type": "string" }
              }
            }
          },
          "variants": {
            "type": "array",
            "minItems": 1,
            "description": "All visual states/variants of this component.",
            "items": {
              "type": "object",
              "required": ["name", "description"],
              "properties": {
                "name": { "type": "string", "description": "Variant name (e.g., 'ok', 'error', 'expanded', 'loading')." },
                "description": { "type": "string" },
                "mock_css_class": {
                  "type": ["string", "null"],
                  "description": "CSS class name for the mock render (e.g., 'mock-badge-ok'). Phase 4 generates this CSS."
                },
                "mock_html": {
                  "type": ["string", "null"],
                  "description": "HTML snippet for the visual example on the docs page."
                },
                "tokens_used": {
                  "type": "array",
                  "items": { "type": "string" },
                  "description": "Token names from tokens.json used by this variant (e.g., ['status-ok-bg', 'status-ok-text'])."
                }
              }
            }
          },
          "layout": {
            "type": "object",
            "description": "Pixel-precise measurements for the component.",
            "required": ["specs"],
            "properties": {
              "specs": {
                "type": "array",
                "minItems": 1,
                "items": {
                  "type": "object",
                  "required": ["property", "value"],
                  "properties": {
                    "property": {
                      "type": "string",
                      "description": "CSS property name (e.g., 'height', 'padding', 'font-size', 'border-radius', 'gap')."
                    },
                    "value": {
                      "type": "string",
                      "description": "CSS value (e.g., '28px', '4px 8px', '13px')."
                    },
                    "token": {
                      "type": ["string", "null"],
                      "description": "Matching token name from tokens.json, if this value maps to a token."
                    }
                  }
                }
              }
            }
          },
          "dos_and_donts": {
            "type": "array",
            "minItems": 1,
            "description": "Usage guidelines.",
            "items": {
              "type": "object",
              "required": ["type", "text"],
              "properties": {
                "type": {
                  "type": "string",
                  "enum": ["do", "dont"],
                  "description": "'do' for recommended practice, 'dont' for anti-pattern."
                },
                "text": { "type": "string", "description": "The guideline text." },
                "example": { "type": ["string", "null"], "description": "Optional HTML/code example." }
              }
            }
          },
          "accessibility": {
            "type": "object",
            "description": "Accessibility considerations.",
            "properties": {
              "aria_labels": { "type": ["string", "null"], "description": "Required ARIA attributes." },
              "keyboard": { "type": ["string", "null"], "description": "Keyboard interaction description." },
              "contrast": { "type": ["string", "null"], "description": "Color contrast notes." },
              "screen_reader": { "type": ["string", "null"], "description": "Screen reader behavior." }
            }
          },
          "code_example": {
            "type": ["string", "null"],
            "description": "Code snippet showing how to use this component (JSX/HTML)."
          },
          "related_inconsistencies": {
            "type": "array",
            "items": { "type": "string" },
            "description": "IDs from audit-results.json inconsistencies that affect this component (e.g., ['INC-001', 'INC-003'])."
          }
        }
      }
    },
    "action_items": {
      "type": "array",
      "description": "PR-style task cards for the action-items.html page. Generated from inconsistencies + improvement opportunities.",
      "items": {
        "type": "object",
        "required": ["id", "title", "priority", "effort", "labels", "description"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Sequential ID (e.g., 'AI-001')."
          },
          "title": {
            "type": "string",
            "description": "PR-style title (e.g., 'Normalize StatusBadge implementation across all pages')."
          },
          "priority": {
            "type": "string",
            "enum": ["p0-critical", "p1-high", "p2-medium", "p3-low"],
            "description": "Priority level."
          },
          "effort": {
            "type": "string",
            "enum": ["easy", "medium", "hard"],
            "description": "Estimated implementation effort."
          },
          "labels": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["inconsistency", "tokens", "component", "accessibility", "responsive", "documentation", "refactor"]
            },
            "description": "Categorization labels."
          },
          "description": {
            "type": "string",
            "description": "Detailed problem description."
          },
          "related_inconsistency": {
            "type": ["string", "null"],
            "description": "ID from audit-results.json (e.g., 'INC-001')."
          },
          "related_component": {
            "type": ["string", "null"],
            "description": "PascalCase component name."
          },
          "files_changed": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Source files that need changes."
          },
          "before_after": {
            "type": "object",
            "description": "Visual or code before/after for the task card.",
            "properties": {
              "before_html": { "type": ["string", "null"], "description": "HTML mock of current state." },
              "after_html": { "type": ["string", "null"], "description": "HTML mock of fixed state." },
              "diff": { "type": ["string", "null"], "description": "Code diff if applicable." }
            }
          },
          "github_issue_title": {
            "type": ["string", "null"],
            "description": "Pre-formatted title for GitHub issue auto-linking (if repo URL provided)."
          }
        }
      }
    }
  }
}
```

#### Validation checklist for components.json

Before saving, verify:
- [ ] `app_url` matches the other two files
- [ ] Every component `name` matches a pattern `name` from `audit-results.json`
- [ ] Every component has at least one variant
- [ ] Every component has at least one layout spec
- [ ] Every component has at least one do/don't entry
- [ ] `slug` values are unique (no duplicates)
- [ ] `tokens_used` in variants reference token names that exist in `tokens.json`
- [ ] `related_inconsistencies` reference IDs that exist in `audit-results.json`
- [ ] Action items with `related_inconsistency` reference valid IDs

---

### source-audit.json (Optional)

Produced by: Phase 1-Source (Source Code Audit)
Consumed by: Phase 2 (supplements audit-results.json with exact values)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SourceAudit",
  "description": "Findings from source code analysis. Supplements the visual audit with exact values and file mappings.",
  "type": "object",
  "required": ["repo_url", "audit_date", "tech_stack", "theme_config", "component_files"],
  "properties": {
    "repo_url": {
      "type": "string",
      "format": "uri"
    },
    "audit_date": {
      "type": "string",
      "format": "date"
    },
    "tech_stack": {
      "type": "object",
      "required": ["framework", "css_approach"],
      "properties": {
        "framework": { "type": "string" },
        "framework_version": { "type": ["string", "null"] },
        "ui_library": { "type": ["string", "null"] },
        "ui_library_version": { "type": ["string", "null"] },
        "css_approach": { "type": "string" },
        "language": { "type": "string" },
        "build_tool": { "type": ["string", "null"] }
      }
    },
    "theme_config": {
      "type": "object",
      "description": "Raw theme configuration extracted from source.",
      "properties": {
        "file_path": { "type": "string", "description": "Path to the theme config file in the repo." },
        "format": {
          "type": "string",
          "enum": ["css-custom-properties", "css-in-js", "tailwind-config", "sass-variables", "less-variables", "json", "other"],
          "description": "How theme values are defined."
        },
        "raw_values": {
          "type": "object",
          "description": "Key-value pairs of raw token values as found in source. Keys are the original variable names."
        }
      }
    },
    "route_definitions": {
      "type": "array",
      "description": "Routes found in the route configuration.",
      "items": {
        "type": "object",
        "required": ["path", "component_file"],
        "properties": {
          "path": { "type": "string" },
          "component_file": { "type": "string" },
          "name": { "type": ["string", "null"] }
        }
      }
    },
    "component_files": {
      "type": "array",
      "description": "Mapping of UI patterns to their source files.",
      "items": {
        "type": "object",
        "required": ["pattern_name", "files"],
        "properties": {
          "pattern_name": {
            "type": "string",
            "description": "PascalCase pattern name matching audit-results.json."
          },
          "files": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["path", "type"],
              "properties": {
                "path": { "type": "string", "description": "File path relative to repo root." },
                "type": {
                  "type": "string",
                  "enum": ["component", "style", "test", "story", "type-definition"],
                  "description": "What kind of file this is."
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## Appendix B: Handoff Validator Script

Save this script as `validate-handoff.py` in your project directory. It is zero-dependency Python (stdlib only). Exit codes: 0 = pass, 1 = fail, 2 = missing files.

```python
#!/usr/bin/env python3
"""
Handoff Schema Validator
========================
Validates audit-results.json, tokens.json, and components.json for:
- Required fields and correct types
- Cross-reference integrity (INC IDs, token names, pattern names, slugs)
- Enum value correctness
- File existence (screenshots)

Usage:
    python validate-handoff.py <project-directory>

    The project directory should contain:
    - audit-results.json
    - tokens.json (optional — skips token cross-checks if missing)
    - components.json (optional — skips component cross-checks if missing)
    - screenshots/ (optional — skips screenshot file checks if missing)

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
    2 = missing required files or invalid JSON
"""

import json
import os
import sys
import re
from pathlib import Path

# ─── Enums ───────────────────────────────────────────────────────────────────

SCOPE_TIERS = {"core", "core-plus-data", "full", "custom"}
TOOLS = {"perplexity-computer", "claude-code", "claude-cowork", "manual"}
PATTERN_CATEGORIES = {"navigation", "data-display", "input", "feedback", "layout", "overlay", "media", "utility"}
SEVERITY_LEVELS = {"critical", "major", "minor", "cosmetic"}
INCONSISTENCY_TYPES = {"implementation-drift", "hardcoded-values", "missing-normalization", "style-drift", "duplicated-logic", "accessibility", "responsive"}
AUTH_METHODS = {"username-password", "sso", "api-token", "oauth", "none", None}
TOKEN_SOURCES = {"visual-audit", "source-code", "both"}
COMPLEXITY_LEVELS = {"simple", "medium", "complex"}
DO_DONT_TYPES = {"do", "dont"}
PRIORITY_LEVELS = {"p0-critical", "p1-high", "p2-medium", "p3-low"}
EFFORT_LEVELS = {"easy", "medium", "hard"}
ACTION_LABELS = {"inconsistency", "tokens", "component", "accessibility", "responsive", "documentation", "refactor"}
TYPOGRAPHY_CATEGORIES = {"heading", "body", "label", "code", "display"}
FONT_WEIGHTS = {100, 200, 300, 400, 500, 600, 700, 800, 900}
SLUG_PATTERN = re.compile(r'^[a-z0-9-]+$')

# ─── Reporter ────────────────────────────────────────────────────────────────

class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passes = []
        self.current_file = ""

    def set_file(self, name):
        self.current_file = name

    def error(self, msg):
        self.errors.append(f"[FAIL] {self.current_file}: {msg}")

    def warn(self, msg):
        self.warnings.append(f"[WARN] {self.current_file}: {msg}")

    def ok(self, msg):
        self.passes.append(f"[PASS] {self.current_file}: {msg}")

    def print_report(self):
        print("\n" + "=" * 70)
        print("HANDOFF SCHEMA VALIDATION REPORT")
        print("=" * 70)

        if self.passes:
            print(f"\n--- Passed ({len(self.passes)}) ---")
            for p in self.passes:
                print(f"  {p}")

        if self.warnings:
            print(f"\n--- Warnings ({len(self.warnings)}) ---")
            for w in self.warnings:
                print(f"  {w}")

        if self.errors:
            print(f"\n--- Errors ({len(self.errors)}) ---")
            for e in self.errors:
                print(f"  {e}")

        print("\n" + "-" * 70)
        total = len(self.passes) + len(self.warnings) + len(self.errors)
        print(f"Total checks: {total}")
        print(f"Passed: {len(self.passes)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors: {len(self.errors)}")

        if self.errors:
            print("\nRESULT: FAIL")
        elif self.warnings:
            print("\nRESULT: PASS (with warnings)")
        else:
            print("\nRESULT: PASS")

        print("=" * 70)
        return len(self.errors) == 0

# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_json(path, report):
    """Load and parse a JSON file. Returns None on failure."""
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        report.set_file(path.name)
        report.error(f"Invalid JSON: {e}")
        return None

def check_required_field(data, field, expected_type, report, context=""):
    """Check that a required field exists and has the correct type."""
    prefix = f"{context}." if context else ""
    if field not in data:
        report.error(f"Missing required field '{prefix}{field}'")
        return False
    if not isinstance(data[field], expected_type):
        report.error(f"'{prefix}{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
        return False
    return True

def check_enum(value, allowed, report, field_name):
    """Check that a value is in the allowed set."""
    if value not in allowed:
        report.error(f"'{field_name}' has invalid value '{value}'. Allowed: {sorted(str(v) for v in allowed if v is not None)}")
        return False
    return True

def check_non_empty_array(data, field, report, context=""):
    """Check that a field is a non-empty array."""
    prefix = f"{context}." if context else ""
    if field not in data:
        report.error(f"Missing required array '{prefix}{field}'")
        return False
    if not isinstance(data[field], list):
        report.error(f"'{prefix}{field}' should be array, got {type(data[field]).__name__}")
        return False
    if len(data[field]) == 0:
        report.error(f"'{prefix}{field}' must not be empty")
        return False
    return True

# ─── audit-results.json ─────────────────────────────────────────────────────

def validate_audit(data, project_dir, report):
    report.set_file("audit-results.json")

    # Top-level required fields
    for field, ftype in [("app_url", str), ("audit_date", str), ("tool", str)]:
        check_required_field(data, field, ftype, report)

    # Tool enum
    if "tool" in data:
        if check_enum(data["tool"], TOOLS, report, "tool"):
            report.ok(f"tool = '{data['tool']}' is valid")

    # Scope object
    if check_required_field(data, "scope", dict, report):
        scope = data["scope"]
        if check_required_field(scope, "tier", str, report, "scope"):
            if check_enum(scope["tier"], SCOPE_TIERS, report, "scope.tier"):
                report.ok(f"scope.tier = '{scope['tier']}' is valid")
        check_required_field(scope, "description", str, report, "scope")
        check_required_field(scope, "total_routes_discovered", int, report, "scope")
        check_required_field(scope, "routes_audited", int, report, "scope")

    # Auth (optional but validate if present)
    if "auth" in data and isinstance(data["auth"], dict):
        auth = data["auth"]
        if "method" in auth:
            check_enum(auth["method"], AUTH_METHODS, report, "auth.method")

    # Pages audited
    page_urls = set()
    page_elements = set()
    screenshot_paths = []

    if check_non_empty_array(data, "pages_audited", report):
        for i, page in enumerate(data["pages_audited"]):
            ctx = f"pages_audited[{i}]"
            check_required_field(page, "url", str, report, ctx)
            check_required_field(page, "name", str, report, ctx)
            check_required_field(page, "screenshot", str, report, ctx)
            check_required_field(page, "elements", list, report, ctx)

            if "url" in page:
                page_urls.add(page["url"])
            if "elements" in page and isinstance(page["elements"], list):
                page_elements.update(page["elements"])
            if "screenshot" in page:
                screenshot_paths.append(page["screenshot"])

            # Additional screenshots
            if "additional_screenshots" in page and isinstance(page["additional_screenshots"], list):
                for j, ss in enumerate(page["additional_screenshots"]):
                    check_required_field(ss, "path", str, report, f"{ctx}.additional_screenshots[{j}]")
                    check_required_field(ss, "state", str, report, f"{ctx}.additional_screenshots[{j}]")
                    if "path" in ss:
                        screenshot_paths.append(ss["path"])

        report.ok(f"pages_audited has {len(data['pages_audited'])} entries")

    # Patterns
    pattern_names = set()
    if check_non_empty_array(data, "patterns", report):
        for i, pat in enumerate(data["patterns"]):
            ctx = f"patterns[{i}]"
            check_required_field(pat, "name", str, report, ctx)
            check_required_field(pat, "pages", list, report, ctx)
            check_required_field(pat, "instance_count", int, report, ctx)
            check_required_field(pat, "variation_count", int, report, ctx)
            check_required_field(pat, "description", str, report, ctx)

            if check_required_field(pat, "category", str, report, ctx):
                check_enum(pat["category"], PATTERN_CATEGORIES, report, f"{ctx}.category")

            if "name" in pat:
                pattern_names.add(pat["name"])

        report.ok(f"patterns has {len(data['patterns'])} entries")

    # Cross-check: every element in pages must have a matching pattern
    orphan_elements = page_elements - pattern_names
    if orphan_elements:
        for elem in sorted(orphan_elements):
            report.error(f"Element '{elem}' appears in pages_audited but has no matching entry in patterns[]")
    else:
        report.ok(f"All {len(page_elements)} element names in pages match pattern entries")

    # Unused patterns (warning only)
    unused_patterns = pattern_names - page_elements
    if unused_patterns:
        for pat in sorted(unused_patterns):
            report.warn(f"Pattern '{pat}' defined but not referenced in any page's elements[]")

    # Inconsistencies
    inconsistency_ids = set()
    if "inconsistencies" in data and isinstance(data["inconsistencies"], list):
        for i, inc in enumerate(data["inconsistencies"]):
            ctx = f"inconsistencies[{i}]"

            if check_required_field(inc, "id", str, report, ctx):
                inc_id = inc["id"]
                if inc_id in inconsistency_ids:
                    report.error(f"{ctx}: Duplicate inconsistency ID '{inc_id}'")
                inconsistency_ids.add(inc_id)

            check_required_field(inc, "title", str, report, ctx)
            check_required_field(inc, "canonical", str, report, ctx)
            check_required_field(inc, "reasoning", str, report, ctx)

            if check_required_field(inc, "severity", str, report, ctx):
                check_enum(inc["severity"], SEVERITY_LEVELS, report, f"{ctx}.severity")

            if check_required_field(inc, "type", str, report, ctx):
                check_enum(inc["type"], INCONSISTENCY_TYPES, report, f"{ctx}.type")

            if check_required_field(inc, "pages", list, report, ctx):
                for page_ref in inc["pages"]:
                    if page_ref not in page_urls:
                        report.error(f"{ctx}: References page '{page_ref}' not found in pages_audited")

            if check_required_field(inc, "variants", list, report, ctx):
                if len(inc["variants"]) < 2:
                    report.error(f"{ctx}: variants must have at least 2 entries (found {len(inc['variants'])})")
                for j, var in enumerate(inc["variants"]):
                    check_required_field(var, "page", str, report, f"{ctx}.variants[{j}]")
                    check_required_field(var, "implementation", str, report, f"{ctx}.variants[{j}]")

        if data["inconsistencies"]:
            report.ok(f"inconsistencies has {len(data['inconsistencies'])} entries with unique IDs")
    else:
        check_required_field(data, "inconsistencies", list, report)

    # Raw observations
    if check_required_field(data, "raw_observations", dict, report):
        obs = data["raw_observations"]
        if "has_dark_mode" not in obs:
            report.warn("raw_observations.has_dark_mode not set")
        else:
            report.ok(f"has_dark_mode = {obs['has_dark_mode']}")

    # Screenshot file existence
    screenshots_dir = project_dir / "screenshots"
    if screenshots_dir.exists():
        missing_screenshots = []
        for ss_path in screenshot_paths:
            full_path = project_dir / ss_path
            if not full_path.exists():
                missing_screenshots.append(ss_path)
        if missing_screenshots:
            for ss in missing_screenshots:
                report.error(f"Screenshot file not found: {ss}")
        else:
            report.ok(f"All {len(screenshot_paths)} screenshot files exist")
    elif screenshot_paths:
        report.warn(f"screenshots/ directory not found — cannot verify {len(screenshot_paths)} screenshot paths")

    return pattern_names, inconsistency_ids, page_urls, data.get("raw_observations", {}).get("has_dark_mode", False)


# ─── tokens.json ─────────────────────────────────────────────────────────────

def validate_tokens(data, audit_url, has_dark_mode, report):
    report.set_file("tokens.json")

    # Top-level required fields
    check_required_field(data, "app_url", str, report)
    check_required_field(data, "extraction_date", str, report)

    # URL match
    if "app_url" in data and audit_url:
        if data["app_url"] != audit_url:
            report.error(f"app_url '{data['app_url']}' does not match audit-results.json '{audit_url}'")
        else:
            report.ok("app_url matches audit-results.json")

    # Source enum
    if check_required_field(data, "source", str, report):
        if check_enum(data["source"], TOKEN_SOURCES, report, "source"):
            report.ok(f"source = '{data['source']}' is valid")

    # Colors
    token_names = set()

    if check_required_field(data, "colors", dict, report):
        colors = data["colors"]
        for subcategory in ["brand", "status", "surface", "text", "border"]:
            if check_non_empty_array(colors, subcategory, report, "colors") if subcategory in ["brand", "status", "surface", "text"] else True:
                if subcategory in colors and isinstance(colors[subcategory], list):
                    for i, entry in enumerate(colors[subcategory]):
                        ctx = f"colors.{subcategory}[{i}]"
                        check_required_field(entry, "name", str, report, ctx)
                        if "name" in entry:
                            token_names.add(entry["name"])

                        # Status colors need light.bg/text/border
                        if subcategory == "status":
                            if check_required_field(entry, "light", dict, report, ctx):
                                light = entry["light"]
                                for prop in ["bg", "text", "border"]:
                                    check_required_field(light, prop, str, report, f"{ctx}.light")
                            if has_dark_mode and "dark" not in entry:
                                report.error(f"{ctx}: App has dark mode but no 'dark' object provided")

                        # Surface/text need light, dark if dark mode
                        if subcategory in ["surface", "text", "border"]:
                            check_required_field(entry, "light", str, report, ctx)
                            if has_dark_mode and "dark" not in entry:
                                report.warn(f"{ctx}: App has dark mode but no 'dark' value")

                        # Figma RGB validation for brand colors
                        if subcategory == "brand" and "figma_rgb" in entry:
                            rgb = entry["figma_rgb"]
                            for ch in ["r", "g", "b"]:
                                if ch in rgb:
                                    if not (0 <= rgb[ch] <= 1):
                                        report.error(f"{ctx}.figma_rgb.{ch} = {rgb[ch]} is out of range [0, 1]")
                            report.ok(f"{ctx} has valid figma_rgb") if all(0 <= rgb.get(ch, 0) <= 1 for ch in ["r", "g", "b"]) else None

            elif subcategory == "border":
                # Border is not strictly required but should exist
                if subcategory not in colors:
                    report.warn("colors.border not present")

        report.ok(f"colors has all required subcategories")

    # Spacing
    if check_required_field(data, "spacing", dict, report):
        if check_non_empty_array(data["spacing"], "scale", report, "spacing"):
            for i, entry in enumerate(data["spacing"]["scale"]):
                ctx = f"spacing.scale[{i}]"
                check_required_field(entry, "name", str, report, ctx)
                check_required_field(entry, "value_px", (int, float), report, ctx)
                if "name" in entry:
                    token_names.add(entry["name"])
            report.ok(f"spacing.scale has {len(data['spacing']['scale'])} entries")

    # Typography
    font_family_names = set()
    if check_required_field(data, "typography", dict, report):
        typo = data["typography"]

        if check_non_empty_array(typo, "families", report, "typography"):
            for i, entry in enumerate(typo["families"]):
                ctx = f"typography.families[{i}]"
                check_required_field(entry, "name", str, report, ctx)
                check_required_field(entry, "family", str, report, ctx)
                check_required_field(entry, "usage", str, report, ctx)
                if "name" in entry:
                    font_family_names.add(entry["name"])
                    token_names.add(entry["name"])

        if check_non_empty_array(typo, "styles", report, "typography"):
            categories_found = set()
            for i, entry in enumerate(typo["styles"]):
                ctx = f"typography.styles[{i}]"
                check_required_field(entry, "name", str, report, ctx)

                if check_required_field(entry, "category", str, report, ctx):
                    check_enum(entry["category"], TYPOGRAPHY_CATEGORIES, report, f"{ctx}.category")
                    categories_found.add(entry["category"])

                check_required_field(entry, "font_family", str, report, ctx)
                if "font_family" in entry and entry["font_family"] not in font_family_names:
                    report.error(f"{ctx}.font_family '{entry['font_family']}' not found in typography.families")

                check_required_field(entry, "size_px", (int, float), report, ctx)

                if check_required_field(entry, "weight", int, report, ctx):
                    check_enum(entry["weight"], FONT_WEIGHTS, report, f"{ctx}.weight")

                check_required_field(entry, "line_height", (int, float), report, ctx)

                if "name" in entry:
                    token_names.add(entry["name"])

            # Check minimum coverage
            for required_cat in ["heading", "body", "code"]:
                if required_cat not in categories_found:
                    report.error(f"typography.styles missing category '{required_cat}' — need at least one heading, body, and code style")
                else:
                    report.ok(f"typography.styles has '{required_cat}' category")

    # Border radius
    if check_non_empty_array(data, "border_radius", report):
        for i, entry in enumerate(data["border_radius"]):
            ctx = f"border_radius[{i}]"
            check_required_field(entry, "name", str, report, ctx)
            check_required_field(entry, "value_px", (int, float), report, ctx)
            if "name" in entry:
                token_names.add(entry["name"])
        report.ok(f"border_radius has {len(data['border_radius'])} entries")

    # Elevation (optional)
    if "elevation" in data and isinstance(data["elevation"], list):
        for i, entry in enumerate(data["elevation"]):
            ctx = f"elevation[{i}]"
            check_required_field(entry, "name", str, report, ctx)
            if check_required_field(entry, "light", dict, report, ctx):
                check_required_field(entry["light"], "css", str, report, f"{ctx}.light")
            if "name" in entry:
                token_names.add(entry["name"])
        report.ok(f"elevation has {len(data['elevation'])} entries")

    return token_names


# ─── components.json ─────────────────────────────────────────────────────────

def validate_components(data, audit_url, pattern_names, inconsistency_ids, token_names, report):
    report.set_file("components.json")

    # Top-level
    check_required_field(data, "app_url", str, report)
    check_required_field(data, "extraction_date", str, report)

    # URL match
    if "app_url" in data and audit_url:
        if data["app_url"] != audit_url:
            report.error(f"app_url '{data['app_url']}' does not match audit-results.json '{audit_url}'")
        else:
            report.ok("app_url matches audit-results.json")

    # Components
    slugs = set()
    component_names = set()

    if check_non_empty_array(data, "components", report):
        for i, comp in enumerate(data["components"]):
            ctx = f"components[{i}]"

            # Name
            if check_required_field(comp, "name", str, report, ctx):
                name = comp["name"]
                component_names.add(name)
                if pattern_names and name not in pattern_names:
                    report.error(f"{ctx}: name '{name}' not found in audit-results.json patterns")

            # Slug
            if check_required_field(comp, "slug", str, report, ctx):
                slug = comp["slug"]
                if not SLUG_PATTERN.match(slug):
                    report.error(f"{ctx}: slug '{slug}' does not match pattern ^[a-z0-9-]+$")
                if slug in slugs:
                    report.error(f"{ctx}: duplicate slug '{slug}'")
                slugs.add(slug)

            check_required_field(comp, "description", str, report, ctx)

            # Complexity enum
            if check_required_field(comp, "complexity", str, report, ctx):
                check_enum(comp["complexity"], COMPLEXITY_LEVELS, report, f"{ctx}.complexity")

            # Category enum
            if check_required_field(comp, "category", str, report, ctx):
                check_enum(comp["category"], PATTERN_CATEGORIES, report, f"{ctx}.category")

            check_required_field(comp, "pages", list, report, ctx)

            # Variants
            if check_non_empty_array(comp, "variants", report, ctx):
                for j, var in enumerate(comp["variants"]):
                    vctx = f"{ctx}.variants[{j}]"
                    check_required_field(var, "name", str, report, vctx)
                    check_required_field(var, "description", str, report, vctx)

                    # Token cross-reference
                    if "tokens_used" in var and isinstance(var["tokens_used"], list) and token_names:
                        for tok in var["tokens_used"]:
                            if tok not in token_names:
                                report.error(f"{vctx}: tokens_used references '{tok}' not found in tokens.json")

            # Layout
            if check_required_field(comp, "layout", dict, report, ctx):
                if check_non_empty_array(comp["layout"], "specs", report, f"{ctx}.layout"):
                    for j, spec in enumerate(comp["layout"]["specs"]):
                        sctx = f"{ctx}.layout.specs[{j}]"
                        check_required_field(spec, "property", str, report, sctx)
                        check_required_field(spec, "value", str, report, sctx)

            # Do/Don't
            if check_non_empty_array(comp, "dos_and_donts", report, ctx):
                for j, dd in enumerate(comp["dos_and_donts"]):
                    dctx = f"{ctx}.dos_and_donts[{j}]"
                    if check_required_field(dd, "type", str, report, dctx):
                        check_enum(dd["type"], DO_DONT_TYPES, report, f"{dctx}.type")
                    check_required_field(dd, "text", str, report, dctx)

            # Related inconsistencies cross-reference
            if "related_inconsistencies" in comp and isinstance(comp["related_inconsistencies"], list) and inconsistency_ids:
                for inc_ref in comp["related_inconsistencies"]:
                    if inc_ref not in inconsistency_ids:
                        report.error(f"{ctx}: related_inconsistencies references '{inc_ref}' not found in audit-results.json")

        report.ok(f"components has {len(data['components'])} entries")

        # Check all pattern names are covered
        if pattern_names:
            uncovered = pattern_names - component_names
            if uncovered:
                for pat in sorted(uncovered):
                    report.warn(f"Pattern '{pat}' from audit-results.json has no matching component")
            else:
                report.ok(f"All {len(pattern_names)} patterns from audit have matching components")

        # Slug uniqueness summary
        report.ok(f"All {len(slugs)} slugs are unique")

    # Action items
    if "action_items" in data and isinstance(data["action_items"], list):
        action_ids = set()
        for i, ai in enumerate(data["action_items"]):
            ctx = f"action_items[{i}]"

            if check_required_field(ai, "id", str, report, ctx):
                if ai["id"] in action_ids:
                    report.error(f"{ctx}: duplicate action item ID '{ai['id']}'")
                action_ids.add(ai["id"])

            check_required_field(ai, "title", str, report, ctx)
            check_required_field(ai, "description", str, report, ctx)

            if check_required_field(ai, "priority", str, report, ctx):
                check_enum(ai["priority"], PRIORITY_LEVELS, report, f"{ctx}.priority")

            if check_required_field(ai, "effort", str, report, ctx):
                check_enum(ai["effort"], EFFORT_LEVELS, report, f"{ctx}.effort")

            if check_required_field(ai, "labels", list, report, ctx):
                for label in ai["labels"]:
                    check_enum(label, ACTION_LABELS, report, f"{ctx}.labels")

            # Cross-reference inconsistency
            if "related_inconsistency" in ai and ai["related_inconsistency"] and inconsistency_ids:
                if ai["related_inconsistency"] not in inconsistency_ids:
                    report.error(f"{ctx}: related_inconsistency '{ai['related_inconsistency']}' not found in audit-results.json")

        report.ok(f"action_items has {len(data['action_items'])} entries with unique IDs")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-handoff.py <project-directory>")
        print("       The directory should contain audit-results.json, tokens.json, components.json")
        sys.exit(2)

    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.is_dir():
        print(f"Error: '{project_dir}' is not a directory")
        sys.exit(2)

    report = Report()

    # ── Load files ──

    audit_path = project_dir / "audit-results.json"
    tokens_path = project_dir / "tokens.json"
    components_path = project_dir / "components.json"

    audit_data = load_json(audit_path, report)
    tokens_data = load_json(tokens_path, report)
    components_data = load_json(components_path, report)

    if audit_data is None:
        report.set_file("audit-results.json")
        report.error("File not found or invalid JSON — this file is required")
        report.print_report()
        sys.exit(2)

    # ── Validate audit-results.json ──

    pattern_names, inconsistency_ids, page_urls, has_dark_mode = validate_audit(
        audit_data, project_dir, report
    )
    audit_url = audit_data.get("app_url")

    # ── Validate tokens.json ──

    token_names = set()
    if tokens_data is not None:
        token_names = validate_tokens(tokens_data, audit_url, has_dark_mode, report)
    else:
        report.set_file("tokens.json")
        report.warn("File not found — skipping token validation and token cross-reference checks")

    # ── Validate components.json ──

    if components_data is not None:
        validate_components(
            components_data, audit_url, pattern_names, inconsistency_ids, token_names, report
        )
    else:
        report.set_file("components.json")
        report.warn("File not found — skipping component validation")

    # ── Print report ──

    passed = report.print_report()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
```
