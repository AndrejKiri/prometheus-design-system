# design-system-extraction-code skill — problems encountered & proposed fixes

Handoff to Claude Code. The design-system-extraction-code skill ran to completion
against the Prometheus audit zip `prometheus-e83j.onrender.com-audit.zip`
(Phase 1 output from the design-system-extraction-cowork skill). All 6 phases completed and
the validator exited 0 (25/25 PASS). This document enumerates every friction
point hit along the way — schema confusion, tooling gaps, unclear instructions,
and silent traps — with concrete fix proposals tagged by target:

- **[skill]** — change the design-system-extraction-code skill instructions (SKILL.md)
- **[validator]** — change `scripts/validate-handoff.py`
- **[gen]** — prescribe or change the `gen.py` HTML generator approach
- **[figma]** — change Figma plugin template or instructions
- **[schema]** — change a JSON schema file

---

## 1. `typography.styles[i].font_family` cross-reference is non-obvious — CRITICAL

**What happened.** The validator checks that each typography style's
`font_family` field matches the `name` of an entry in `typography.families[]`
— i.e., it is a *reference key*, not a CSS font stack. First attempt used the
full CSS string `"-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto…"` for
sans-serif styles and `"monospace"` for code styles. Validator threw 7 errors:

```
ERROR tokens.json typography.styles[0].font_family: value "-apple-system,
BlinkMacSystemFont…" not found in typography.families[*].name
```

Fixing required rewriting all 7 style entries to use the family's `name` field
(`"body"` or `"mono"`), not the CSS value.

**Root cause.** The schema enforces a cross-reference constraint (relational
integrity), but nowhere in Phase 2's prose or in the schema's `description`
field is this explained. The field is named `font_family`, which everywhere else
in CSS/design means a font-family string value. The skill uses it as a foreign
key.

**Fix.**

- **[skill]** In Phase 2's typography section, add an explicit callout:
  > `font_family` in each style entry is a **reference** to
  > `typography.families[].name` — use the short name token (e.g. `"body"`,
  > `"mono"`) not the CSS family string. Think of it as a foreign key.
- **[schema]** Add a `description` on the `font_family` field in
  `tokens.schema.json`:
  ```json
  "font_family": {
    "type": "string",
    "description": "Must match the 'name' field of an entry in typography.families[]. This is a reference key, not a CSS family string."
  }
  ```
- **[validator]** When this error fires, print an actionable hint rather than
  just the mismatch: *"font_family must be a name reference from
  typography.families[*].name. You provided a CSS stack string. Use the family's
  short name token instead (e.g. 'body', 'mono')."*

---

## 2. `python` command not found — validator fails to run

**What happened.** The skill's instruction says:

```bash
python <path-to-this-skill>/scripts/validate-handoff.py <project-folder>
```

On macOS 14+, `python` is not in PATH — only `python3`. First run immediately
failed:

```
zsh: command not found: python
```

**Root cause.** macOS dropped the `python` → `python3` symlink in Monterey.
The skill was written assuming a Linux/Debian environment where `python` may
still exist.

**Fix.**

- **[skill]** Replace every `python` invocation in SKILL.md with `python3`.
- **[validator]** Add a shebang `#!/usr/bin/env python3` to
  `validate-handoff.py` so it can be run as `./validate-handoff.py` without
  specifying the interpreter at all.
- **[skill]** Add a one-time env check at the top of Phase 0:
  ```bash
  python3 --version || { echo "python3 required"; exit 1; }
  ```

---

## 3. Skill does not prescribe using a generator script for the docs site

**What happened.** Phase 4 says "Produce a static HTML/CSS/JS site." There are
28 HTML files (10 top-level + 18 component pages). The natural Claude Code
approach is 28 separate `Write()` calls, which is slow, error-prone to nav
drift, and burns context window. The right approach is a Python generator
(`gen.py`) that reads `tokens.json` + `components.json` + `audit-results.json`
and writes all files in one pass. I had to invent this approach; the skill
should prescribe it.

**Root cause.** Phase 4 describes what to produce but not *how* to produce it.
When there are N pages sharing identical nav blocks, a generator is the only
maintainable approach.

**Fix.**

