# design-system-extraction-cowork skill — problems encountered & proposed fixes

The skill ran to completion against https://prometheus-e83j.onrender.com. The visual audit covered 10 pages (both themes), cataloged 31 UI patterns and 9 inconsistencies, and produced a validator-PASS `audit-results.json` (9 PASS / 4 benign WARN / 0 errors) plus a handoff zip ready for Claude Code. This document enumerates every friction point hit along the way — with each fix tagged by who should implement it:

- **[skill]** — change the design-system-extraction-cowork skill itself (SKILL.md, scripts, vocabulary files)
- **[validator]** — change `scripts/validate-handoff.py`
- **[cowork]** — change Cowork's sandbox plumbing (out of scope for a skill fix; noted so Claude Code knows what not to try to solve)
- **[handoff-to-cc]** — document a Phase 1.5 that Claude Code runs locally after Cowork hands off

---

## 1. Screenshot binary export is blocked in the Cowork sandbox — CRITICAL

**What happened.** The skill's core artefact is supposed to be real screenshots, one per page × theme. In Cowork, the Chrome MCP extension exposes `save_to_disk` for screenshots, but it returns opaque `ss_<hash>` IDs, not image bytes. Base64 payloads returned from the browser's `javascript_tool` calls (e.g. `canvas.toDataURL()` round-trips) are filtered out of the response before reaching the model. The net effect: there is no path inside Cowork to land a JPEG on the user's disk. I switched the run to "Degraded Screenshot Mode": capture rich DOM observations, emit 1×1 placeholder JPEGs at every screenshot path referenced in `audit-results.json`, and set `screenshots_are_placeholders: true` so Claude Code can backfill in Phase 1.5.

**Root cause.** The Cowork sandbox, by design, does not let arbitrary browser-side code exfiltrate binary data to disk. The Chrome MCP `save_to_disk` output is an opaque reference that the model cannot convert into bytes. There is no sandboxed path to Playwright/Puppeteer running headless on the user's machine.

**Fix.**

- **[skill]** Promote Degraded Screenshot Mode from a fallback to the documented default when running under Cowork. Make it unambiguous in SKILL.md that Phase 1 in Cowork produces placeholder JPEGs and that real screenshots are backfilled by Claude Code Phase 1.5.
- **[skill]** Ship `scripts/init-placeholders.sh` (already present — keep it) and reference it from the SKILL.md checklist so agents don't have to rediscover it.
- **[handoff-to-cc]** Document Phase 1.5 in the code-side skill: a small Playwright/Puppeteer harness that reads `audit-results.json`, navigates to each page (honoring the theme via `data-mantine-color-scheme` / localStorage or equivalent), waits for network idle, and writes real JPEGs at the paths listed under `pages_audited[].screenshot` and `pages_audited[].additional_screenshots[].path`. After the backfill it should flip `screenshots_are_placeholders` to `false`.
- **[cowork]** (noted, not a skill fix) If Cowork later exposes a "save browser screenshot to workspace file" primitive, the skill can drop Degraded Mode.

---

## 2. Chrome extension must be connected before the skill starts — HIGH

**What happened.** The first `mcp__Claude_in_Chrome__javascript_tool` call failed because the extension wasn't attached. I had to stop, prompt the user ("please open Chrome"), wait, and retry. This is a hard floor — with no browser, the skill can't proceed past Phase 0.

**Root cause.** The skill's SKILL.md mentions Chrome as a requirement but doesn't do a pre-flight check. There's no "connect Chrome first" gate before the first navigation attempt.

**Fix.**

- **[skill]** Add a Phase 0.0 pre-flight: call a cheap no-op like `tabs_context_mcp` or `read_page` on about:blank. If it errors, show a clear message ("I need the Claude-in-Chrome extension attached. Please open Chrome, click the extension icon, and confirm connection. Say 'ready' when done.") and block on user confirmation before continuing.
- **[skill]** Detect at the start whether Computer Use or Chrome MCP is the active browser substrate and branch appropriately in the SKILL.md wording. Right now the skill uses both vocabularies interchangeably.

---

## 3. `browser_batch` fails on chrome://newtab/ — HIGH

**What happened.** The first attempt to use `mcp__Claude_in_Chrome__browser_batch` returned "Can't interact with browser internal pages." The tool can't operate on any `chrome://` URL, including the default new-tab page that a fresh browser opens on.

**Root cause.** Chrome blocks extensions from scripting internal pages. The skill didn't account for the starting state.

**Fix.**

