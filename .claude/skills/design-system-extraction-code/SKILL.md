---
name: design-system-extraction-code
description: >
  Extract design tokens and components from a visual audit package or source
  repo. Produces tokens.json, components.json, a static design system docs
  site, and a Figma bootstrap plugin. Picks up from audit-results.json
  (produced by the design-system-extraction-cowork skill) or from a source repo alone.
  Requires filesystem access. No browser needed.
metadata:
  author: AndrejKiri
  version: '0.2'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
  paired-skill: design-system-extraction-cowork (docs/skill-cowork/SKILL.md)
---

# Design System Extraction — Claude Code Skill

---

## Core Principle

**Derive, not invent.** Every token, component, and pattern must come from the actual application. Document what exists, then resolve inconsistencies with reasoning and a canonical choice.

**Exception — docs-site meta components.** The documentation site has its own UI (theme toggle, sidebar nav button, copy-code button). Tag these `origin: "docs-meta"` in `components.json` — do not mistake them for derived components.

---

## Phase Overview

```
[design-system-extraction-cowork]
         │
         ▼ audit-results.json + screenshots/
 Phase 1-Source (optional)
         │ source-audit.json
         ▼
    Phase 2: Token Extraction
         │ tokens.json
         ▼
    Phase 3: Component Extraction
         │ components.json
         ▼
    Phase 4: Docs Site (gen.py)
         │ design-system/
         ▼
    Phase 5: Figma Plugin
         │ design-system/figma-plugin/
         ▼
    Phase 6: Deploy + QA → GitHub Pages
```

Each phase validates with `python3 validate-handoff.py <project-folder>` before proceeding.

---

## Supporting Files

| File | Purpose |
|------|---------|
| [`schemas/audit-results.schema.json`](schemas/audit-results.schema.json) | Schema for `audit-results.json` (input) |
| [`schemas/source-audit.schema.json`](schemas/source-audit.schema.json) | Schema for `source-audit.json` (Phase 1-Source output) |
| [`schemas/tokens.schema.json`](schemas/tokens.schema.json) | Schema for `tokens.json` (Phase 2 output) |
| [`schemas/components.schema.json`](schemas/components.schema.json) | Schema for `components.json` (Phase 3 output) |
| [`scripts/validate-handoff.py`](scripts/validate-handoff.py) | Progressive validator — run after each phase |
| [`templates/figma-plugin/manifest.json.template`](templates/figma-plugin/manifest.json.template) | Figma plugin manifest skeleton |
| [`templates/figma-plugin/code.js.template`](templates/figma-plugin/code.js.template) | Figma plugin skeleton with font-fallback pattern |

Schemas are authoritative. Prose summarizes; schemas define.

---

## Entry Check — Start Here

### 1. Resolve the project folder

Check how the skill was invoked:

| Invocation | Project folder |
|------------|---------------|
| `/design-system-extraction-code ~/path/to/folder` | Use that path |
| `/design-system-extraction-code ~/path/to/audit-results.json` | Use that file's parent directory |
| `/design-system-extraction-code ~/path/to/audit.zip` | Extract the zip first, then use the extracted folder |
| No argument | Ask the user: *"Where is the project folder or handoff zip from the design-system-extraction-cowork skill?"* |

All output files (`source-audit.json`, `tokens.json`, `components.json`, `design-system/`) are written into this folder. Confirm the path with the user before writing anything.

### 2. Check what exists in the project folder

| Situation | Action |
|-----------|--------|
| `audit-results.json` exists and validates | → Start Phase 2 |
| `audit-results.json` exists but has errors | → Fix errors, then Phase 2 |
| No `audit-results.json`, but source repo provided | → Run Phase 1-Source, then Phase 2 |
| Neither | → Stop. Tell the user to run the `design-system-extraction-cowork` skill first, or provide a source repo URL |

Run the validator immediately on any existing files. The skill directory is where the `design-system-extraction-code/` tree lives, **not** the project folder:

```bash
SKILL_DIR="$(dirname "$(find ~/.claude ~/.config/claude -name design-system-extraction-code -type d 2>/dev/null | head -1)")"
python3 "$SKILL_DIR/design-system-extraction-code/scripts/validate-handoff.py" --project "<project-folder>"
```

Or if invoked via a slash command that already resolves the skill path, use the literal path from the arguments. The validator accepts either `--project <path>` or a positional `<path>` — prefer `--project` in scripts to avoid ambiguity.

The validator is progressive — it checks whatever files exist. Exit 0 = pass, 1 = errors, 2 = missing required files.

