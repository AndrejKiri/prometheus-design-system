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
  version: '3.0'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
---

# Reverse-Engineer a Design System

## Table of Contents

- [When to Use](#when-to-use)
- [Core Principle](#core-principle)
- [Supporting Files](#supporting-files)
- [Tool Capability Matrix](#tool-capability-matrix)
- [Shared Project Folder](#shared-project-folder)
- [Phase 0 — Scope & Auth](#phase-0--scope--auth)
- [Phase 1 — Visual Audit](#phase-1--visual-audit)
- [Phase 1-Source — Source Audit (alternative/supplement)](#phase-1-source--source-audit-alternativesupplement)
- [Phase 2 — Extract Tokens](#phase-2--extract-tokens)
- [Phase 3 — Extract Components](#phase-3--extract-components)
- [Phase 4 — Build Docs Site](#phase-4--build-docs-site)
- [Phase 5 — Figma Plugin](#phase-5--figma-plugin)
- [Phase 6 — Deploy & QA](#phase-6--deploy--qa)
- [Quality Checklist](#quality-checklist)
- [Reference Implementation Notes](#reference-implementation-notes)

## When to Use

- Audit a website or web app's UI for patterns, tokens, and inconsistencies.
- Extract a design system from an existing codebase or live site.
- Produce a design system documentation site from an existing UI.
- Create a Figma bootstrap plugin from extracted design tokens.

## Core Principle

**Derive, not invent.** Every token, component, and pattern must come from the actual application being audited. Document what exists, then resolve inconsistencies with reasoning and a canonical choice.

**Exception — docs-site meta components.** The documentation site itself has UI (theme toggle, sidebar nav button, copy-code button). Tag these with `origin: "docs-meta"` in `components.json` so they are not mistaken for derived components. Keep them separate in the catalog if the user wants strict provenance.

## Supporting Files

All referenced files live alongside this SKILL.md:

| File | Purpose |
|------|---------|
| [`schemas/audit-results.schema.json`](schemas/audit-results.schema.json) | JSON Schema for Phase 1 output |
| [`schemas/tokens.schema.json`](schemas/tokens.schema.json) | JSON Schema for Phase 2 output |
| [`schemas/components.schema.json`](schemas/components.schema.json) | JSON Schema for Phase 3 output |
| [`schemas/source-audit.schema.json`](schemas/source-audit.schema.json) | JSON Schema for optional source audit |
| [`scripts/validate-handoff.py`](scripts/validate-handoff.py) | Zero-dep Python validator for all handoff files |
| [`templates/figma-plugin/manifest.json.template`](templates/figma-plugin/manifest.json.template) | Figma plugin manifest skeleton |
| [`templates/figma-plugin/code.js.template`](templates/figma-plugin/code.js.template) | Figma plugin skeleton with font-fallback pattern |

Treat schemas as authoritative. Prose in this doc summarizes; schemas define.

## Tool Capability Matrix

Before starting, identify which tool you are.

| Capability | Perplexity Computer | Claude Code | Claude Cowork |
|---|---|---|---|
| Headless browser (Playwright) | ✅ built-in | ⚠ MCP only | ❌ |
| Interactive browser (Computer Use / Chrome ext) | ✅ | ❌ | ✅ |
| Filesystem access | ✅ | ✅ strong | ✅ |
| Batch-edit many files via Python | ✅ | ✅ | ❌ |
| Visual QA / screenshots | ✅ | ⚠ MCP only | ✅ slow |
| **Best at** | Full end-to-end | Phases 2-6 + source audit | Phases 0-1 (visual) |

**Handoff pattern.** When tools combine: Cowork or Perplexity runs Phase 0-1 and writes `audit-results.json` + `screenshots/`. Claude Code picks up from Phase 2 pointed at the same folder.

**If you are Claude Code with no browser:** tell the user you can do Phase 1-Source from their repo, or accept an `audit-results.json` produced by another tool.

## Shared Project Folder

All tools point at the same project folder. Create a `CLAUDE.md` file at the root:

```markdown
# Design System Project

## Target Application
- URL: <app-url>
- Source repo: <repo-url or "N/A">
- Auth: <method, credentials stored securely, not in this file>

## Scope
- Tier: <core | core-plus-data | full | custom>
- Pages audited: <count>

## Progress
- [ ] Phase 0: Scope assessment
- [ ] Phase 1: Visual audit (tool: ___)
- [ ] Phase 1-Source: Source audit (tool: ___, optional)
- [ ] Phase 2: Token extraction
- [ ] Phase 3: Component extraction
- [ ] Phase 4: Documentation site
- [ ] Phase 5: Figma plugin
- [ ] Phase 6: Deploy + QA

## Handoff Files
- audit-results.json  — Phase 1 output
- source-audit.json   — Phase 1-Source output (optional)
- tokens.json         — Phase 2 output
- components.json     — Phase 3 output
- screenshots/        — reference screenshots
```

### Validating Handoff Files

After each phase that produces JSON, run:

```bash
python docs/scripts/validate-handoff.py <project-directory>
```

Validator is progressive — checks whatever files exist. Exit codes: 0 pass, 1 fail, 2 missing required files. Checks required fields, enum correctness, cross-references (INC IDs ↔ tokens ↔ patterns ↔ components), dark-mode consistency, screenshot existence, slug uniqueness.

---

## Phase 0 — Scope & Auth

**Must run first.** Do not skip.

### 0.1 Gather info

Ask the user:
1. URL of the application.
2. Authentication — credentials, SSO details, or API token.
3. Source code repo URL (optional — enables exact token extraction).
4. GitHub repo for action-item linking (optional).

Test login immediately. If it fails, stop and ask for corrected credentials — do not proceed with a partial audit.

### 0.2 Discover routes

- Crawl navigation links from the authenticated home page.
- If source available: parse route definitions (React Router, Next.js pages/app, Vue Router, etc.).

### 0.3 Present scope options

| App size | Recommendation |
|---|---|
| < 15 pages | Audit everything. No scoping. |
| 15-30 pages | Recommend **core-plus-data**. Flag admin/system as optional. |
| 30+ pages | Strongly recommend focusing on a subset. Let the user pick. |

Present categorized routes (core UI / data views / admin-system / edge cases) and wait for the user to choose before proceeding.

### 0.4 Check for pre-seeded data

Some pages look empty without sample data (dashboards, alert pages). Ask which pages might show empty states — screenshot both populated and empty where relevant.

---

## Phase 1 — Visual Audit

Requires browser access.

### 1.1 Browse every page in scope

```javascript
const { chromium } = await import("playwright");
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1400, height: 900 } });
const page = await context.newPage();
// login first if needed
for (const url of scopedRoutes) {
  await page.goto(url, { waitUntil: "networkidle" });
  await page.screenshot({ path: `screenshots/${pageName}.jpg`, type: "jpeg", quality: 85 });
  // catalog what you see
}
```

For each page document: URL, name, every visible UI element type, colors / font sizes / spacing / radii observed, interactive patterns. Expand accordions, click tabs, hover buttons — screenshot each state.

### 1.2 Catalog every UI pattern

Inventory table per page with columns: Pattern | Pages Found | Count | Variations. Be exhaustive within scope — scroll to the bottom, expand everything, miss nothing.

### 1.3 Identify inconsistencies

This is the real value. For each:
1. What is inconsistent (file paths/lines if source available).
2. Table of variants across pages.
3. Canonical choice + reasoning.
4. Concrete fix (code diff if possible).

Look for: same concept with different implementations, hardcoded values vs tokens, missing status normalization (`UP` vs `up` vs `active`), style drift, duplicated logic.

### 1.4 Save audit results

Write `audit-results.json` conforming to [`schemas/audit-results.schema.json`](schemas/audit-results.schema.json). Key fields: `scope`, `pages_audited`, `patterns`, `inconsistencies`, `raw_observations`. Every inconsistency needs a unique `id` (`INC-001` etc.) — other files cross-reference these.

**Before handing off:** run `python docs/scripts/validate-handoff.py .` and fix every error.

---

## Phase 1-Source — Source Audit (alternative/supplement)

When the source repo is available.

```bash
git clone --depth 1 <repo-url> source-code
```

**Priority reading order for large codebases:**
1. `package.json` — framework, UI library, CSS approach.
2. Theme config file (search for `theme`, `tokens`, `colors`).
3. Route definitions.
4. Shared/common components directory.
5. Layout/shell components.
6. Page-level components (one per route in scope).

Write `source-audit.json` conforming to [`schemas/source-audit.schema.json`](schemas/source-audit.schema.json).

---

## Phase 2 — Extract Tokens

Read `audit-results.json` (and `source-audit.json` if available). Produce `tokens.json` conforming to [`schemas/tokens.schema.json`](schemas/tokens.schema.json).

### Coverage requirements

| Category | Required content |
|---|---|
| `colors.brand` | ≥ 1 entry (header/accent) |
| `colors.status` | ≥ 2 entries (typically ok + error); each with `light.{bg,text,border}`; `dark` required if app has dark mode |
| `colors.surface` | at minimum page-bg, card-bg |
| `colors.text` | at minimum primary, secondary |
| `spacing.scale` | named scale (xs/sm/md/lg/xl) with px values |
| `typography.families` | ≥ body font; include `figma_family` safe-name for Phase 5 |
| `typography.styles` | ≥ 1 heading, 1 body, 1 code style |
| `border_radius` | named scale |

### Pre-compute for Figma

Fill `figma_rgb` (0-1 range) on brand colors and `figma_effects` on shadows. Saves Phase 5 conversion work.

**Validate:** `python docs/scripts/validate-handoff.py .`

---

## Phase 3 — Extract Components

Read `audit-results.json` and `tokens.json`. Produce `components.json` conforming to [`schemas/components.schema.json`](schemas/components.schema.json).

Per component, document: name (PascalCase), slug (lowercase-hyphenated), description, complexity (`simple`/`medium`/`complex`), category, pages, props, variants (with `mock_css_class` + `mock_html` for Phase 4 rendering), layout specs, dos/donts, accessibility notes, code example, `related_inconsistencies`, `origin` (`derived` or `docs-meta`).

### Complexity tiers

- **Simple** — stateless, few props (EmptyState, ErrorAlert, InfoCard).
- **Medium** — some internal state or composition (CodeBlock, KeyValueTable, HealthPanel).
- **Complex** — significant interactivity (DataTable, FilterToolbar, AppShell).

### Action items

Populate `action_items[]` with PR-style task cards — one per inconsistency plus any improvement opportunities. Each card: priority, effort, labels, before/after, files changed.

**Validate:** `python docs/scripts/validate-handoff.py .`

---

## Phase 4 — Build Docs Site

Read `tokens.json`, `components.json`, `audit-results.json`. Produce a static HTML/CSS/JS site — no frameworks, no build step.

### File structure

```
design-system/
├── index.html                      # Home page with card grid
├── tokens.html                     # Token docs with visual swatches
├── icons.html                      # Icon inventory (if applicable)
├── components.html                 # Component catalog overview
├── components/<slug>.html          # Individual component pages
├── patterns.html                   # Composition patterns
├── action-items.html               # PR-style task cards
├── audit-report.html               # Full audit findings
├── inconsistencies.html            # Inconsistency resolution log
├── migration.html                  # Migration/adoption guide (optional)
├── changelog.html                  # Version history
├── figma.html                      # Figma plugin docs
├── figma-plugin/                   # Built from templates/
├── screenshots/
├── styles.css                      # Single global stylesheet
├── main.js                         # Vanilla JS IIFE
└── README.md
```

**Path collision warning.** `components.html` and `components/` coexist. Some static servers resolve `/components` ambiguously. Always link with explicit `.html` (`components.html`) or trailing slash (`components/<slug>.html`) — never bare `/components`.

### CSS architecture

Single stylesheet with CSS custom properties. Prefix all tokens with `--doc-`. Brand tokens may embed the product name when it aids readability (e.g., `--doc-brand-orange` for a product whose brand color is orange) — this is a readability choice, not a requirement. `--doc-brand-primary` is the generic form.

Organize sections with clear comment delimiters: Custom Properties → Reset → Layout → Typography → Code → Tables → Cards → Visual examples (`.mock-*`) → Color swatches → Do/Don't grid → Callouts → PR task cards → Responsive.

Light/dark with `[data-theme="dark"]` selector. Respect `prefers-color-scheme` on first load, persist choice in localStorage.

### main.js — vanilla IIFE

1. Theme toggle (light/dark, respects `prefers-color-scheme`).
2. Active nav highlighting.
3. Mobile sidebar burger toggle + overlay.
4. Auto-generated copy buttons on `<pre>` blocks.
5. Collapsible sidebar with localStorage persistence.
6. GitHub issue links on action-item cards (if repo URL provided).

### Navigation

Sidebar nav is hardcoded identically in every HTML file. When adding/removing a page, **always batch-update with Python**:

```python
import glob
OLD_NAV = '<the old nav block>'
NEW_NAV = '<the new nav block>'
for f in sorted(glob.glob("*.html") + glob.glob("components/*.html")):
    c = open(f).read().replace(OLD_NAV, NEW_NAV)
    open(f, "w").write(c)
```

Paths: top-level pages `href="tokens.html"`; component pages `href="../tokens.html"`.

### Component page template

Section order (all `<h2 id="...">` for deep-linking):

1. Title + subtitle (`<h1>` + `<p class="doc-subtitle">`).
2. `#description`.
3. Do/Don't grid (no heading — visual block between title and description).
4. `#design` — visual examples via `.mock-*` CSS classes.
5. Component Reference — collapsible `<details>` with screenshots and live-app links.
6. `#implementation` — source code with syntax-highlighted spans.
7. `#layout` — pixel measurements table.
8. `#accessibility` — ARIA, contrast, keyboard notes.

### Mock component CSS

`.mock-*` classes render static previews on component pages. Examples: `.mock-badge` + `.mock-badge-{ok,err,warn,info,unknown}`, `.mock-panel` + variants, `.mock-app-shell`, `.mock-app-header`.

### Syntax highlighting (inline spans)

`.cmt` comments · `.kw` keywords · `.str` strings · `.num` numbers · `.tag` tags · `.attr` attributes.

### Action items page

PR-style task cards with: number, title, labels (inconsistency / tokens / component / easy / medium / hard), problem description, before/after mockups, code diff, files changed. `main.js` turns these into GitHub issue links if a repo URL is in the project config.

---

## Phase 5 — Figma Plugin

Copy templates, populate from `tokens.json`, ship.

```bash
cp docs/templates/figma-plugin/manifest.json.template figma-plugin/manifest.json
cp docs/templates/figma-plugin/code.js.template       figma-plugin/code.js
```

Replace `{{PROJECT_NAME}}` and `{{UNIQUE_ID}}` in the manifest. In `code.js`, replace the `// {{POPULATE_FROM_…}}` markers with the JS object literals derived from `tokens.json`.

### Font rules (learned from real bugs)

- Figma uses `"Semi Bold"` with a space. `"SemiBold"` crashes.
- `"DejaVu Sans Mono"` and `"Roboto Mono"` are **not** bundled. Use `"Courier New"` for monospace.
- `"Inter"` is the ultimate safe fallback — always bundled.
- Some families ship `"Regular"` only — requesting `"Medium"`/`"Bold"` throws. Always wrap `loadFontAsync` in try/catch.

The template already implements the three-level fallback (requested family+weight → requested family+Regular → Inter+weight → Inter+Regular).

### Distributing

Zip the `figma-plugin/` directory into `figma-plugin.zip` and commit. Users import via **Figma → Plugins → Development → Import plugin from manifest**.

---

## Phase 6 — Deploy & QA

Docs site is pure static HTML. Deploy via:

- **GitHub Pages** — push to `main`, enable Pages.
- **Any static host** — Netlify, Vercel, S3.
- **Local** — `npx serve . -l 3000`.

### Visual QA

Open the deployed site and verify:

- Light and dark mode on every page.
- Mobile responsive — burger menu works.
- All screenshots load in collapsible component references.
- Copy buttons work on every code block.
- No broken links (`../` vs direct).
- Component page section order matches the template.

If no browser available, tell the user the above checklist and ask them to spot-check.

---

## Quality Checklist

- [ ] Every page within the selected scope was visited and screenshotted.
- [ ] All inconsistencies documented with resolution reasoning.
- [ ] Token values match the actual source (not approximated).
- [ ] `validate-handoff.py` exits 0.
- [ ] All component pages follow the template section order.
- [ ] Light and dark mode render correctly on every page.
- [ ] Navigation is identical across all HTML files.
- [ ] Mobile responsive — burger menu works.
- [ ] Screenshots load in collapsible references.
- [ ] Figma plugin runs without crashing — font fallbacks tested.
- [ ] Copy buttons work on all code blocks.
- [ ] `CLAUDE.md` progress checklist fully checked off.

---

## Reference Implementation Notes

The [Prometheus Design System](https://github.com/AndrejKiri/prometheus-design-system) is the reference implementation. It documents ~17 components extracted from the Prometheus monitoring UI plus 2 docs-site meta components, with a working Figma plugin and 11 screenshots.

**Known deviations from strict skill output** (the reference was hand-authored before this skill existed):

- Handoff JSON files (`audit-results.json`, `tokens.json`, `components.json`) are not committed. Regenerating via the skill requires authoring them first.
- Two components (`theme-toggle`, `nav-button`) are `origin: "docs-meta"` — parts of the docs site chrome, not extracted from Prometheus.
- CSS uses `--doc-brand-orange` rather than the generic `--doc-brand-primary` — a readability choice for a product whose brand color is orange.
- `migration.html` is included. Optional in the skill; include when the design system describes a migration path from the existing UI.
- `additional_screenshots` (interactive states like modals, expanded accordions) are not captured — the reference only has the 11 static page shots.

When generating from scratch via this skill, produce the JSON files first, tag docs-meta components explicitly, and decide brand-token naming up front.
