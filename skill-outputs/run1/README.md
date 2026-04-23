# run1 — Prometheus UI audit, 2026-04-21

First end-to-end run of the design-system extraction skills against the Prometheus web UI demo at https://prometheus-e83j.onrender.com.

Both skills ran to completion (validator exit 0, 25/25 PASS). Screenshots in the output are 1×1 placeholder JPEGs — the Cowork sandbox blocked pixel export. See `run1-output-combined/CLAUDE.md` for details.

---

## Artifacts

### Skill outputs

| File | Description |
|------|-------------|
| [`run1-output-cowork.zip`](run1-output-cowork.zip) | Raw zip handed off by the Cowork skill (design-system-extraction-cowork). Contains the audit package: `audit-results.json`, `observations/`, `screenshots/` (placeholders), and `CLAUDE.md`. |
| [`run1-output-code.zip`](run1-output-code.zip) | Raw zip produced by the Claude Code skill (design-system-extraction-code). Contains the full design system artifact tree: `tokens.json`, `components.json`, and the `design-system/` static site. |
| [`run1-output-combined/`](run1-output-combined/) | Unpacked and merged tree from both zips. This is the canonical browseable output for this run. See below for its structure. |

### Feedback documents

| File | Description |
|------|-------------|
| [`run1-feedback-skill-ui-audit.md`](run1-feedback-skill-ui-audit.md) | Post-run analysis of the ui-audit (Cowork) skill. 16 friction points documented — screenshot export failure, delete permissions, naming drift, async JS limitations, and more — each with a root-cause analysis and a concrete fix tagged by target (`[skill]`, `[validator]`, `[cowork]`, `[handoff-to-cc]`). |
| [`run1-feedback-skill-design-system.md`](run1-feedback-skill-design-system.md) | Post-run analysis of the extract-design-system (Claude Code) skill. Schema ambiguities, validator edge cases, and gen.py/Figma issues, all with proposed fixes. |
| [`run1-feedback-baseline-vs-output-comparison.md`](run1-feedback-baseline-vs-output-comparison.md) | Side-by-side comparison of the skill-output documentation site against the hand-authored reference design system site. Covers visual structure, token coverage, component depth, and framing differences. |

### Visual diff

| File | Description |
|------|-------------|
| [`run1-side-by-side-comparison.html`](run1-side-by-side-comparison.html) | Standalone HTML page that embeds both the reference design system and the skill-output site in iframes for pixel-accurate visual diffing. Open in a browser — no server required. |

---

## run1-output-combined/ structure

```
run1-output-combined/
├── CLAUDE.md                  Project context, progress checklist, and screenshot limitation note
├── audit-results.json         Phase 1 output — structured audit findings for all 10 pages × 2 themes
├── tokens.json                Phase 2 output — design token definitions (colors, typography, spacing, etc.)
├── components.json            Phase 3 output — component catalog with props, variants, and pattern references
├── design-system/             Static HTML documentation site (open index.html locally or via `npx serve`)
│   ├── index.html             Home page
│   ├── tokens.html            Design token reference
│   ├── icons.html             Tabler icon inventory
│   ├── components.html        Component overview grid
│   ├── components/<slug>.html Individual component pages (18 components)
│   ├── patterns.html          Recurring layout and interaction patterns
│   ├── action-items.html      Concrete improvement tasks in PR-card format
│   ├── inconsistencies.html   INC-001 through INC-009 — design inconsistencies found and resolved
│   ├── audit-report.html      Full audit findings
│   ├── figma.html             Figma library setup guide
│   ├── changelog.html         Version history
│   ├── figma-plugin/          Figma plugin source (code.js + manifest.json)
│   ├── styles.css             Global stylesheet
│   ├── main.js                Theme toggle, copy buttons, navigation
│   └── gen.py                 Python script used to regenerate HTML pages from JSON data
├── observations/              Raw per-page DOM/CSS notes captured during live browser inspection
│   ├── <page>-light.json      Light-theme observations for each of the 10 audited pages
│   └── dark-observations.json Dark-theme observations (combined)
└── screenshots/               Page screenshots — 1×1 placeholder JPEGs (real capture blocked by Cowork sandbox)
    └── <page>-<theme>.jpg     One file per page × theme (20 total)
```

---

## Known limitations

- **Screenshots are placeholders.** All 20 `screenshots/*.jpg` files are 196-byte 1×1 JPEGs. The Cowork sandbox's safety filter blocks binary data export from the browser automation channel. Re-capture with a local Playwright script against the audit URLs in `audit-results.json` if real pixels are needed.
- **Phase 1-Source not run.** The optional source-audit step (cross-referencing visual patterns to React component source in the Prometheus repo) was not executed for this run. `source-audit.json` does not exist.