- **[skill]** Always issue an explicit `navigate` to the target URL before the first `browser_batch` call. Add this to the SKILL.md Phase 0 checklist as a numbered step ("0. Navigate away from chrome://newtab/ to the target URL").
- **[skill]** In the browser-helper examples, model every batch-first interaction with an `operations: [{type:"navigate", url: TARGET}, ...rest]` opener.

---

## 4. SPA navigation nukes the injected `__observe()` helper — HIGH

**What happened.** I injected a small `window.__observe()` helper to capture DOM+CSS snapshots. On a classic website this survives, but Prometheus is a Mantine React SPA — internal navigation keeps the page alive but the skill's `navigate` call to a new route triggers a full document replace, wiping the window state. Subsequent `__observe()` calls threw ReferenceError. I worked around it by re-injecting the observer inline with every call.

**Root cause.** The skill's helper lifecycle assumes page-load injection is durable. It isn't, under the `navigate` tool in Chrome MCP which does a full doc reload, or across any cross-route navigation in any SPA.

**Fix.**

- **[skill]** Move `browser-helpers.js` from "inject once, call many" to a self-contained IIFE that every `javascript_tool` call ships inline. The helper file already exists in `scripts/` — change the calling pattern in SKILL.md examples to always `cat` the helper and append the specific observation call.
- **[skill]** Document the Mantine/React/Vue/SPA case explicitly with a note: "Assume every `navigate` wipes window state. Re-inject helpers in each tool call."

---

## 5. Status dropdown wouldn't open via `.click()` — MEDIUM

**What happened.** The 10 route discovery hinges on opening the Status dropdown in the header. Calling `.click()` on the `<button>` from `javascript_tool` didn't pop the Mantine Menu; its event listener expects a synthetic pointer event. I had to fall back to a real `computer` mouse click at `[535, 28]`.

**Root cause.** Mantine's Menu component uses a floating-UI-style trigger that discriminates between programmatic and real pointer events. This is a broader class of React-widget gotcha.

**Fix.**

- **[skill]** Add a "When `.click()` doesn't fire" recipe to `scripts/interaction-recipes.json`: try in order — `.click()` → `dispatchEvent(new PointerEvent('click', {bubbles:true, ...}))` → real `computer` click. Document the escalation ladder in SKILL.md.
- **[skill]** Include a short selector-resolution helper that returns element bounding-box center coordinates — useful for the real-click fallback (no more manual coordinate guessing).

---

## 6. `allow_cowork_file_delete` parameter shape mismatch — MEDIUM

**What happened.** When the user said "Redo from scratch" I tried to delete the prior audit via `allow_cowork_file_delete`. First attempt used `path` (schema error), second used `file_path` with the Desktop path (mount error). I ended up doing a bash `mv` to rename the prior folder aside.

**Root cause.** The tool's parameter shape isn't documented in the skill, and the path-vs-mount translation (`/Users/.../Desktop/Claude` ↔ `/sessions/.../mnt/Claude`) isn't called out for destructive tools.

**Fix.**

- **[skill]** Document the "redo from scratch" path as: `mv <project-folder> <project-folder>-backup-<ISO-date>` via `mcp__workspace__bash`. This is the most reliable approach and works identically whether the file-delete MCP is available or not.
- **[skill]** Add an exact "delete the prior run" recipe to SKILL.md so future agents don't re-derive it.

---

## 7. Inconsistency vocabulary is too loose — MEDIUM

**What happened.** I catalogued 9 inconsistencies (INC-001 through INC-009) and had to pick `type` and `severity` values largely by feel. The skill's vocabulary of `implementation-drift / hardcoded-values / missing-normalization / style-drift / duplicated-logic` is useful but narrow — several of my findings straddled two buckets (e.g. duplicate empty-state copy is both `duplicated-logic` and a content-pattern issue; the hljs semantic color inversion is `style-drift` but also "theming-bug"). The validator accepts anything, so there's no feedback loop.

**Root cause.** The vocabulary file exists but isn't exhaustive enough for real-world findings, and the validator doesn't enforce it.

**Fix.**

- **[skill]** Expand `inconsistency-types.json` to include at least: `content-pattern-duplication`, `theming-bug`, `a11y-contrast`, `responsive-drift`, `semantic-color-mismatch`, `naming-inconsistency`. Include a one-line description of each.
- **[validator]** Validate `inconsistencies[].type` against the vocabulary and emit a WARN (not FAIL) if unknown. Also validate `severity` is one of a closed set (`critical | high | medium | low`).
- **[skill]** Provide ~10 worked-example inconsistency entries in `examples/inconsistencies.json` so agents have a concrete template to pattern-match against.

---

## 8. `audit-results.schema.json` is permissive; easy to emit valid-but-thin data — MEDIUM