- **[skill]** In Phase 4, add a prescriptive instruction:
  > Write a `gen.py` generator in the project folder (not inside
  > `design-system/`). It reads `tokens.json`, `components.json`, and
  > `audit-results.json`, then writes every HTML file. Run it once to produce
  > the full site. Never write HTML files by hand unless fixing a single-file
  > bug — always regenerate from source.
- **[gen]** The generator should be explicitly structured with:
  - `sidebar_nav(prefix="")` helper that produces consistent nav with correct
    relative paths (top-level: `href="tokens.html"`, component pages:
    `href="../tokens.html"`)
  - `gen_component_page(comp)` that produces pages in the prescribed section
    order
  - A `main()` that writes all files to `design-system/` and prints a
    file-count summary
- **[skill]** In the "Navigation" section, replace the Python one-liner batch
  pattern with: "Use the generator. If you must patch nav in place, use the
  one-liner." The current wording implies the one-liner is the primary approach.

---

## 4. `components/<slug>.html` + `components.html` path collision not addressed clearly enough

**What happened.** The skill warns: *"Path collision warning. `components.html`
and `components/` coexist."* But it doesn't say: always create `components/`
as a directory *before* writing `components.html`, otherwise some file-write
tools may create `components` as a file. In generator code, the ordering
matters.

**Root cause.** A note doesn't replace an instruction. The skill assumes the
reader will sequence file creation correctly.

**Fix.**

- **[gen]** In gen.py, always `os.makedirs("design-system/components",
  exist_ok=True)` as the first file-system operation, before writing any HTML.
- **[skill]** Change the note to an instruction: "Create the `components/`
  directory first, then write `components.html`. Order matters — some tools
  treat a pre-existing file named `components` as a collision with the
  directory."

---

## 5. `screenshots/` symlink vs copy — deployment behavior not specified

**What happened.** The docs site needs screenshots accessible at
`design-system/screenshots/<slug>-<theme>.jpg`. The options are:
1. Copy all screenshots into `design-system/screenshots/`
2. Create a relative symlink: `design-system/screenshots → ../screenshots`

I used a symlink (option 2). Symlinks work for local `npx serve` but break on
GitHub Pages (Pages does not follow symlinks — it silently skips symlinked
directories). The skill doesn't mention this.

**Root cause.** The skill says "Symlink or copy from project root" without
noting that symlinks fail in the most common deployment target.

**Fix.**

- **[skill]** Change the screenshots note to: "**Copy** screenshots into
  `design-system/screenshots/` rather than symlinking. Symlinks are ignored by
  GitHub Pages and some static hosts. The generator should copy files at build
  time with `shutil.copy2`."
- **[gen]** In `gen.py`, add a step:
  ```python
  import shutil
  src = pathlib.Path("screenshots")
  dst = pathlib.Path("design-system/screenshots")
  if src.exists():
      shutil.copytree(src, dst, dirs_exist_ok=True)
  ```
  Run this before writing HTML.

---

## 6. `figma_rgb` pre-computation is easy to skip; no explicit formula given

**What happened.** Phase 2 says "Fill `figma_rgb` (0–1 range) on brand colors."
The audit-results.json stores colors as `rgb(34, 139, 230)` CSS strings. To
convert, you divide each channel by 255. That's obvious once you know it, but
the skill doesn't spell it out. I had to run a manual Python one-liner to get
the values right, then verify against the Figma plugin output.

**Root cause.** Phase 2 mentions the requirement as a single sentence under a
subsection. The formula isn't given, and there's no note about rounding
precision (number of decimal places matters for readability in code.js).

**Fix.**

- **[skill]** In Phase 2, add a box:
  > **Figma RGB formula:** `figma_rgb = { r: R/255, g: G/255, b: B/255 }`.
  > Round to 4 decimal places. Example: `rgb(34, 139, 230)` →
  > `{ r: 0.1333, g: 0.5451, b: 0.9020 }`.
  >
  > Helper snippet:
  > ```python
  > import re
  > def to_figma_rgb(css):
  >     r,g,b = map(int, re.findall(r'\d+', css)[:3])
  >     return {"r": round(r/255,4), "g": round(g/255,4), "b": round(b/255,4)}
  > ```
- **[validator]** Check that all `figma_rgb` values are in [0, 1] range and
  flag any integer values > 1 (a common mistake where raw 0–255 values are
  written directly).

