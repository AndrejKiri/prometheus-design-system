---
name: design-system-extraction-cowork-wrapup
description: >
  Post-run wrapup for the design-system-extraction-cowork skill. Documents every
  friction point encountered during the cowork session with root cause and fix
  proposals, then compares the skill-output docs site against a reference design
  system site. Produces three artifacts: a friction-points markdown doc, a
  reference-vs-output comparison doc, and a side-by-side iframe HTML tool.
  Runs in Claude Code after the Cowork handoff zip has been received.
metadata:
  author: AndrejKiri
  version: '0.2'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
  paired-skill: design-system-extraction-cowork
---

# Design System Extraction Cowork — Wrapup Skill

Run this skill after `design-system-extraction-cowork` completes and you have
received the handoff zip. Produces three files that document what happened and
how the output compares to a reference.

---

## Phase 0 — Gather context

Ask the user for:

1. **Project folder** — path to the extracted handoff directory (contains
   `audit-results.json`, `screenshots/`, `CLAUDE.md`).
2. **Run identifier** — a short slug for this run (e.g. `run1`, `run2`). Used
   to prefix all output files.
3. **Reference URL** (optional) — base URL of the reference design system site
   (e.g. `https://andrejkiri.github.io/prometheus-design-system/`). Required for
   Phase 2 and Phase 3. If not provided, skip those phases and tell the user.

**Output folder is fixed.** Always write output files to `skill-outputs/<run-id>/`
at the project root (i.e. the root of the git repo, not the project folder).
Create the directory if it does not exist. Do not ask the user where to write —
this is always the correct location.

**Skill output URL** — read from `CLAUDE.md` in the project folder under
`## Deployed skill output`. If the entry is absent, skip Phases 2 and 3 and
tell the user to run Phase 6 of `design-system-extraction-code` first (which
deploys the site and writes the URL into `CLAUDE.md`).

Read `CLAUDE.md` and `audit-results.json` from the project folder for session
context (target URL, pages audited, scope, known limitations).

---

## Phase 1 — Friction points document

Write `<run-id>-feedback-skill-design-system-extraction-cowork.md` to the output
folder. This document records every friction point hit during the cowork session.

### Format

```markdown
# design-system-extraction-cowork skill — problems encountered & proposed fixes

<one-paragraph intro: skill ran to completion against <target-url>, 
what completed successfully (validator result, page count), then "This document
enumerates every friction point hit along the way — with each fix tagged by who
should implement it:">

- **[skill]** — change the design-system-extraction-cowork skill itself (SKILL.md,
  scripts, vocabulary files)
- **[validator]** — change `scripts/validate-handoff.py`
- **[cowork]** — change Cowork's sandbox plumbing (out of scope for a skill fix;
  noted so Claude Code knows what not to try to solve)
- **[handoff-to-cc]** — document a Phase 1.5 that Claude Code runs locally after
  Cowork hands off

---

## <N>. <Issue title> — <CRITICAL | HIGH | MEDIUM | LOW>

**What happened.** <concrete description of what went wrong, including exact
error messages, tool names, and what you tried>

**Root cause.** <why it happened — architectural constraint, missing
documentation, tool limitation, etc.>

**Fix.**

- **[tag]** <concrete fix proposal, including code snippets or script examples
  where applicable>

---
```

Repeat the numbered-section block for every issue encountered. Number issues in
order of impact (most disruptive first).

### Required sections after the numbered issues

After the last numbered issue, include these sections in order:

**Things Claude Code can do that Cowork cannot**

A numbered list of capabilities Cowork lacks that Claude Code can supply as
Phase 1.5 steps. For each capability: what it is, why Cowork can't do it, how
Claude Code would implement it. Common items to include if applicable:
- Real screenshot capture via Playwright/Puppeteer (Cowork sandbox blocks binary export)
- Source-code cross-reference via `git clone` + file search
- Build-time design-token extraction from source config files
- Accessibility audit via axe-core or pa11y
- Responsive-mode capture at multiple viewport widths
- Motion/animation probing

**Things neither Cowork nor Claude Code can do**

