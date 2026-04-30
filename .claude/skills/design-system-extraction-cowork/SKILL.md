---
name: design-system-extraction-cowork
description: >
  Visual audit of a web application UI. Scopes the audit, authenticates,
  browses every page interactively, catalogs UI patterns, identifies
  inconsistencies, and writes audit-results.json + screenshots/ for handoff
  to Claude Code. Requires browser access (Computer Use / Chrome extension).
metadata:
  author: AndrejKiri
  version: '0.2'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
  paired-skill: design-system-extraction-code (docs/skill-code/SKILL.md)
---

# Design System Extraction — Claude Cowork Skill

**This skill produces the handoff package for the `design-system-extraction-code` Claude Code skill.**

Run Phases 0 and 1 in order, then stop and hand off.

---

## Core Principle

**Derive, not invent.** Every pattern and inconsistency must come from the actual application. Document what exists — do not fill in gaps from assumptions.

---

## Supporting Files

| File | Purpose |
|------|---------|
| [`schemas/audit-results.schema.json`](schemas/audit-results.schema.json) | Schema for `audit-results.json` output |
| [`scripts/validate-handoff.py`](scripts/validate-handoff.py) | Validator — run before handing off |

---

## Phase 0.0 — Pre-flight (browser ready check)

**Run this before anything else. Without a connected browser the skill cannot proceed past Phase 0.**

### 0.0.1 Detect the browser substrate

This skill supports two browser substrates. Check which is active and adopt that vocabulary for the rest of the run:

| Substrate | How you can tell | Tool prefix |
|---|---|---|
| Claude-in-Chrome MCP extension | `mcp__Claude_in_Chrome__*` tools available | `mcp__Claude_in_Chrome__` |
| Computer Use | `mcp__Claude_in_Chrome__*` tools absent; `computer` tool present | `computer` (mouse/keyboard primitives) |

If neither is available, stop and ask the user to enable one.

### 0.0.2 Verify the browser is connected

For Chrome MCP, call a cheap no-op like `mcp__Claude_in_Chrome__tabs_context_mcp` (or `read_page` on `about:blank`). If it errors with "extension not connected" or similar, show this message and block:

> I need the Claude-in-Chrome extension attached. Please open Chrome, click the extension icon, and confirm connection. Say "ready" when done.

Wait for the user before retrying. Do not proceed until the no-op call returns successfully.

### 0.0.3 Navigate away from chrome://newtab/ before any batch call

Chrome blocks extensions from scripting `chrome://` URLs (including the default new-tab page). The first `mcp__Claude_in_Chrome__browser_batch` will fail with "Can't interact with browser internal pages" if the active tab is still on `chrome://newtab/` or `chrome://...`.

**Always issue an explicit `navigate` to the target URL before the first `browser_batch` call.** When constructing a batch yourself, lead with the navigate as operation 0:

```js
mcp__Claude_in_Chrome__browser_batch({
  operations: [
    { type: "navigate", url: TARGET_URL },
    // ...rest of the batch
  ]
})
```

---

## Phase 0 — Scope & Auth

**Run after Phase 0.0 passes. Do not skip.**

### 0.1 Gather info

Ask the user:
1. URL of the application.
2. Project folder path — where all output files (`audit-results.json`, `screenshots/`, `CLAUDE.md`) will be written. If not provided, default to `~/audit/<app-hostname>` and confirm with the user before proceeding.
3. Authentication — credentials, SSO details, or API token.
4. Source code repo URL (optional — helps Claude Code extract exact token values).
5. GitHub repo URL (optional — used to generate GitHub issue links on action-item cards).

Test login immediately. If it fails, stop and ask for corrected credentials — do not proceed.

### 0.2 Discover routes

Crawl navigation links from the authenticated home page. List every discovered route.

### 0.3 Present scope options

| App size | Recommendation |
|---|---|
| < 15 pages | Audit everything. No scoping needed. |
| 15–30 pages | Recommend **core-plus-data**. Flag admin/system pages as optional. |
| 30+ pages | Strongly recommend a focused subset. Let the user choose. |

Present routes in categories (core UI / data views / admin-system / edge cases). **Wait for the user to confirm scope before proceeding.**

### 0.4 Check for pre-seeded data

Some pages look empty without sample data (dashboards, alert lists, metrics). Ask which pages might be empty — screenshot both populated and empty states where relevant.

### 0.4 Create project folder and CLAUDE.md