---

## 7. Status color border defaults to opaque black — wrong in dark mode

**What happened.** The audit-results.json's status color observations didn't
include explicit border values for status badges. The skill requires
`light.border` and `dark.border` in every status color entry. I defaulted to
`{ r: 0, g: 0, b: 0 }` (opaque black). In dark mode, black borders on dark
backgrounds are invisible and in light mode they produce harsh outlines that
don't match the actual app.

**Root cause.** The schema requires a border field but doesn't say what to use
when the app has no visible border (border-style: none or border-color:
transparent). The correct default is transparent: `{ r: 0, g: 0, b: 0, a: 0 }`.
But `a` (alpha) isn't even in the Figma RGB type currently.

**Fix.**

- **[skill]** In Phase 2's status colors section, add: "If the app uses no
  visible border on status badges, set border to transparent:
  `{ r: 0, g: 0, b: 0, a: 0 }`. Do not default to opaque black."
- **[schema]** Allow an optional `a` field (0–1 alpha) on all `figma_rgb`
  objects so transparent can be expressed.
- **[figma]** In `code.js.template`, where `setValueForMode` is called for
  border colors, add a comment: *"If alpha is 0, Figma treats this as
  transparent — correct behavior for no-border states."*

---

## 8. `mock_html` ↔ `.mock-*` CSS class naming convention is implicit

**What happened.** Phase 3 says each variant should have `mock_html` for Phase
4 rendering. Phase 4 says to write `.mock-*` CSS classes. But the naming
convention connecting them is nowhere stated — the generator has to infer it.
In practice I used `.mock-badge-ok`, `.mock-badge-err`, `.mock-panel-open`,
etc. A future skill run might use `.badge--ok`, `.panel--expanded`, and
produce broken previews.

**Root cause.** The skill treats mock_html and styles.css as separate concerns
without defining a naming contract between them.

**Fix.**

- **[skill]** Add a "Mock class naming convention" section:
  > `.mock-<component-slug>` is the base class; variants append `-<modifier>`:
  > `.mock-badge-ok`, `.mock-badge-err`, `.mock-panel-loading`, etc.
  > `mock_html` in components.json must use these exact class names.
  > The generator's styles.css must define matching rules.
  > Never use BEM (`--`, `__`) in mock class names — it conflicts with the base
  > style's flat class structure.

---

## 9. Phase dependency graph is never stated

**What happened.** The skill's phases are numbered 0–6 and described
sequentially, implying a strict order. But it's not stated explicitly. A
reader could reasonably wonder: can I run Phase 3 before Phase 2 is validated?
Can I run Phase 5 before Phase 4 is complete? The validator is progressive but
won't tell you that phases have hard dependencies.

**Root cause.** The skill prose describes each phase but doesn't summarize the
dependency graph. For a 6-phase process this matters.

**Fix.**

- **[skill]** Add a dependency diagram at the top of SKILL.md:
  ```
  Phase 1 (design-system-extraction-cowork) → Phase 2 (tokens) → Phase 3 (components)
                                        ↘
                                          Phase 4 (docs site) → Phase 5 (Figma plugin)
                                        ↗
                                Phase 3 (components)
                                          ↓
                                    Phase 6 (deploy + QA)
  ```
  With a note: "Phases 4 and 5 both read tokens.json and components.json.
  Do not start Phase 4 until both Phase 2 and Phase 3 validator passes are
  clean."

---

## 10. How to handle gaps in audit-results.json is not documented

**What happened.** Several fields in audit-results.json were sparse or
absent — for example, explicit dark-mode border colors for status badges,
exact shadow values for some cards, letter-spacing on code blocks. The skill's
Phase 2 instruction says "derive from audit-results.json" but doesn't say what
to do when a value simply isn't there.

**Root cause.** The audit can only observe what's present and computable at the
time. Some values require screen-pixel measurement or source-code inspection
that may have been skipped.

**Fix.**