A numbered list of capabilities that are out of scope for both agents. State
clearly "Don't let the skill promise these." Common items:
- Real-user accessibility audit (automated tools catch ~40%)
- Cross-OS font-fallback rendering verification
- Real user timing / Core Web Vitals under realistic network conditions
- Licensed brand/typeface verification
- Security-scoped testing (CSRF, XSS)

**Suggested SKILL.md structure after fixes**

A directory tree (fenced code block) showing the recommended skill directory
layout after all fixes are applied. Include new scripts, vocabulary files, and
example directories proposed in the fixes above.

**For Claude Code: suggested order of operations**

A numbered list of the first steps Claude Code should take after receiving this
handoff — e.g., unpack zip, run Playwright screenshot capture, run validator,
clone source repo, proceed to Phase 2. End with: "At the same time, open a PR
against the design-system-extraction-cowork skill with the fixes above.
Prioritize the highest-impact issues."

---

## Phase 2 — Reference comparison document

Requires: Reference URL and Skill output URL from Phase 0. If either is missing,
skip this phase and tell the user.

Fetch HTML from both sites using `web_fetch`. Fetch these pages from each site:
`index.html`, `tokens.html`, `icons.html`, `components.html`, `patterns.html`,
`action-items.html`.

Write `<run-id>-feedback-baseline-vs-output-comparison.md` to the output folder.

### Format

```markdown
# <App name> Design System — Audit Report

**Reference:** <reference base URL>
**Skill output:** <skill output base URL>

Focus: visual design + structure & features. Format: bullet list.

---

## Overall verdict

<2–3 paragraphs: what the two sites have in common at the top level (same type
of thing, same color palette), then where they diverge — taxonomy, depth,
framing, tone. Name the core tension: the reference is typically a code-author's
view (React component names, CSS variables, implementation detail) while the
skill output is a DOM-audit's view (design-descriptive names, INC-coded findings,
audit-specific pages).>

---

## Homepage layout — side-by-side mock

> If you cannot render live screenshots (sandbox restriction), note this and
> say the companion side-by-side HTML tool is provided for pixel-level visual
> diffing.

---

## Header / top bar

- Compare: background color, text color, wordmark/title text, version chip,
  theme toggle placement and style, burger menu position.
- List every difference as a bullet.

## Left sidebar / primary navigation

- Compare: section groupings (flat list vs explicit section headers), page
  ordering, component list length and naming style, active-state styling.
- Note any pages present in one sidebar but absent from the other.

## Homepage content

- Compare: H1, tagline/subtitle, callout boxes (WIP notice, provenance),
  explore card grid (card count, card icons/tags, layout), stat lines, 
  acknowledgements section.

## Design Tokens page

- Compare: token families covered (colors, typography, spacing, radius,
  elevation, borders), depth of each section (extra sub-tables, CSS variable
  references, motion tokens, breakpoints, PromQL colors present only in
  reference?), color value consistency across both sites.
- Note any token families present in one but absent from the other.

## Icon Inventory page

- Compare: library attribution, icon count, grouping style, rendered-glyph
  availability, import-symbol column, Do/Don't guidelines, Figma note.
- List icons present in only one site.

## Components overview page

- Compare: component count, naming style (PascalCase React names vs 
  design-descriptive labels), grouping approach (per-card category tags vs
  explicit H2 category sections), per-component detail pages, Figma plugin
  download link placement.
- Map overlapping components: `Reference Name` ⇔ `Skill Name`.
- List reference-only and skill-only components separately.

## UI Patterns page

- Compare: pattern count, pattern names, depth of implementation detail
  (composition-level ASCII trees vs implementation code blocks with React
  component trees, URL param tables, hooks).

## Action Items page

- Compare: item count and ID scheme (PR#N vs AI-NNN), before/after visual
  mockups presence, migration guide presence, topic overlap and divergence.
- List topics present in only one site.

## Pages / routes present

- List: pages in both, reference-only pages, skill-only pages.

## Visual / styling feel (inferred from content + tokens declared)

- Compare: palette match, card visual style (category tag vs leading emoji),
  typography token alignment, anchor TOC in sub-pages.

## Content/tone

- Compare: authorship voice (first-person proposal vs report-like artefact),
  use of structured identifiers (INC-NNN, AI-NNN vs plain prose).

## Things that are the same (skill hits the mark on)

- Bullet list of what matched well: layout structure, color values, page set,
  token families, icon library, patterns coverage, Figma story.

## Biggest structural gaps if you want the skill output closer to the reference

- Numbered list of the most impactful differences to close, ordered by effort.
  Each item: what to add/change and what it would produce.

---

## How to verify visually

Open **`<run-id>-side-by-side-comparison.html`** in a browser (double-click the
file). Both frames navigate to the same page at the same time. Scroll each
independently.

---

*Generated <date> from web_fetch of each site's HTML. Pages fetched: home,
tokens, icons, components, patterns, action-items.*
```