**What happened.** The validator passed my file with only 9 PASS checks and 0 FAIL, even though it doesn't verify that `raw_observations.colors_observed` has the expected depth, nor that dark-theme observations exist when `has_dark_mode: true`, nor that at least one inconsistency variant cites two or more pages. A thin file could pass.

**Root cause.** The validator's scope is shape + file existence, not content depth.

**Fix.**

- **[validator]** Add content-depth checks as WARN-level: (a) if `has_dark_mode: true`, require at least one element in `raw_observations.dark_observations` (or similar); (b) require at least N colors_observed entries for a "full" tier audit (N≈10); (c) for each inconsistency with `pages` length < 2, emit a WARN — cross-page inconsistencies are the point.
- **[validator]** Warn if any pattern has `instance_count: 1` and `variation_count: 0` — it's probably not a pattern, it's a single component.
- **[skill]** Add a self-check prompt to the Phase 1 wrapup: "before writing audit-results.json, verify every inconsistency references at least 2 pages, and every pattern appears on at least 2 pages or is a framework primitive."

---

## 9. Theme-toggle approach is per-app and undocumented — MEDIUM

**What happened.** To capture dark-mode deltas I had to reverse-engineer Prometheus's theme mechanism — it uses `data-mantine-color-scheme` on `<html>` and `mantine-color-scheme-value` in localStorage. Every tech-stack will differ (Tailwind `class="dark"`, next-themes, CSS-variables via a `data-theme` attribute, MUI ColorScheme, Radix, etc.). The skill has no playbook for this.

**Root cause.** Theme detection is stack-specific, but the skill treats it as one-liner.

**Fix.**

- **[skill]** Ship `scripts/detect-theme-toggle.js` — a small browser-side probe that tries the common patterns in order (data-theme attr, class="dark" on html/body, localStorage keys matching `theme|color-scheme|mantine`, system-prefers-color-scheme media query) and reports which one is live. Call it from Phase 0 and store the result in the project's `CLAUDE.md` under a `## Theme toggle` section so every subsequent step knows how to toggle.
- **[skill]** Document the five most common theme mechanisms with a one-line "how to flip it" recipe each.

---

## 10. Path translation between file tools and bash is a constant foot-gun — LOW