- **[skill]** Add a "Handling missing values" section to Phase 2:
  > When a value is absent from audit-results.json:
  > 1. Check `source-audit.json` (if available) for the authored value.
  > 2. If source audit is absent, use the most visually conservative default:
  >    transparent for borders, 0 for shadow spread, `inherit` for
  >    letter-spacing.
  > 3. Tag the token with `"derived": false, "note": "Not observed in audit —
  >    using conservative default. Verify against source."` so downstream
  >    consumers know to re-check.
- **[schema]** Add optional `derived` (boolean) and `note` (string) fields on
  token leaf objects so gaps can be flagged in the data itself.

---

## 11. Generator must be re-run to pick up changes — no watch mode or incremental rebuild

**What happened.** During Phase 4 iteration I edited tokens.json or
components.json, then had to manually remember to re-run gen.py. There's no
make-style dependency tracking or watch mode. If gen.py is run once and then
a JSON file is edited, the HTML silently goes stale.

**Root cause.** gen.py is a one-shot generator; the skill doesn't address
iteration workflow.

**Fix.**

- **[gen]** Add a `--watch` flag to gen.py that uses `watchdog` (or polling
  fallback) to re-run on any change to `*.json` in the project folder.
- **[skill]** In Phase 4, note: "While building, run `python3 gen.py --watch`
  in one terminal and `npx serve design-system -l 3000` in another. Changes
  to JSON files will re-generate the site automatically."
- **[skill]** As a minimum even without watch mode: "After editing any JSON
  source, always re-run `python3 gen.py` before reviewing the site."

---

## 12. Figma plugin cannot be tested without a Figma account

**What happened.** The quality checklist item "Figma plugin runs without
crashing — font fallbacks tested" is unverifiable without a live Figma session.
I shipped the plugin based on static code review only. The font-fallback chain
(requested family+weight → Regular → Inter+weight → Inter) was present but not
execution-tested.

**Root cause.** The skill includes a quality checklist item that requires
external access it can't guarantee.

**Fix.**

- **[skill]** Change the checklist item to: "Figma plugin code reviewed for
  font fallback correctness (execution test requires Figma account — see
  manual QA step)."
