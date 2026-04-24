# design-system-extraction-code skill — problems encountered & proposed fixes

The skill ran to completion against the run2 Cowork handoff zip
(`run2-output-cowork.zip`, 10 pages × 2 themes, 31 patterns, 9 inconsistencies).
The validator passed cleanly at the end (24/24 checks, 0 errors). The full
pipeline produced `tokens.json`, `components.json`, a 42-page docs site, and a
Figma plugin, deployed to GitHub Pages.

But the path from "audit zip" to "deployed site" was lumpier than necessary.
This document enumerates every friction point hit along the way — schema
confusion, tooling gaps, unclear instructions, and silent traps — with concrete
fix proposals tagged by target:

- **[skill]** — change the design-system-extraction-code skill instructions (`SKILL.md`)
- **[validator]** — change `scripts/validate-handoff.py`
- **[gen]** — prescribe or change the `gen.py` HTML generator approach
- **[figma]** — change Figma plugin template or instructions
- **[schema]** — change a JSON schema file

---

## 1. Phase 6 deploy URL was wrong because the skill ignores existing Pages workflows — CRITICAL

**What happened.** Phase 6 instructions told me to copy `design-system/`
contents into `$REPO_ROOT/$SKILL_OUTPUT_PATH/` and push. The repo's actual deploy
contract is a GitHub Actions workflow at `.github/workflows/pages.yml` that
ignores the literal path I pushed to and instead copies the *latest*
`skill-outputs/run*/<...>/design-system/` to `_site/skill-output/`. I documented
the deployed URL as the nested path I'd written to (`skill-outputs/run2/prometheus-audit/design-system/`).
The user opened the URL, hit a GitHub 404, and had to flag it. Cost: one round
trip + a second commit to fix `CLAUDE.md`.

**Root cause.** The skill assumes Pages is configured "Deploy from branch", but
many real repos use a workflow with a custom layout. SKILL.md never tells you
to look at `.github/workflows/` first.

**Fix.**

- **[skill]** — Add a Phase 6 step **before** the `cp -r` instruction:
  > **0. Check for an existing Pages workflow.** Run `ls .github/workflows/`.
  > If a `*pages*.yml` file exists, read it. The workflow may flatten, rename,
  > or filter your output path. The deployed URL is whatever the workflow
  > publishes to, not the literal repo path. If unsure, run
  > `gh api repos/<owner>/<repo>/pages` to see `build_type` — `workflow` means a
  > custom workflow controls the deploy.
- **[skill]** — Update the "Deployed URL" template in the
  `## Deployed skill output` block to be a question, not a fill-in:
  > URL: <run `gh api repos/<owner>/<repo>/pages` and the workflow's
  > `actions/deploy-pages` step output to confirm — do NOT guess from
  > filesystem layout>

---

## 2. `gen.py.template` is 90% TODO — Phase 4 required ~600 lines of fresh code — HIGH

**What happened.** The provided `templates/gen.py.template` is a working
skeleton (~330 lines) but every meaningful page renderer is a one-line stub:
`gen_tokens` literally writes `<!-- TODO: generate token tables from tokens.json -->`.
Producing a docs site that matches the SKILL.md spec — 3-section sidebar
(Foundations / Components / Audit), 5-card homepage with category tags + version
chip + WIP callout + Acknowledgements, swatches with CSS-var table, per-component
do/don't grid + design + implementation + layout + accessibility sections,
priority-bucketed action items with before/after, inconsistencies with canonical
+ reasoning + fix per item, migration grouping — required ~600 lines of new
Python plus ~500 lines of CSS. This took the majority of Phase 4 effort.

**Root cause.** The template was designed as a starting skeleton, but the
SKILL.md spec around it grew detailed (homepage card grid spec, sidebar spec,
component page section order, action-item card spec, etc.). The template did
not grow with the spec.

**Fix.**