---

## Phase 3 — Side-by-side comparison HTML

Requires: Reference URL and Skill output URL. If either is missing, skip.

Write `<run-id>-side-by-side-comparison.html` to the output folder. This is a
self-contained static HTML file — no dependencies, no server required.

### Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title><App name> Design System — Live Side-by-Side Comparison</title>
<style>
  /* box-sizing reset, full-height body */
  /* header: dark slate background (rgb(65,73,81)), white text, flexbox */
  /* select/input/button: semi-transparent white, rounded */
  /* .grid: css-grid 1fr 1fr, 1px gap on #dee2e6, height calc(100vh - 56px) */
  /* .pane: flexbox column, white background */
  /* .pane-header: light gray (#f8f9fa), border-bottom, tiny uppercase label */
  /* iframe: flex:1, width:100%, border:0 */
</style>
</head>
<body>
<header>
  <h1><App name> Design System — Live Side-by-Side</h1>
  <label>Page: <select id="pageSelect">
    <!-- one <option> per page present in both sites -->
    <!-- value = the .html filename, text = human label -->
    <!-- include at minimum: index.html (Home), tokens.html (Tokens),
         icons.html (Icons), components.html (Components),
         patterns.html (Patterns), action-items.html (Action Items) -->
    <!-- add any skill-only pages as additional options -->
  </select></label>
  <span class="meta">Both frames navigate together. Scroll each independently.</span>
</header>
<div class="grid">
  <div class="pane">
    <div class="pane-header">
      <span class="label">Reference</span>
      <span class="url" id="leftUrl"></span>
      <a id="leftOpen" target="_blank" rel="noopener">open ↗</a>
    </div>
    <iframe id="leftFrame" title="Reference site"></iframe>
  </div>
  <div class="pane">
    <div class="pane-header">
      <span class="label">Skill Output</span>
      <span class="url" id="rightUrl"></span>
      <a id="rightOpen" target="_blank" rel="noopener">open ↗</a>
    </div>
    <iframe id="rightFrame" title="Skill-output site"></iframe>
  </div>
</div>
<script>
  const REF_BASE = "<reference base URL — trailing slash>";
  const SKILL_BASE = "<skill output base URL — trailing slash>";
  const sel = document.getElementById("pageSelect");
  const leftFrame = document.getElementById("leftFrame");
  const rightFrame = document.getElementById("rightFrame");
  const leftUrl = document.getElementById("leftUrl");
  const rightUrl = document.getElementById("rightUrl");
  const leftOpen = document.getElementById("leftOpen");
  const rightOpen = document.getElementById("rightOpen");
  function update() {
    const p = sel.value;
    const l = REF_BASE + p;
    const r = SKILL_BASE + p;
    leftFrame.src = l; rightFrame.src = r;
    leftUrl.textContent = l; rightUrl.textContent = r;
    leftOpen.href = l; rightOpen.href = r;
  }
  sel.addEventListener("change", update);
  update();
</script>
</body>
</html>
```

Replace `REF_BASE` and `SKILL_BASE` with the actual base URLs. Both must end
with a trailing slash. The page selector options should match the actual pages
present in the skill output site (read from `design-system/` directory listing
if the project folder is available, otherwise use the standard set above).

---

## Output summary

After all phases complete, confirm:

- [ ] `<run-id>-feedback-skill-design-system-extraction-cowork.md` written
- [ ] `<run-id>-feedback-baseline-vs-output-comparison.md` written (if URLs provided)
- [ ] `<run-id>-side-by-side-comparison.html` written (if URLs provided)

Tell the user the output folder path and remind them to open the HTML file in
a browser for pixel-level visual comparison.