---

## Shared Project Folder

All output files go in the project folder. If `CLAUDE.md` exists (created by the Cowork skill), read it for context. If it does not exist, create it:

```markdown
# Design System Project

## Target Application
- URL: <app-url>
- Source repo: <repo-url or "N/A">
- Auth: <method — do NOT store credentials here>

## Scope
- Tier: <core | core-plus-data | full | custom>
- Pages audited: <count>

## Progress
- [ ] Phase 0: Scope assessment
- [ ] Phase 1: Visual audit (tool: ___)
- [ ] Phase 1-Source: Source audit (tool: claude-code, optional)
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

Check off progress items as you complete each phase.

---

## Phase 1-Source — Source Audit (optional supplement)

Run this when a source repo is available. Provides exact token values and file mappings that visual audit cannot reliably capture. Skip if no repo is provided.

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

Write `source-audit.json` in the project folder, conforming to [`schemas/source-audit.schema.json`](schemas/source-audit.schema.json).

**Validate:** `python3 <path-to-this-skill>/scripts/validate-handoff.py <project-folder>`

---

## Phase 2 — Extract Tokens

Read `audit-results.json` (and `source-audit.json` if available). Produce `tokens.json` conforming to [`schemas/tokens.schema.json`](schemas/tokens.schema.json).

### Coverage requirements

| Category | Required content |
|---|---|
| `colors.brand` | ≥ 1 entry (header/accent) |
| `colors.status` | ≥ 2 entries (typically ok + error); each with `light.{bg,text,border}`; `dark` required if app has dark mode. Use `"transparent"` for border when the status has no visible border (not `""` or `null`) |
| `colors.surface` | at minimum page-bg, card-bg |
| `colors.text` | at minimum primary, secondary |
| `spacing.scale` | named scale (xs/sm/md/lg/xl) with px values |
| `spacing.semantic` | optional — named pairs like `page-padding`, `card-gap`, `section-margin` that reference the scale |
| `typography.families` | ≥ body font; include `figma_family` safe-name for Phase 5 |
| `typography.styles` | ≥ 1 heading, 1 body, 1 code style |
| `border_radius` | named scale |
| `breakpoints` | optional — named responsive breakpoints (mobile/tablet/desktop/wide) with px values |
| `motion` | optional — named durations (fast/base/slow) and easing curves (ease-in-out, etc.) |
| `domain_lexicon` | optional but encouraged — product-specific glossary (e.g. PromQL operators, custom status values) the docs site should render as a reference |
| CSS custom-property table | Tokens page must include a table mapping every token name to its `--doc-*` CSS var, so consumers can copy-paste |

### Handling gaps in audit-results.json

When `audit-results.json` is incomplete (missing pages, sparse elements, placeholder screenshots), do not stop. Document the gap and continue:

1. Note missing pages in `tokens.json` under a `"gaps"` array: `{ "type": "missing-page", "page": "/alerts", "reason": "not in audit scope" }`.
2. For tokens that can't be derived visually, mark them with `"source": "inferred"` and add a note.
3. Set `tokens.json[].source = "visual-audit"` unless you have source-code confirmation — never upgrade to `"both"` speculatively.

A partial audit is a valid input. Produce the best output you can from what exists, and flag the gaps explicitly.

### `typography.styles[].font_family` is a reference key

`font_family` must exactly match a `typography.families[].name` value — it is NOT a CSS font-family string. Example:

```json
"families": [{ "name": "body-sans", "family": "Inter, sans-serif", "usage": "body text" }],
"styles":   [{ "name": "body/regular", "font_family": "body-sans", ... }]
```

The validator will error if `font_family` doesn't match any `families[].name` and will list the available names in the error message.

### Optional: rationale field

When a brand token's value isn't obvious from name alone (e.g. a specific hex chosen for WCAG contrast, a size picked to match a library's default), add `"rationale": "<why>"` on the token entry. Reserve for non-obvious choices — if the reason is "matches the header color", don't bother.

### Pre-compute for Figma

Fill `figma_rgb` (0–1 range) on brand colors and `figma_effects` on shadows. Saves Phase 5 conversion work.

Formula: divide each 0–255 channel value by 255. Example — `#F5A623` → `r = 245/255 = 0.961`, `g = 166/255 = 0.651`, `b = 35/255 = 0.137`. The validator checks that all channels are in [0, 1].

**Validate:** `python3 <path-to-this-skill>/scripts/validate-handoff.py <project-folder>`