Create a `CLAUDE.md` in the shared project folder (the folder where all handoff files will live):

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
- [ ] Phase 1: Visual audit (tool: claude-cowork)
- [ ] Phase 1-Source: Source audit (tool: claude-code, optional)
- [ ] Phase 2: Token extraction
- [ ] Phase 3: Component extraction
- [ ] Phase 4: Documentation site
- [ ] Phase 5: Figma plugin
- [ ] Phase 6: Deploy + QA

## Handoff Files
- audit-results.json  — Phase 1 output
- source-audit.json   — Phase 1-Source output (optional, produced by Claude Code)
- tokens.json         — Phase 2 output
- components.json     — Phase 3 output
- screenshots/        — reference screenshots
```

---

## Phase 1 — Visual Audit

> **Screenshot capture is delegated to Phase 1.5 by default.** Cowork's sandbox cannot exfiltrate screenshot bytes (base64 is filtered; `save_to_disk` returns an opaque `ss_<hash>` ID with no filesystem path). **Phase 1 in Cowork produces 1×1 placeholder JPEGs and rich DOM observations.** Claude Code's Phase 1.5 backfills real screenshots locally via Playwright using the page list and `additional_screenshots[].state` keys you record here. Do not spend turns trying to export real images — that path is closed. See [KNOWN-LIMITATIONS.md](KNOWN-LIMITATIONS.md).

**Initialize placeholders before browsing.** Run this once at the start of Phase 1:

```bash
bash <path-to-this-skill>/scripts/init-placeholders.sh <project-folder>
```

This seeds `screenshots/` with the 1×1 placeholder file (`placeholder.jpg`) and creates the directory if missing. Set `"screenshots_are_placeholders": true` at the top level of `audit-results.json` and document the limitation in `raw_observations.screenshot_limitations`.

### 1.1 Browse every page in scope

Navigate to each URL in scope using the browser. For each page:

1. Navigate to the URL and wait for the page to fully load.
2. Copy the placeholder file to `screenshots/<page-name>.jpg` in the project folder. The real image is captured in Phase 1.5 — your job here is to record the path so Phase 1.5 knows where to write.
3. Scroll through the full page — do not miss content below the fold.
4. Expand accordions, click tabs, open dropdowns, hover interactive elements.
5. Record each notable interactive state as an entry in `additional_screenshots[]` with a controlled `state` key (see [Phase 1.4](#14-write-audit-resultsjson)) — Phase 1.5 will replay and capture.

Document for each page: URL, name, every visible UI element type, observed colors / font sizes / spacing / border radii / shadows.

### 1.2 Catalog every UI pattern

For each page, produce an inventory table:

| Pattern | Pages Found | Count | Variations |
|---------|------------|-------|-----------|
| ... | ... | ... | ... |

Be exhaustive within scope — scroll to the bottom, expand everything, miss nothing.

**Pattern naming convention** — use the same name every time a pattern appears across pages. Name drift (`"Mantine Card (same wrapper)"` on page A vs `"Card Title with Icon"` on page B for the same element) causes validator cross-reference errors.

Rules:
- Title Case, noun-phrase form (`Primary Button`, not `Primary Buttons` or `Button: Primary`)
- Parenthetical qualifiers for variants: `Filter Input (Pills)` vs `Filter Input (Single Field)`
- Framework-prefix only when it disambiguates: `Mantine Alert Info Callout` ✓, `Mantine Card` ✓
- Start from [`vocab/patterns-vocabulary.md`](vocab/patterns-vocabulary.md) — extend it, don't invent parallel vocabulary
- Lock in names after the **first page** — reuse them exactly on all subsequent pages

### 1.3 Identify inconsistencies

This is the primary deliverable. For each inconsistency:

1. What is inconsistent.
2. Table of variants across pages (what it looks like on each page).
3. Canonical choice — which variant is correct, with reasoning.
4. Concrete fix (code diff if source is available).

Look for: same concept implemented differently across pages, hardcoded values vs tokens, missing status normalization (`UP` vs `up` vs `active`), style drift, duplicated logic.

### 1.3b Encode interactive states for Phase 1.5

Cowork cannot reliably trigger and capture interactive states (modals, accordion expansions, hover). Instead of trying to screenshot these in Cowork, encode each desired state as a semantic key in `additional_screenshots[]` under the relevant page:

```json
"additional_screenshots": [
  { "path": "screenshots/targets-settings-modal.jpg", "state": "modal-open-settings" },
  { "path": "screenshots/targets-accordion-expanded.jpg", "state": "expanded-accordion" },
  { "path": "screenshots/home-dark.jpg", "state": "dark-theme" }
]
```

Claude Code's `capture-interactive.mjs` reads these keys, looks them up in `interaction-recipes.json`, executes the action sequence in Playwright, and saves the screenshot. State keys must use the controlled vocabulary defined in [Phase 1.4](#14-write-audit-resultsjson).

### 1.3c Wait for stable DOM before observing

A `setTimeout(600)` is not sufficient — data-heavy pages (accordion targets, tables) may still be populating after 600ms. Use a concrete signal instead:

```js
(async () => {
  await window.__waitForStable([
    '[class*="Accordion-root"]',
    'table tbody tr',
    '[class*="DataTable"]'
  ]);
  // now safe to read computed styles
})()
```

Inject `__waitForStable` early in the session via `javascript_tool`:

```js
window.__waitForStable = async (selectors, quietMs = 500, timeoutMs = 8000) => {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const found = selectors.some(s => document.querySelector(s));
    if (found) {
      // wait for DOM to go quiet
      await new Promise(resolve => {
        let timer;
        const mo = new MutationObserver(() => {
          clearTimeout(timer);
          timer = setTimeout(() => { mo.disconnect(); resolve(); }, quietMs);
        });
        mo.observe(document.body, { childList: true, subtree: true });
        timer = setTimeout(() => { mo.disconnect(); resolve(); }, quietMs);
      });
      return;
    }
    await new Promise(r => setTimeout(r, 100));
  }
};
```

Also available as `scripts/browser-helpers.js` — inject the whole file contents at the start of a page survey session.

### 1.4 Write audit-results.json

Write `audit-results.json` in the project folder, conforming to [`schemas/audit-results.schema.json`](schemas/audit-results.schema.json).

Required fields: `app_url`, `audit_date`, `tool` (`"claude-cowork"`), `scope`, `pages_audited`, `patterns`, `inconsistencies`, `raw_observations`.

**Inconsistency IDs:** Use format `INC-NNN` with zero-padded 3-digit sequence (`INC-001`, `INC-002`, …). Order severe → minor. Reserve `INC-900+` for deferred/won't-fix. Claude Code cross-references these IDs in tokens.json and components.json.

**`audit_date`:** Use ISO 8601 format `YYYY-MM-DD` (e.g. `"2026-04-21"`). The validator enforces this.

**`additional_screenshots[].state`:** Use the controlled vocabulary from [`vocab/state-vocabulary.md`](vocab/state-vocabulary.md):
- `light-theme`, `dark-theme`
- `modal-open-<name>` (e.g. `modal-open-settings`)
- `tab-<name>` (e.g. `tab-graph`)
- `hover-<selector>` (e.g. `hover-target-row`)
- `expanded-<group>` (e.g. `expanded-node_exporter`)
- `error-<code>` (e.g. `error-503`)
- `empty-state`, `loading-state`

**Validate before handing off:**

```bash
python <path-to-this-skill>/scripts/validate-handoff.py <project-folder>
```

Fix every `[FAIL]` before proceeding. Warnings are acceptable.

---

## Gotchas

### Workspace delete permissions

The Cowork workspace folder (`/sessions/<session-id>/mnt/Claude/`) is delete-protected by default. Any `rm` call or attempt to overwrite files there will fail with `Operation not permitted`.

**Before any cleanup step that involves `rm` or overwriting files in the workspace, call `allow_cowork_file_delete` once per target directory:**

```
mcp__cowork__allow_cowork_file_delete(path="/sessions/<session-id>/mnt/Claude/")
```

### Packaging the handoff zip

The `zip` CLI cannot overwrite a pre-existing file it considers a corrupt archive (e.g. a 0-byte file created by a failed earlier run). Use Python's `zipfile` module instead — it handles pre-existing files gracefully:

```python
import zipfile, os, sys
src = sys.argv[1]; out = sys.argv[2]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(src):
        for f in files:
            full = os.path.join(root, f)
            arc = os.path.relpath(full, os.path.dirname(src))
            z.write(full, arc)