- **[gen]** — Flesh out `gen.py.template` to render a complete site for any
  validated `tokens.json` + `components.json` + `audit-results.json` triple, not
  just a placeholder. Concretely, the template should ship working
  implementations of: `gen_tokens`, `gen_components`, `gen_component_page` (with
  do/don't + variants + specs + accessibility), `gen_action_items` (with
  priority buckets + before/after), `gen_inconsistencies`, `gen_migration`,
  `gen_audit_report`, `gen_index` (with version chip + WIP callout +
  acknowledgements), `gen_styles` (full styles.css including the mock-* class
  catalog), `gen_main_js`. Adding new pages should be the user's job; rendering
  the spec'd ones should be the template's job.
- **[gen]** — Split out `gen.py.template`'s embedded CSS and JS into separate
  `templates/styles.css.template` and `templates/main.js.template` files that
  `gen.py` reads and copies. This avoids a 1000-line Python file and lets the
  CSS be edited by humans.

---

## 3. Validator does not collect names from `spacing.layout` — five legitimate references rejected — HIGH

**What happened.** I put semantic spacing tokens in `tokens.json →
spacing.layout[]` (`header-height`, `icon-button-size`, `card-padding`,
`alert-padding`, `control-height`). Each is a valid named layout token per the
schema. Components referenced them in `tokens_used`. Validator failed:

```
[FAIL] components.json: components[0].variants[0]: tokens_used references 'header-height' not found in tokens.json
[FAIL] components.json: components[6].variants[0]: tokens_used references 'icon-button-size' not found in tokens.json
[FAIL] components.json: components[28].variants[0]: tokens_used references 'card-padding' not found in tokens.json
... (5 errors)
```

Cost: a 5-edit pass to either rename or strip the references, losing the
semantic layer in the process.

**Root cause.** [`scripts/validate-handoff.py`](scripts/validate-handoff.py)
lines 388–395 only walk `data["spacing"]["scale"]` when collecting
`token_names` — `spacing.layout` is silently dropped despite being a documented
schema field.

**Fix.**

- **[validator]** — In `validate_tokens`, after the `spacing.scale` loop, also
  walk `data["spacing"].get("layout", [])` and add each entry's `name` to
  `token_names`. Same treatment for any future top-level token category
  (`breakpoints`, `motion.durations`, `motion.easings`, `domain_lexicon[].term`).
- **[validator]** — Add a regression test: a `tokens.json` that uses every
  schema-allowed token category, plus a `components.json` that references one
  name from each, must validate clean.

---

## 4. `origin: "docs-meta"` components always fail validation — HIGH

**What happened.** SKILL.md explicitly tells me to mark docs-site chrome
components (theme toggle, sidebar nav button) with `origin: "docs-meta"`. I did:
two components, `theme-toggle` and `nav-button`. Validator:

```
[FAIL] components.json: components[31]: name 'theme-toggle' not found in audit-results.json patterns
[FAIL] components.json: components[32]: name 'nav-button' not found in audit-results.json patterns
```

The schema accepts `origin: ["derived", "docs-meta"]` but the validator
unconditionally enforces "name must match a pattern in audit-results.json"
without an exception for the docs-meta case. I had to remove both components
to get a clean validation run.

**Root cause.** [`scripts/validate-handoff.py`](scripts/validate-handoff.py)
lines 499–500:

```python
if pattern_names and name not in pattern_names:
    report.error(f"{ctx}: name '{name}' not found in audit-results.json patterns")
```

No `if comp.get("origin") == "docs-meta"` skip.

**Fix.**

- **[validator]** — Skip the pattern-name check when `comp.get("origin") ==
  "docs-meta"`. Also skip the "uncovered patterns" warning's expectation that
  every pattern have a derived component (already a warning, not an error —
  fine).