---

## Phase 3 — Extract Components

Read `audit-results.json` and `tokens.json`. Produce `components.json` conforming to [`schemas/components.schema.json`](schemas/components.schema.json).

Per component, document: name (PascalCase — `StatusBadge`, `HealthPanel`, `DataTable`, never `status-badge` or `Status Badge`), slug (lowercase-hyphenated — `status-badge`, matches name), description, complexity (`simple`/`medium`/`complex`), category, pages, props, variants (with `mock_css_class` + `mock_html` for Phase 4 rendering), layout specs, dos/donts, accessibility notes, code example, `related_inconsistencies`, `origin` (`derived` or `docs-meta`).

**Naming rules (enforced):** `name` is PascalCase with no spaces or hyphens. `slug` is `name.lower().replace(" ", "-")` converted to kebab-case. The two must match each other unambiguously — e.g. `StatusBadge` ↔ `status-badge`, `DataTable` ↔ `data-table`.

### Complexity tiers

- **Simple** — stateless, few props (EmptyState, ErrorAlert, InfoCard).
- **Medium** — some internal state or composition (CodeBlock, KeyValueTable, HealthPanel).
- **Complex** — significant interactivity (DataTable, FilterToolbar, AppShell).

### Action items

Populate `components.json → action_items[]` with PR-style task cards — not a separate file. One card per inconsistency (cross-reference via `related_inconsistency`) plus any improvement opportunities surfaced during component extraction.

**Target depth:** aim for **15–25 cards** for a mid-sized app. If you produce fewer than 10, the action items page looks thin and readers suspect the audit was shallow. Include every `INC-NNN` plus tokenization opportunities, accessibility gaps, responsive issues, and deprecation candidates.

Each card: `id`, `title`, `description`, `priority`, `effort`, `labels`, `related_inconsistency` (INC-NNN or null), `before` (description or code snippet of current state), `after` (description or code snippet of canonical state), `files_changed` (estimated file list — read the source repo if available).

Render on `action-items.html` as cards with:
- Priority badge (p0/p1/p2/p3) top-left.
- Effort chip (easy/medium/hard) next to priority.
- Before / After side-by-side code blocks where applicable.
- Files-changed collapsible list.
- "Open issue" link (populated by `main.js` from `GITHUB_REPO_URL`).

### Migration guide

When ≥ 3 action items share a theme (e.g. "replace hardcoded colors with tokens"), add a `migration.html` page that groups them into a step-by-step adoption plan. Link from the homepage card grid. Skip if the action items are disparate.

**Validate:** `python3 <path-to-this-skill>/scripts/validate-handoff.py <project-folder>`

---

## Phase 4 — Build Docs Site

Read `tokens.json`, `components.json`, `audit-results.json`. Produce a static HTML/CSS/JS site — no frameworks, no build step. Write all files into a `design-system/` subdirectory of the project folder.

### Homepage acknowledgements

Add a short **Acknowledgements** section below the card grid crediting:

- The audited application (URL, short description).
- The design-system-extraction pipeline (link to the skill repo if available).
- Any upstream design systems the audited app inherited from (Material, Tailwind, Mantine, etc.) if detectable from `source-audit.json`.

One `<section class="acknowledgements">` with 2–3 sentences is enough — not a full credits roll.

### Homepage card grid — 5 category cards, not 9 emoji cards

The homepage card grid has exactly **5 cards**, each tagged with a category label (no emojis):

1. **Tokens** (Foundations) — summary of color/spacing/type coverage
2. **Components** (Components) — count + link to catalog
3. **Action Items** (Components) — count + link to tasks
4. **Audit Report** (Audit) — pages audited + inconsistency count
5. **Figma Plugin** (Audit) — link to figma docs page

Each card has `<span class="card-tag">Foundations|Components|Audit</span>` to signal its nav group. Do not generate one card per HTML page — consolidate secondary pages (Patterns, Icons, Changelog, Inconsistencies, Migration) into the sidebar only.

### Homepage chrome — version chip + WIP callout

The homepage (`index.html`) header should include two elements above the card grid:

1. **Version chip** — a small `<span class="version-chip">v{VERSION}</span>` near the title. Read `{VERSION}` from `audit-results.json.audit_date` (e.g. `v2026.04.23`) or from a `version` field in CLAUDE.md if present.
2. **WIP callout** — an `<aside class="callout callout-wip">` paragraph below the title explaining this is an auto-extracted design system, not hand-authored, and may contain inferred values. One sentence is enough.

