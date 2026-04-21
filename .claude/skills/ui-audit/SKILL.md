---
name: ui-audit
description: >
  Visual audit of a web application UI. Scopes the audit, authenticates,
  browses every page interactively, catalogs UI patterns, identifies
  inconsistencies, and writes audit-results.json + screenshots/ for handoff
  to Claude Code. Requires browser access (Computer Use / Chrome extension).
metadata:
  author: AndrejKiri
  version: '0.1'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
  paired-skill: extract-design-system (docs/skill-code/SKILL.md)
---

# UI Audit — Claude Cowork Skill

**This skill produces the handoff package for the `extract-design-system` Claude Code skill.**

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

## Phase 0 — Scope & Auth

**Must run first. Do not skip.**

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

### 1.1 Browse every page in scope

Navigate to each URL in scope using the browser. For each page:

1. Navigate to the URL and wait for the page to fully load.
2. Take a full-page screenshot. Save to `screenshots/<page-name>.jpg` in the project folder.
3. Scroll through the full page — do not miss content below the fold.
4. Expand accordions, click tabs, open dropdowns, hover interactive elements.
5. Screenshot each notable interactive state (expanded accordion, open dropdown, hover button, filled form, error state).

Document for each page: URL, name, every visible UI element type, observed colors / font sizes / spacing / border radii / shadows.

### 1.2 Catalog every UI pattern

For each page, produce an inventory table:

| Pattern | Pages Found | Count | Variations |
|---------|------------|-------|-----------|
| ... | ... | ... | ... |

Be exhaustive within scope — scroll to the bottom, expand everything, miss nothing.

### 1.3 Identify inconsistencies

This is the primary deliverable. For each inconsistency:

1. What is inconsistent.
2. Table of variants across pages (what it looks like on each page).
3. Canonical choice — which variant is correct, with reasoning.
4. Concrete fix (code diff if source is available).

Look for: same concept implemented differently across pages, hardcoded values vs tokens, missing status normalization (`UP` vs `up` vs `active`), style drift, duplicated logic.

### 1.4 Write audit-results.json

Write `audit-results.json` in the project folder, conforming to [`schemas/audit-results.schema.json`](schemas/audit-results.schema.json).

Required fields: `app_url`, `audit_date`, `tool` (`"claude-cowork"`), `scope`, `pages_audited`, `patterns`, `inconsistencies`, `raw_observations`.

Every inconsistency needs a unique `id` (`INC-001`, `INC-002`, …) — Claude Code cross-references these IDs in tokens.json and components.json.

**Validate before handing off:**

```bash
python <path-to-this-skill>/scripts/validate-handoff.py <project-folder>
```

Fix every `[FAIL]` before proceeding. Warnings are acceptable.

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

> **Audit complete.** The handoff zip `<app-hostname>-audit.zip` is ready. Pass it to Claude Code with the `extract-design-system` skill — point it at the zip or the extracted folder and it will pick up from Phase 2 automatically.
>
> If you also have the source repo, provide it to Claude Code — it can run a source audit (Phase 1-Source) to get exact token values before extracting.
