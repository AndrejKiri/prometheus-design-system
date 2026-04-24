# Design System Project

## Target Application
- URL: https://prometheus-e83j.onrender.com
- Source repo: https://github.com/prometheus/prometheus (user-confirmed; used by Claude Code in Phase 1-Source)
- Auth: None (public demo)

## Scope
- Tier: TBD (set after Phase 0 route discovery)
- Pages audited: TBD
- Themes: light + dark (Prometheus UI supports both)

## Progress
- [x] Phase 0: Scope assessment
- [x] Phase 1: Visual audit (tool: claude-cowork)
- [ ] Phase 1-Source: Source audit (skipped — raw_observations already rich)
- [x] Phase 2: Token extraction
- [x] Phase 3: Component extraction
- [x] Phase 4: Documentation site
- [x] Phase 5: Figma plugin
- [x] Phase 6: Deploy + QA (automated checks; deployment pending user confirmation)

## Handoff Files
- audit-results.json   — Phase 1 output (this session)
- screenshots/         — one JPEG per page × theme (placeholder-sized — sandbox blocked export)
- observations/        — raw per-page DOM/CSS notes captured during live inspection
- source-audit.json    — Phase 1-Source output (skipped this run)
- tokens.json          — Phase 2 output
- components.json      — Phase 3 output (31 components, 18 action items)
- gen.py               — Phase 4 generator (regenerate site with `python3 gen.py`)
- design-system/       — Phase 4 generated docs site
- design-system/figma-plugin/ — Phase 5 Figma bootstrap plugin
- design-system/figma-plugin.zip — distributable plugin archive

## Deployed skill output
- URL: https://andrejkiri.github.io/prometheus-design-system/skill-output/
- Run: run2
- Deployed: 2026-04-24

The `.github/workflows/pages.yml` workflow copies the latest `skill-outputs/run*/`
directory's `design-system/` into `/skill-output/` on every push to `skill-outputs/**`.
Do NOT link to the nested `skill-outputs/run2/...` path — the site is only served
at the flat `/skill-output/` URL.

## QA — automated (passed)
- validate-handoff.py: PASS, 24 checks, 0 warnings, 0 errors
- All 11 top-level + 31 component HTML files generated
- No bare `/components` hrefs anywhere
- 31/31 component pages emit `<img onerror="…">` handlers for screenshots
- figma-plugin/manifest.json is valid JSON
- code.js parses as valid JavaScript

## QA — manual (not yet verified)
- [ ] Light + dark theme on every page
- [ ] Mobile responsive — burger menu works
- [ ] Component reference screenshots load (currently placeholders)
- [ ] Figma plugin runs in Figma without crashing — font fallbacks tested