Style the version chip as a small pill (same shape as `.tag`). The WIP callout uses the standard `.callout` class with a `callout-wip` modifier (yellow-ish background).

### Generator script

**Always write a `gen.py` in the project folder** and generate HTML from it — do not write HTML files directly. This keeps regeneration fast, prevents stale content, and handles screenshots and sidebar sync correctly.

Start from [`templates/gen.py.template`](../templates/gen.py.template). Copy it to the project folder and fill in the `{{POPULATE_FROM_*}}` sections. Then run:

```bash
python3 gen.py
```

On re-runs, `gen.py` overwrites all HTML files (preventing stale content) and copies `screenshots/` fresh. Watch mode:

```bash
python3 gen.py --watch
```

**Do not write HTML files by hand** if you can express the page as a Python function. Reserve direct HTML editing for one-off cosmetic fixes that are not worth parameterizing.

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
├── screenshots/                    # Copied (not symlinked) from project root — required for GitHub Pages
├── styles.css                      # Single global stylesheet
├── main.js                         # Vanilla JS IIFE
└── README.md
```

**Path collision warning.** `components.html` and `components/` coexist. Always link with explicit `.html` (`components.html`) or trailing slash (`components/<slug>.html`) — never bare `/components`.

### CSS architecture

Single stylesheet with CSS custom properties. Prefix all tokens with `--doc-`. Brand tokens may embed the product name for readability (e.g., `--doc-brand-orange`) — `--doc-brand-primary` is the generic form.

Organize with comment delimiters: Custom Properties → Reset → Layout → Typography → Code → Tables → Cards → Visual examples (`.mock-*`) → Color swatches → Do/Don't grid → Callouts → PR task cards → Responsive.

Light/dark with `[data-theme="dark"]` selector. Respect `prefers-color-scheme` on first load, persist choice in localStorage.

### main.js — vanilla IIFE

1. Theme toggle (light/dark, respects `prefers-color-scheme`).
2. Active nav highlighting.
3. Mobile sidebar burger toggle + overlay.
4. Auto-generated copy buttons on `<pre>` blocks.
5. Collapsible sidebar with localStorage persistence.
6. GitHub issue links on action-item cards (if repo URL provided in CLAUDE.md).

### Navigation

Sidebar nav is **grouped into three sections** — not a flat list. Use this structure:

1. **Foundations** — Home, Tokens, Icons
2. **Components** — Components catalog, Patterns (composition), Action Items
3. **Audit** — Audit Report, Inconsistencies, Figma Plugin, Changelog

Section headings are `<div class="sidebar-section">` elements between the `<ul>` groups; group each section's links in its own `<ul>`. `gen.py` should render all three sections in every HTML file.

**Conditional Audit section:** if `audit-results.json` is absent (source-only run) or has `raw_observations.audit_only: false`, consolidate the Audit group so only pages that have real content are linked. Never show sidebar links that lead to 404s or empty pages — omit them from the nav rendering.

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

### Icons page

When the audited app has a recognisable icon library, render `icons.html` with:

1. **Library header** — name of the library, version if known, default size.
2. **Grouped grid** — group icons by usage category (navigation, status, action, chart, decorative). Not alphabetical.
3. **Per-icon card** — SVG preview, icon name, usage description, import code snippet (e.g. `import { IconChevronRight } from '@tabler/icons-react'` or the app's actual import pattern).
4. **Search/filter** input at the top.

If `tokens.json → icons` is absent or empty, write a short placeholder paragraph on `icons.html` instead of omitting the page (sidebar still links to it).

### Mock component CSS

`.mock-*` classes render static previews on component pages. Naming convention: `.mock-<component-slug>` for the base class, then `.mock-<slug>--<variant>` or `.mock-<slug>-<state>` for modifiers (e.g. `.mock-badge`, `.mock-badge-ok`, `.mock-badge-err`, `.mock-panel--dark`).

When writing `mock_html` in `components.json`, reference these classes directly: `"mock_html": "<span class=\"mock-badge mock-badge-ok\">UP</span>"`. Never use inline styles in `mock_html` — all visual properties belong in `styles.css` under the `.mock-*` section.

### Syntax highlighting (inline spans)

`.cmt` comments · `.kw` keywords · `.str` strings · `.num` numbers · `.tag` tags · `.attr` attributes.

### Action items page

PR-style task cards with: number, title, labels (inconsistency / tokens / component / easy / medium / hard), problem description, before/after mockups, code diff, files changed. `main.js` turns these into GitHub issue links if a repo URL is in CLAUDE.md.

---

## Phase 5 — Figma Plugin

Copy templates, populate from `tokens.json`, ship.

```bash
cp <path-to-this-skill>/templates/figma-plugin/manifest.json.template design-system/figma-plugin/manifest.json
cp <path-to-this-skill>/templates/figma-plugin/code.js.template       design-system/figma-plugin/code.js
```

Replace `{{PROJECT_NAME}}` and `{{UNIQUE_ID}}` in the manifest. In `code.js`, replace the `// {{POPULATE_FROM_…}}` markers with JS object literals derived from `tokens.json`.