```

Run as: `python3 -c "..." <project-folder> <output.zip>`

### `await` at top level in javascript_tool

`javascript_tool` evaluates scripts as classic (non-module) expressions. Top-level `await` throws `SyntaxError`. Wrap every async block in an IIFE:

```js
(async () => {
  const result = await fetch('/api/data').then(r => r.json());
  return result;
})()
```

Pre-seed this helper early in the session:

```js
window.__runAsync = fn => (async () => fn())();
```

Then use: `window.__runAsync(async () => { ... })`

### Runtime.evaluate timeout on large return values

Chrome DevTools Protocol times out (~45s) on return payloads exceeding a few KB. Cap per-call returns to ~2KB. For anything larger:
- Spit data to `window.__audit_buffer` and read in chunks
- Or delegate to Claude Code's Playwright script

Never attempt to return screenshot data (base64) from `javascript_tool` — the payload is too large and also filtered by the sandbox.

### Brave browser blocks the Claude extension

Brave Shields blocks WebSocket connections on `claude.ai`. If the Chrome MCP extension fails to connect or the first screenshot hangs >10s, Brave is the likely cause.

**Fix:** Either disable Brave Shields on `claude.ai` (per-site), or use standard Chrome.

Add an environment check at the start of Phase 0: ask the user which browser they're using, and if Brave, prompt them to switch or disable Shields before proceeding.

### Theme toggle — ARIA text describes the action, not the state

Mantine's theme-toggle ActionIcon label reads "Switch to light theme" or "Switch to dark theme" — i.e., what the click *will do*, not the current state. Clicking once does not reliably set a known theme because Mantine supports `auto | light | dark`.

**Always set theme directly via JS instead of clicking the button:**

```js
document.documentElement.setAttribute('data-mantine-color-scheme', 'dark');
localStorage.setItem('mantine-color-scheme-value', 'dark');
```

Verify by checking: `getComputedStyle(document.body).backgroundColor`

Cache the reference background colors for light (`rgb(255,255,255)` or similar) and dark early in the session — use these as ground-truth for which theme is active.

---

## Phase 1.5 — Screenshot Capture (Claude Code, local)

**This phase runs in Claude Code after receiving the handoff zip — before Phase 2.**

Cowork cannot reliably export screenshots. Claude Code runs locally with Playwright and a real filesystem. If `audit-results.json` contains `"screenshots_are_placeholders": true`, or any screenshot file is ≤ 500 bytes, run:

```bash
node .claude/skills/design-system-extraction-cowork/scripts/capture-screenshots.mjs <project-folder>
```

The script reads `pages_audited[].screenshot` and `pages_audited[].additional_screenshots[].path` from `audit-results.json` and writes real JPEGs to `screenshots/`. Viewport: 1280×800. Both light and dark themes if `has_dark_mode` is true.

**One-time setup:** `npm install playwright` then `npx playwright install chromium`

For interactive states (modals, expanded accordions, hover):

```bash
node .claude/skills/design-system-extraction-cowork/scripts/capture-interactive.mjs <project-folder>
```

Reads `interaction-recipes.json` (in the project folder) for `state → action` mappings. A template `interaction-recipes.json` is in `scripts/`.

After capture, re-run the validator:

```bash
python3 "$(pwd)/.claude/skills/design-system-extraction-cowork/scripts/validate-handoff.py" <project-folder>
```

---

## Degraded Screenshot Mode (now the default)

Phase 1 in Cowork operates in placeholder mode end-to-end. The steps are baked into Phase 1.1 above; this section is reference for what happens under the hood:

1. `scripts/init-placeholders.sh <project-folder>` seeds 1×1 placeholders.
2. Each page's `screenshot` path and every `additional_screenshots[].path` references the placeholder.
3. `"screenshots_are_placeholders": true` is set at the top of `audit-results.json`.
4. `raw_observations.screenshot_limitations` documents that Cowork cannot export bytes.
5. The validator prints `[WARN]` not `[FAIL]` for placeholder files when the flag is true.
6. Claude Code's [Phase 1.5](#phase-15--screenshot-capture-claude-code-local) backfills real JPEGs via Playwright and flips the flag to `false`.

---

## Handoff

**Stop here.** Do not proceed to token extraction or docs site — that is Claude Code's job.

Before handing off, confirm:
- [ ] `audit-results.json` exists in the project folder
- [ ] `validate-handoff.py` exits 0 (or exits 1 with only warnings)
- [ ] `screenshots/` directory exists with one file per audited page
- [ ] `CLAUDE.md` progress shows Phase 0 and Phase 1 checked off

### Create handoff zip

```bash
cd <project-folder>/..
zip -r <app-hostname>-audit.zip <project-folder-name>/
```

Name the zip after the app hostname (e.g. `prometheus.io-audit.zip`). This zip is the handoff package for Claude Code.

Then tell the user:

> **Audit complete.** The handoff zip `<app-hostname>-audit.zip` is ready. Pass it to Claude Code with the `design-system-extraction-code` skill — point it at the zip or the extracted folder and it will pick up from Phase 2 automatically.
>
> If you also have the source repo, provide it to Claude Code — it can run a source audit (Phase 1-Source) to get exact token values before extracting.