- **[skill]** Add a "Manual QA" subsection in Phase 5 with step-by-step
  instructions for a human tester:
  1. Open Figma → Plugins → Development → Import plugin from manifest.
  2. Run the plugin.
  3. Verify: variable collections appear (Brand, Spacing, Radius, Surface,
     Text, Status Colors).
  4. Verify: text styles appear with correct names.
  5. Verify: elevation/card effect style appears.
  6. Check console for font fallback messages (expected when Courier New
     weight variants don't resolve).
- **[figma]** Add `console.log` statements in `createTextStyles()` that print
  which fallback level was used for each style, so testers can verify the
  fallback chain fired correctly:
  ```js
  console.log(`[font] ${def.name}: ${resolvedFamily} / ${resolvedStyle}`);
  ```

---

## 13. `action_items[]` location in components.json vs the docs site is confusing

**What happened.** The skill puts `action_items[]` inside `components.json` as
a top-level array. But action items are surfaced on `action-items.html` in the
docs site. The generator needs to read them from `components.json`, but the
skill doesn't state this mapping. A developer reading Phase 4 would look for
an `action-items.json` that doesn't exist.

**Root cause.** `action_items` logically belongs to components (they reference
INC IDs and component slugs), but their rendering target is a standalone page.
The skill doesn't bridge the two.

**Fix.**

- **[skill]** In Phase 4's file structure table, note next to `action-items.html`:
  "(data source: `components.json → action_items[]`)"
- **[gen]** In gen.py, document the source mapping at the top of
  `gen_action_items_page()`:
  ```python
  # source: components["action_items"] — top-level array in components.json
  ```
- **[skill]** Consider moving action_items to its own `action-items.json` for
  clarity. Or explicitly document in Phase 3: "action_items[] is a top-level
  array in components.json, not a separate file."

---

## 14. No guidance on output zip naming conventions

**What happened.** The skill says to name the zip after the app hostname
(`<app-hostname>-design-system.zip`). The Cowork audit zip was named
`prometheus-e83j.onrender.com-audit.zip`. The output zip became
`prometheus-e83j.onrender.com-design-system.zip`. That's correct, but only by
inference — the skill doesn't say "use the same hostname prefix as the input
zip" or "derive from the URL in CLAUDE.md".

**Root cause.** The naming rule is stated but not operationalized.

**Fix.**

- **[skill]** Add a concrete derivation rule:
  > Zip name = `<hostname>-design-system.zip` where `<hostname>` is the `host`
  > component of the URL in CLAUDE.md (e.g. `prometheus-e83j.onrender.com`).
  > To extract it: `python3 -c "from urllib.parse import urlparse; print(urlparse('<url>').netloc)"`.
- **[skill]** Add a sample snippet to Phase 6:
  ```bash
  APP_URL=$(grep -m1 'URL:' CLAUDE.md | awk '{print $3}')
  HOSTNAME=$(python3 -c "from urllib.parse import urlparse; print(urlparse('$APP_URL').netloc)")
  zip -r "../${HOSTNAME}-design-system.zip" .
  ```

---

## 15. Validator `<path-to-this-skill>` is ambiguous in Claude Code context

**What happened.** SKILL.md says to run:
```bash
python <path-to-this-skill>/scripts/validate-handoff.py <project-folder>
```
But `<path-to-this-skill>` is not defined anywhere in Claude Code context. The
skill lives at `.claude/skills/design-system-extraction-code/` relative to the project
root, but the user's project root is also the working directory — so you need
to figure out this path at runtime. First attempt used a wrong relative path
and got `ModuleNotFoundError`.

**Root cause.** The instruction uses a placeholder that requires environment
knowledge not explicitly provided.

**Fix.**

- **[skill]** Replace with an absolute path derivation instruction:
  > The skill directory is at `<project-root>/.claude/skills/design-system-extraction-code/`.
  > Run the validator as:
  > ```bash
  > python3 "$(pwd)/.claude/skills/design-system-extraction-code/scripts/validate-handoff.py" <project-folder>
  > ```
  > Or from within the project folder:
  > ```bash
  > python3 ../.claude/skills/design-system-extraction-code/scripts/validate-handoff.py .
  > ```
- **[validator]** Make `validate-handoff.py` accept the project folder as either
  a positional arg or `--project <path>` for clarity.

---

## 16. QA checklist item "mobile responsive — burger menu works" is unverifiable without a browser

**What happened.** Phase 6's QA checklist includes "Mobile responsive — burger
menu works." Claude Code cannot open a browser viewport at 375px and click the
burger button. The checklist item was passed with a comment "requires manual
browser test." But the skill marks it as a standard checklist item with no
asterisk or qualification.

**Root cause.** The checklist mixes items Claude Code can verify (file
existence, link patterns, HTML structure) with items requiring a real browser
(layout, JS interaction, mobile breakpoints).

**Fix.**

- **[skill]** Split Phase 6's QA checklist into two sections:
  - **Automated checks** (Claude Code can verify): validator passes, all 28
    HTML files exist, no broken `../` path patterns in component pages, all
    screenshot `<img>` tags have `onerror` handlers, copy buttons present on
    `<pre>` blocks (structural check), Figma plugin manifest valid JSON.
  - **Manual browser checks** (human tester): light/dark mode per page, mobile
    burger menu, copy buttons actually copy, no broken images, interactive
    component references load.
- **[skill]** At the end of Phase 6, add: "Open a PR or hand off to a human for
  manual browser QA. Claude Code cannot substitute for a real browser
  interaction test."

---

## 17. No prescribed place to document design decisions / token resolution rationale

**What happened.** Several tokens required judgment calls: which of two similar
blues to treat as `brand-blue-light` vs `brand-blue-dark`, what the canonical
nav slate color is, how to handle a border color that was absent from the audit.
These decisions live in the conversation transcript but not in any artifact.
Future maintainers of the design system have no record of why a token has its
value.

**Root cause.** The skill's output schema has no field for rationale or
provenance on tokens or components.

**Fix.**

- **[schema]** Add an optional `rationale` string field to token objects in
  `tokens.schema.json`. Populated when the value required a judgment call or
  conflict resolution. Example:
  ```json
  "brand-blue-light": {
    "value": "#228BE6",
    "figma_rgb": { … },
    "rationale": "Most frequent blue in audit (12/18 patterns). Mantine's
                   default primary color at 600 weight."
  }
  ```
- **[skill]** In Phase 2, add: "For any token where you had to choose between
  multiple observed values or apply a default, add a `rationale` string
  explaining the choice."
- **[skill]** In Phase 3, same: "For each `related_inconsistency`, record in
  `resolution` the chosen canonical behavior and why."

---

## 18. Skill is silent on what to do when `design-system/` already exists

**What happened.** If Phase 4 is re-run (e.g., to fix a bug in gen.py), old
generated files may persist alongside new ones if the generator doesn't clean
up. Component slugs that were renamed between runs leave orphaned HTML files
that will have dead nav links.

**Root cause.** The skill says to build into `design-system/` but never says to
clean it first.

**Fix.**

- **[gen]** At the top of gen.py's `main()`:
  ```python
  import shutil
  ds = pathlib.Path("design-system")
  if ds.exists():
      # Remove generated HTML only — preserve figma-plugin/ and screenshots/
      for f in ds.glob("*.html"):
          f.unlink()
      comps_dir = ds / "components"
      if comps_dir.exists():
          shutil.rmtree(comps_dir)
  ```
- **[skill]** Note: "Each run of gen.py regenerates all HTML. The generator
  cleans up stale component pages automatically. Do not manually place files
  in `design-system/` — they will be removed on the next gen.py run."

---

## Summary: issues by phase

| Phase | Issue | Severity |
|-------|-------|----------|
| 0 — Entry | `python` not found (macOS) | High |
| 0 — Entry | Validator path ambiguous in Claude Code context | Medium |
| 2 — Tokens | `font_family` cross-reference not documented | **Critical** |
| 2 — Tokens | `figma_rgb` formula not given | Medium |
| 2 — Tokens | Status border defaults to opaque black | Medium |
| 2 — Tokens | No guidance on handling missing audit values | Medium |
| 3 — Components | `mock_html` ↔ CSS class naming implicit | Medium |
| 3 — Components | `action_items` location confusing | Low |
| 4 — Docs site | Generator not prescribed | High |
| 4 — Docs site | `components/` directory creation ordering | Medium |
| 4 — Docs site | Screenshots symlink breaks GitHub Pages | High |
| 4 — Docs site | No watch mode / stale HTML risk | Low |
| 5 — Figma | Plugin untestable without Figma account | Medium |
| 5 — Figma | No debug logging in font fallback chain | Low |
| 6 — QA | Manual checks mixed with automated checks | Medium |
| All | Phase dependency graph unstated | Medium |
| All | No token rationale field | Low |
| All | `design-system/` stale files on re-run | Medium |
| All | Output zip naming not operationalized | Low |
| All | No `derived`/`note` fields for gap tokens | Low |

---

## Suggested skill directory structure after fixes

```
design-system-extraction-code/
├── SKILL.md                       (updated per above)
├── README.md
├── schemas/
│   ├── audit-results.schema.json  (add screenshots_are_placeholders flag)
│   ├── tokens.schema.json         (add font_family description, rationale, derived/note)
│   ├── components.schema.json     (clarify action_items location)
│   └── source-audit.schema.json
├── scripts/
│   ├── validate-handoff.py        (add --project flag, python3 shebang, better error messages)
│   └── to-figma-rgb.py            (new: helper for token color conversion)
├── templates/
│   ├── gen.py.template            (new: generator template with watch mode)
│   ├── figma-plugin/
│   │   ├── manifest.json.template
│   │   └── code.js.template       (add console.log for font fallback)
│   └── styles.css.template        (new: base CSS with mock-* class stubs)
└── examples/
    └── prometheus-audit/          (this run, as a working example)
```

---

## For Claude Code: suggested order of fixes

1. **#1 (font_family)** — schema description + validator error message +
   skill prose. Biggest source of confusion; will confuse every future run.
2. **#2 (python3)** — simple one-line fix in all SKILL.md code blocks.
3. **#3 (generator)** — add gen.py.template and update Phase 4 prose.
4. **#5 (screenshots copy vs symlink)** — update skill + add shutil.copytree
   to gen.py.template.
5. **#6 (figma_rgb formula)** — add box to Phase 2 + to-figma-rgb.py helper.
6. **#15 (validator path)** — update SKILL.md invocation instructions.
7. **#16 (QA checklist split)** — split into automated vs manual sections.
8. All remaining medium/low items as a second pass.