### Font rules (learned from real bugs)

- Figma uses `"Semi Bold"` with a space. `"SemiBold"` crashes.
- `"DejaVu Sans Mono"` and `"Roboto Mono"` are **not** bundled. Use `"Courier New"` for monospace.
- `"Inter"` is the ultimate safe fallback — always bundled.
- Some families only ship `"Regular"` — requesting `"Medium"`/`"Bold"` throws. Always wrap `loadFontAsync` in try/catch.

The template already implements the three-level fallback (requested family+weight → requested family+Regular → Inter+weight → Inter+Regular).

### Manual QA before distributing

The Figma plugin cannot be tested headlessly. Before zipping, ask the user to run the plugin once manually in Figma and verify:

1. Plugin runs without crashing (no red error toast).
2. Variable collections appear: Brand, Spacing, Radius, Status Colors, Surface, Text.
3. Text styles appear with correct names (`heading/page`, `body/default`, `code/default`, etc.).
4. Status colors with a transparent border render as transparent (not black).
5. Check the Figma Plugin console for `console.log` output — the template logs each collection as it's created so you can see where it stopped if it crashed.

If the user cannot run the plugin, report the checklist and note it as unverified.

### Distributing

Zip `design-system/figma-plugin/` into `figma-plugin.zip` and commit. Users import via **Figma → Plugins → Development → Import plugin from manifest**.

---

## Phase 6 — Deploy & QA

### 6.1 Deploy to GitHub Pages

GitHub Pages is the required deployment target. Ask the user for:

1. **GitHub repo URL** — if not already in `CLAUDE.md`.
2. **Skill output path** — the subpath under the Pages site where the docs site
   will live (e.g. `skill-output/`). This is the path segment appended to the
   repo's Pages base URL. Default: `skill-output/`.

#### 6.1.0 Check for an existing Pages workflow first

**Before copying any files**, check whether a custom GitHub Actions workflow
already controls the deploy. The workflow may flatten, rename, or filter your
output path — the deployed URL is whatever the workflow publishes to, **not**
the literal repo path you wrote to.

```bash
ls .github/workflows/
gh api repos/<owner>/<repo>/pages 2>/dev/null | jq '.build_type, .source'
```

Interpret the result:

| `build_type` | What it means | Action |
|---|---|---|
| `legacy` | Pages serves a branch directly ("Deploy from branch") | Continue with the `cp -r` steps below |
| `workflow` | A custom workflow controls the deploy | **Read the matching `*pages*.yml` first.** Note where it copies files from (`skill-outputs/run*/...` is common) and what URL prefix Pages serves (`/skill-output/`, `/`, etc.). Adjust your `SKILL_OUTPUT_PATH` to match what the workflow expects |

If `gh` is unavailable, fall back to inspecting `ls .github/workflows/`. If a
file matching `*pages*.yml` exists, read it before you write anything — assume
the deployed URL will not match your filesystem layout.

#### 6.1.1 Copy and push

Once you know the workflow contract, copy the `design-system/` contents into
the repo at the path the workflow expects:

```bash
# From the project folder
REPO_ROOT=<path-to-git-repo>
SKILL_OUTPUT_PATH=<path-the-workflow-expects>   # confirmed from 6.1.0

# Copy docs site into repo at the correct subpath
cp -r design-system/. "$REPO_ROOT/$SKILL_OUTPUT_PATH/"

# Stage, commit, push
cd "$REPO_ROOT"
git add "$SKILL_OUTPUT_PATH/"
git commit -m "Deploy design system skill output from <run-id>"
git push
```

If GitHub Pages is not yet enabled on the repo, tell the user to enable it
at Settings → Pages → Source: Deploy from branch `main`, folder `/` (root) —
or, if a workflow exists, set Source to GitHub Actions.

#### 6.1.2 Confirm the deployed URL