**What happened.** Throughout the session I had to translate between the file-tool path (`/Users/.../Desktop/Claude/prometheus-audit/...`) and the bash mount path (`/sessions/kind-admiring-ride/mnt/Claude/prometheus-audit/...`). Every bash call needed the mount path, every Read/Write/Edit needed the user-visible path. I got it wrong once (the `allow_cowork_file_delete` issue in #6 above was partially a path-translation bug).

**Root cause.** The two toolchains address the same bytes through different roots and the SKILL.md doesn't tabulate the mapping.

**Fix.**

- **[skill]** Add a one-paragraph "Path translation cheat sheet" to SKILL.md with the exact mapping for Desktop/Claude, outputs, skills, uploads. Repeat it near every bash example.
- **[skill]** Prefer file tools (Read/Write/Edit) in SKILL.md examples where possible; reach for bash only when we need shell semantics (mkdir, mv, zip, python).

---

## 11. "Deployed skill output" URL handoff isn't plumbed in Cowork — LOW

**What happened.** The wrapup skill (this one) Phase 2/3 wants a `## Deployed skill output` URL from `CLAUDE.md`. That URL comes from Claude Code Phase 6. In a Cowork-only run that precedes Claude Code, the entry is missing, so the wrapup silently skips the most user-facing artefacts (reference-comparison doc, side-by-side HTML tool).

**Root cause.** The two skills chain in order, but the wrapup skill is being asked to run before its prerequisites are met.

**Fix.**

- **[skill]** In the wrapup SKILL.md, Phase 0 "context gather" step: when the skill-output URL is absent, state that clearly in the produced feedback MD with a "TODO: re-run wrapup Phases 2 & 3 after Claude Code deploys the docs site" line, instead of just silently skipping.
- **[skill]** Make the cowork skill's final message include a handoff reminder: "After Claude Code Phase 6 deploys the docs site and writes `## Deployed skill output` into CLAUDE.md, come back and run the wrapup skill to generate the reference-vs-output comparison."

---

## Things Claude Code can do that Cowork cannot

1. **Real screenshot capture via Playwright.** Cowork can't exfiltrate browser binaries. Claude Code runs a local Playwright harness that reads `audit-results.json`, navigates to each URL at each theme, waits for network idle, and writes real JPEGs to `screenshots/`, then flips `screenshots_are_placeholders` to `false`.
2. **Source-code cross-reference via `git clone` + file search.** Cowork has no git. Claude Code clones the source repo listed in `CLAUDE.md`, greps for component names and CSS variables, and produces `source-audit.json` linking DOM-observed patterns to their source definitions (e.g. "this Badge uses Mantine's `Badge.Root` with `variant='light'`").
3. **Build-time design-token extraction.** From the source tree, Claude Code can read `theme.ts`, Tailwind `theme.extend`, CSS custom-property declarations, or SCSS variable files and emit `tokens.json` with canonical values — not just the DOM-computed values Cowork samples.
4. **Accessibility audit via axe-core.** Cowork can load axe into a page but can't readily run it across the full site and aggregate results. Claude Code runs pa11y or axe-cli in CI-style against the full URL list.
5. **Responsive capture at multiple viewport widths.** Claude Code's Playwright can drive the browser at 320 / 768 / 1024 / 1440 / 1920 and capture at each, producing a responsive matrix. Cowork can resize the window but can't reliably write a matrix of files.
6. **Motion/animation probing.** Playwright's video recording and CDP tracing can capture transition timings; Cowork can read `getComputedStyle` for `transition-duration` but can't record motion.
7. **Privileged font-family fingerprinting.** Claude Code can read the shipped font files from the built site and assert what the user actually sees; Cowork is limited to whatever `font-family` the CSS declares.

## Things neither Cowork nor Claude Code can do

Don't let the skill promise these.

1. **Real-user accessibility audit.** Automated tools (axe, pa11y, Lighthouse) catch ~40% of WCAG issues. Nobody on this chain is a replacement for a human screen-reader pass.
2. **Cross-OS font-fallback rendering verification.** What a Mac sees when the CSS says `font-family: -apple-system, BlinkMacSystemFont, ...` differs from what a Windows machine sees. Neither agent runs multiple OSes.
3. **Real Core Web Vitals under realistic network conditions.** Lighthouse-in-CI approximates; it doesn't replicate the user's true device/network. And our Onrender free-tier cold-starts skew any number we do get.
4. **Licensed brand / typeface / imagery verification.** We don't verify that a customer paid for the Inter font or has rights to the image assets.
5. **Security-scoped testing.** CSRF, XSS, authZ boundaries. Out of scope for a visual design audit.
6. **Intent inference.** We can flag that two empty-state Alerts have identical copy; we can't decide whether that was deliberate pattern reuse or a copy-paste bug. That requires a human product owner.

## Suggested SKILL.md structure after fixes

```
design-system-extraction-cowork/
├── SKILL.md
├── vocabulary/
│   ├── pattern-names.json
│   ├── state-names.json
│   ├── inconsistency-types.json        # expanded per #7
│   └── severity-levels.json            # new per #7 (closed set)
├── scripts/
│   ├── init-placeholders.sh
│   ├── placeholder.jpg
│   ├── browser-helpers.js              # now self-contained IIFE per #4
│   ├── detect-theme-toggle.js          # new per #9
│   ├── interaction-recipes.json        # expanded per #5
│   ├── capture-screenshots.mjs         # moved to code-side Phase 1.5
│   ├── capture-interactive.mjs         # moved to code-side Phase 1.5
│   ├── validate-handoff.py             # expanded per #8
│   └── validate-incremental.py
├── examples/
│   ├── audit-results.example.json      # new — a full worked example
│   ├── inconsistencies.example.json    # new per #7
│   └── claude-md.example.md            # new — full CLAUDE.md template
└── schemas/
    └── audit-results.schema.json       # tightened per #8
```

## For Claude Code: suggested order of operations

1. Unzip the handoff zip (`prometheus-e83j.onrender.com-audit.zip`) into your working dir.
2. Read `CLAUDE.md` and `audit-results.json` — note `screenshots_are_placeholders: true`.
3. Run Phase 1.5: Playwright harness that backfills real JPEGs at every screenshot path (both themes). Flip the placeholder flag when done.
4. Run the validator again: `python3 scripts/validate-handoff.py <project-folder>` — expect the placeholder WARNs to drop.
5. `git clone https://github.com/prometheus/prometheus` and produce `source-audit.json` (Phase 1-Source, optional).
6. Proceed to Phase 2 (token extraction), Phase 3 (component extraction), Phase 4 (docs site), Phase 5 (Figma plugin), Phase 6 (deploy + write `## Deployed skill output` URL into `CLAUDE.md`).
7. Re-run this wrapup skill once Phase 6 is done to generate the reference-vs-output comparison doc and the side-by-side HTML tool (Phases 2 and 3 of the wrapup).

At the same time, open a PR against the design-system-extraction-cowork skill with the fixes above. Prioritize the highest-impact issues (items #1–#4 here: CRITICAL / HIGH).