- **[skill]** — Once the validator change lands, restore the SKILL.md
  recommendation that docs-meta components belong in `components.json` (they
  currently *can't*, even though SKILL.md says they should).

---

## 5. PascalCase rule for `name` contradicts the validator's exact-match requirement — MEDIUM

**What happened.** SKILL.md Phase 3 says:

> `name` is PascalCase with no spaces or hyphens. ... e.g. `StatusBadge` ↔
> `status-badge`, `DataTable` ↔ `data-table`.

But the validator requires `name` to *exactly* match a pattern in
`audit-results.json`, where pattern names are written as humans see them in the
audit: `"Primary Button"`, `"Filter Input (Pills)"`, `"Mantine Alert Info
Callout"`. These two requirements are mutually exclusive. The
`components.schema.json` field description compounds the contradiction:

> "PascalCase. Must match pattern names from audit-results.json."

I read SKILL.md first, started writing PascalCase names, then noticed the
validator would reject every one of them (run1's components.json uses the
pattern names verbatim), and reverted. Cost: ~10 minutes thinking through which
authority to trust.

**Root cause.** The skill spec drifted away from the validator implementation.
Either side could be the source of truth; SKILL.md and the schema both reflect
an older or hoped-for design.

**Fix.** Pick one of these:

- **[skill]** + **[schema]** — Drop the PascalCase rule. Update SKILL.md to
  say: "`name` must match a pattern name from `audit-results.json` exactly,
  including spaces and special characters. The `slug` is the lowercased
  hyphenated form." Update the schema description to match.
- **OR [validator]** + **[skill]** — Keep PascalCase as the rule. Update the
  validator's pattern-name match to be slug-based or a normalized comparison
  (`audit_pattern.title().replace(" ", "")` ↔ `comp_name`). Update the `cowork`
  skill so `audit-results.json` patterns also carry a PascalCase name.

The first option is the smaller change.

---

## 6. No starter `mock-*` CSS in templates — every component variant required hand-written styles — MEDIUM

**What happened.** SKILL.md prescribes a `mock-<slug>` / `mock-<slug>--<variant>`
CSS class convention for component visual previews on each component page, and
says `mock_html` in `components.json` should reference these classes. But there
is no starter CSS file shipping the common patterns (badge, accordion, alert,
button, card, dropdown, header, table, input, pill, tab). For 31 components I
ended up writing ~30 mock classes from scratch in `styles.css`, each with its
own modifier variants for ok/error/active/etc. That's the bulk of the styles.css
weight.

**Root cause.** Templates ship `gen.py.template`, `figma-plugin/code.js.template`,
`figma-plugin/manifest.json.template` but no `styles.css.template` or
`mock-styles.css`. The SKILL.md says "all visual properties belong in styles.css
under the .mock-* section" without providing what that section should contain.

**Fix.**

- **[gen]** — Add `templates/mock-styles.css` that ships the most common mock
  classes (badge variants, accordion ok/error, alert info/warn/error, button
  primary/secondary, card with shadow, code block, dropdown, header, input
  variants, pill, table base + sortable, tab control). The `gen.py` template
  should concat this file into `styles.css` after the token block. New apps add
  their own bespoke mocks; common ones come for free.
- **[skill]** — Document where the mock CSS comes from in the Phase 4 file
  structure section (currently just lists `styles.css` as an output without
  saying which source files compose it).

---

## 7. Component pages need screenshots — convention for filename mapping is undocumented — MEDIUM

**What happened.** Each component page should have a "Component reference"
collapsible section showing where the component appears in the audited app.
`components.json` lists `pages: ["/targets", "/service-discovery", ...]` per
component. The audit's screenshots are filed as `<page-stub>-<theme>.jpg`
(e.g. `targets-light.jpg`). To wire this up I had to invent the page-url →
screenshot-filename mapping (`p.strip("/").replace("/", "-") + "-light.jpg"`).
The SKILL.md component-page template mentions a `component_references` field
that doesn't exist in the schema.

**Root cause.** The schema models pages as URL strings but doesn't carry the
screenshot filename. The SKILL.md generator template references a field
(`component_references`) that the schema doesn't define and that the audit
doesn't emit.

**Fix.**

- **[schema]** — Add an optional `screenshots[]` array to each component:
  `[{page: "/targets", light: "targets-light.jpg", dark: "targets-dark.jpg"}]`.
  Either the cowork skill or the code skill can populate it from the audit's
  screenshot list.
- **[skill]** — Until the schema change lands, document the URL-to-filename
  convention in Phase 4 ("convert page URL to screenshot stub by stripping `/`
  and joining with `-`") so every gen.py implementation does the same thing.

---

## 8. Figma plugin token transformation is manual — MEDIUM

**What happened.** The `figma-plugin/code.js.template` has comment markers like
`// {{POPULATE_FROM_tokens.colors.brand}}` but no helper script that reads
`tokens.json` and emits a populated `code.js`. I wrote a one-off ~30-line Python
script inline to convert each `rgb(...)` value to Figma's 0–1 RGB format and
print the populated constants. Anyone running this skill will reinvent the same
script.

**Root cause.** Templates encode the *shape* of the populated file but not the
transformation that fills it in.

**Fix.**

- **[figma]** — Ship `scripts/tokens-to-figma.py` that reads `tokens.json` and
  writes a populated `figma-plugin/code.js`. The current `code.js.template`
  becomes the script's output template, not a manual fill-in.
- **[skill]** — Phase 5 instructions become: `python3 <skill-path>/scripts/tokens-to-figma.py
  --tokens tokens.json --out design-system/figma-plugin/code.js`.

---

## 9. Action-item recommended shape isn't documented — schema-required minimum produces thin cards — MEDIUM

**What happened.** The schema only requires `id`, `title`, `description`,
`priority`, `effort`, `labels` for an action item. To produce useful cards on
the docs site (with the before/after diff blocks the skill *also* prescribes),
you need `before_after.{before_html, after_html}`, `files_changed`,
`related_inconsistency`, and `github_issue_title`. The first time I drafted
action items I omitted most of these and the rendered page looked threadbare.
Had to do a second pass.

**Root cause.** Schema describes "what's allowed" but the SKILL.md narrative
recommends a richer shape without saying "you should always include
`before_after` and `files_changed`".

**Fix.**

- **[skill]** — Phase 3 "Action items" section already says "Each card: id,
  title, description, priority, effort, labels, related_inconsistency, before,
  after, files_changed". Promote that line to a "RECOMMENDED" emphasis: every
  card *should* carry before+after+files_changed even though only the first six
  are validator-required.

---

## 10. components.schema.json `name` field description is self-contradictory — MEDIUM

**What happened.** Looking at the field:

```json
"name": {
  "type": "string",
  "description": "PascalCase. Must match pattern names from audit-results.json."
}
```

Pattern names from audit-results.json are NOT PascalCase. They're
`"Primary Button"`, `"Filter Input (Pills)"`, etc. The two sentences in the
description contradict each other. Cost: read the description, get confused,
read the validator code to find the truth.

**Root cause.** Same as #5 — schema text was updated halfway through a planned
PascalCase migration that never landed in the validator or in the upstream
cowork skill.

**Fix.** Same as #5 (resolve the PascalCase question), then update the schema
description to match the resolved decision.

---

## 11. Bash tool `grep` exit code 1 cancels parallel calls — environmental but worth noting — LOW

**What happened.** During Phase 6 automated QA I ran multiple Bash calls in
parallel: `grep -l 'href="/components"' *.html` (expected to return nothing —
exit 1 from grep), `grep -c onerror components/*.html`, `ls *.html | wc -l`.
Grep's exit-1 caused the Bash tool to error out and cancel the *other*
parallel-queued tools too. Cost: 2 turns rerunning each separately.

**Root cause.** Not a skill bug — Claude Code Bash tool behavior. But the QA
checklist commands in SKILL.md naturally produce exit-1 grep calls.

**Fix.**

- **[skill]** — In the Phase 6 automated-QA section, wrap any "expect no
  matches" grep with `|| true`, e.g.
  `grep -l 'href="/components"' *.html components/*.html || echo "ok"`. Add a
  one-line tip near the QA checklist: "When grep is checking for the *absence*
  of a match, append `|| true` so a 0-match exit code doesn't cancel parallel
  Bash calls."

---

## Summary: issues by phase

| Phase | Issue | Severity |
|-------|-------|----------|
| 2 — Tokens | #3 `spacing.layout` token names not collected by validator | **High** |
| 3 — Components | #4 `origin: "docs-meta"` components rejected by validator | **High** |
| 3 — Components | #5 PascalCase rule conflicts with pattern-name match | Medium |
| 3 — Components | #9 Action-item recommended shape not documented | Medium |
| 3 — Components | #10 `components.schema.json` `name` description self-contradictory | Medium |
| 4 — Docs site | #2 `gen.py.template` mostly TODO — 600 LOC required | **High** |
| 4 — Docs site | #6 No starter `mock-*` CSS in templates | Medium |
| 4 — Docs site | #7 Component-page screenshot filename mapping undocumented | Medium |
| 5 — Figma | #8 Manual rgb-to-figma token transformation | Medium |
| 6 — Deploy/QA | #1 Phase 6 ignores existing Pages workflows | **Critical** |
| 6 — Deploy/QA | #11 Bash grep exit-1 cancels parallel calls | Low |

---

## Suggested skill directory structure after fixes

```
design-system-extraction-code/
├── SKILL.md                        # updated: Phase 6 Pages-workflow check, docs-meta restored, mock-CSS layering, screenshot-mapping convention, action-item recommended shape, grep || true tip
├── README.md
├── schemas/
│   ├── audit-results.schema.json
│   ├── source-audit.schema.json
│   ├── tokens.schema.json
│   └── components.schema.json      # updated: name description matches resolved PascalCase decision; new optional screenshots[] field
├── scripts/
│   ├── validate-handoff.py         # updated: collect spacing.layout / breakpoints / motion / lexicon names; skip pattern-match for origin=docs-meta
│   └── tokens-to-figma.py          # NEW: rgb→figma 0-1 conversion, populates code.js
├── templates/
│   ├── gen.py.template             # updated: working renderers for every spec'd page, not just stubs
│   ├── styles.css.template         # NEW: full design-system stylesheet with token block + 3-section sidebar
│   ├── main.js.template            # NEW: theme toggle + burger + copy + issue-link, extracted from gen.py
│   ├── mock-styles.css             # NEW: catalog of common .mock-* classes for the most-recurring component shapes
│   └── figma-plugin/
│       ├── manifest.json.template
│       └── code.js.template        # repurposed: the output template for tokens-to-figma.py, not a manual fill-in
└── examples/
    └── prometheus-e83j.onrender.com/   # this run's full project folder, validator-clean, deployed
```

---

## For Claude Code: suggested order of fixes

1. **#1 (Pages workflow check)** — `[skill]` Phase 6 section. Add a "0. Check
   `.github/workflows/`" step before the `cp -r` instruction. Highest-impact
   fix because the symptom (404 in the browser) only surfaces after the user
   sees it; failing earlier or pointing to the right URL costs nothing.
2. **#3 (`spacing.layout` validator coverage)** — `[validator]` 5-line change.
   Lifts an arbitrary restriction that punished a documented use of the schema.
3. **#4 (docs-meta components)** — `[validator]` 1-line `if origin ==
   "docs-meta": continue`. Removes the contradiction between SKILL.md and the
   validator; lets people actually do what the skill tells them to.
4. **#2 (gen.py.template flesh-out)** — `[gen]` largest single change but the
   biggest time savings per future run. Pair with #6 (mock-styles.css) since
   they ship together.
5. **#5 + #10 (PascalCase resolution)** — `[skill]` + `[schema]`. Pick a
   direction; update SKILL.md and the schema description in the same patch.
6. **#7 (screenshot filename mapping)** — `[schema]` add `screenshots[]` field.
   Pair with the cowork skill so it populates the field at audit time.
7. **#8 (tokens-to-figma.py)** — `[figma]` standalone script. Isolated change.
8. All remaining medium/low items as a second pass.