Do **not** guess the URL from your filesystem layout. Confirm it from the
authoritative sources:

```bash
# After the deploy workflow finishes, the Pages API reports the live URL:
gh api repos/<owner>/<repo>/pages | jq -r '.html_url'

# Or watch the most recent deploy run for the published URL:
gh run list --workflow=pages.yml --limit 1
gh run view <run-id> --log | grep -E 'page_url|html_url'
```

Record this URL in `CLAUDE.md` under a `## Deployed skill output` entry:

```markdown
## Deployed skill output
- URL: <copy-paste from `gh api .../pages` — do NOT guess from filesystem layout>
- Run: <run-id>
- Deployed: <date>
```

### 6.2 Visual QA

Open the deployed site and verify:

- Light and dark mode on every page.
- Mobile responsive — burger menu works.
- All screenshots load in collapsible component references.
- Copy buttons work on every code block.
- No broken links (`../` vs direct).
- Component page section order matches the template.

If no browser is available, report the checklist to the user and ask them to
spot-check. Split automated vs manual checks:

**Automated (Claude Code can verify):** validator exits 0, all expected HTML
files exist, no bare `/components` hrefs, `<img>` tags have `onerror` handlers,
Figma plugin `manifest.json` is valid JSON.

**Manual (human browser required):** light/dark per page, burger menu, copy
buttons, no broken images, mobile layout.

### Create output zip

Once QA passes, zip the entire project folder — this includes the Cowork audit inputs and all Claude Code outputs:

```bash
cd <project-folder>/..
zip -r <app-hostname>-design-system-<YYYY-MM-DD>.zip <project-folder-name>/
```

**Naming format: `<app-hostname>-design-system-<YYYY-MM-DD>.zip`** — hostname + date keeps runs distinguishable. Examples: `prometheus.io-design-system-2026-04-23.zip`, `grafana.com-design-system-2026-05-01.zip`. Do not commit these zips — they're session artifacts, not source.

The zip contains:
- `audit-results.json`, `source-audit.json` (if run), `screenshots/` — from the audit phase
- `tokens.json`, `components.json` — extracted design data
- `design-system/` — the full static docs site + Figma plugin

---

## Quality Checklist

### Automated (Claude Code verifies)

- [ ] `audit-results.json` was the starting point — no values invented.
- [ ] All inconsistencies documented with resolution reasoning.
- [ ] Token values match the actual source (not approximated).
- [ ] `validate-handoff.py` exits 0.
- [ ] All expected HTML files exist in `design-system/`.
- [ ] No bare `/components` hrefs (either `.html` or `components/<slug>.html`).
- [ ] Navigation block is identical across all HTML files.
- [ ] Figma plugin `manifest.json` is valid JSON.
- [ ] `<img>` tags have `onerror` handlers where screenshots are referenced.
- [ ] `CLAUDE.md` progress checklist fully checked off.

### Manual (human browser required)

- [ ] All component pages follow the template section order.
- [ ] Light and dark mode render correctly on every page.
- [ ] Mobile responsive — burger menu works.
- [ ] Screenshots load in collapsible references.
- [ ] Figma plugin runs without crashing — font fallbacks tested.
- [ ] Copy buttons work on all code blocks.
- [ ] Docs site deployed to GitHub Pages and URL recorded in `CLAUDE.md`.

If no browser is available, run the Automated checks yourself and report the Manual checks to the user as a spot-check list — do not claim them passed.

---

## Reference Implementation Notes

The [Prometheus Design System](https://github.com/AndrejKiri/prometheus-design-system) is the reference implementation. It documents ~17 components extracted from the Prometheus monitoring UI plus 2 docs-site meta components, with a working Figma plugin and 11 screenshots.

**Known deviations from strict skill output** (the reference was hand-authored before this skill existed):

- Handoff JSON files (`audit-results.json`, `tokens.json`, `components.json`) are not committed. Regenerating via the skill requires authoring them first.
- Two components (`theme-toggle`, `nav-button`) are `origin: "docs-meta"` — parts of the docs site chrome, not extracted from Prometheus.
- CSS uses `--doc-brand-orange` rather than the generic `--doc-brand-primary` — a readability choice for a product whose brand color is orange.
- `migration.html` is included. Optional in the skill; include when the design system describes a migration path.
- `additional_screenshots` (interactive states like modals, expanded accordions) are not captured — the reference only has the 11 static page shots.

When generating from scratch via this skill, produce the JSON files first, tag docs-meta components explicitly, and decide brand-token naming up front.
