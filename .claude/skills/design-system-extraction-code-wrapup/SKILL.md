---
name: design-system-extraction-code-wrapup
description: >
  Post-run wrapup for the design-system-extraction-code skill. Documents every
  friction point encountered during the Claude Code session — schema confusion,
  tooling gaps, unclear instructions, silent traps — with root cause analysis
  and concrete fix proposals tagged by target. Produces a single friction-points
  markdown doc with a phase summary table and a suggested skill directory
  structure. Run at the end of a design-system-extraction-code session.
metadata:
  author: AndrejKiri
  version: '0.2'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
  paired-skill: design-system-extraction-code
---

# Design System Extraction Code — Wrapup Skill

Run this skill at the end of a `design-system-extraction-code` session, after
Phase 6 (deploy & QA) completes. Produces one feedback document that records
what went wrong, why, and how to fix it.

---

## Phase 0 — Gather context

Ask the user for:

1. **Project folder** — path to the design system project directory (contains
   `audit-results.json`, `tokens.json`, `components.json`, `design-system/`,
   `CLAUDE.md`).
2. **Run identifier** — a short slug for this run (e.g. `run1`, `run2`). Used
   to prefix the output file.
3. **Output folder** — where to write the output file. Default:
   `skill-outputs/<run-id>/` at the project root. Create it if it does not exist.

Read `CLAUDE.md`, the validator output (if captured), and any error messages
from the session for context.

---

## Phase 1 — Friction points document

Write `<run-id>-feedback-skill-design-system-extraction-code.md` to the output
folder.

### Format

```markdown
# design-system-extraction-code skill — problems encountered & proposed fixes

<one-paragraph intro: skill ran to completion against <input zip / target>,
validator result (e.g. "25/25 PASS"), phases completed. Then: "This document
enumerates every friction point hit along the way — schema confusion, tooling
gaps, unclear instructions, and silent traps — with concrete fix proposals
tagged by target:">

- **[skill]** — change the design-system-extraction-code skill instructions (SKILL.md)
- **[validator]** — change `scripts/validate-handoff.py`
- **[gen]** — prescribe or change the `gen.py` HTML generator approach
- **[figma]** — change Figma plugin template or instructions
- **[schema]** — change a JSON schema file

---

## <N>. <Issue title> — <CRITICAL | HIGH | MEDIUM | LOW>

**What happened.** <concrete description: what the skill said to do, what you
tried, exact error message or failure mode, how many turns it cost to work
around>

**Root cause.** <why it happened — schema design choice, missing documentation,
platform constraint, unclear instruction>

**Fix.**

- **[tag]** <concrete fix proposal — update the exact SKILL.md section, add the
  exact schema field, provide a code snippet or CLI invocation>

---
```

Repeat for every issue encountered. Number in order of impact (most disruptive
first). Severity label: CRITICAL = blocked the phase, required fundamental
redesign; HIGH = cost 3+ turns; MEDIUM = cost 1–2 turns or produced a wrong
artifact; LOW = minor confusion or documentation gap.

### Required final sections

After the last numbered issue, include these sections in order:

**Summary: issues by phase**

A markdown table with columns: Phase | Issue | Severity. One row per numbered
issue. Phase format: `<N> — <phase name>` (e.g. `2 — Tokens`, `4 — Docs site`,
`All`). Use "All" for cross-cutting issues not tied to a single phase. Order
rows by phase number, then by severity descending within each phase.

```markdown
## Summary: issues by phase

| Phase | Issue | Severity |
|-------|-------|----------|
| 0 — Entry | ... | High |
| 2 — Tokens | ... | **Critical** |
...
```

**Suggested skill directory structure after fixes**

A fenced directory tree showing the recommended layout after all proposed fixes
are applied. Include:
- `SKILL.md` (updated)
- `README.md`
- `schemas/` — updated schema files with any new fields from fixes
- `scripts/` — updated validator + any new helper scripts proposed
- `templates/` — `gen.py.template` (if generator was prescribed in fixes),
  `figma-plugin/` (updated templates), any new CSS/style templates
- `examples/` — this run's project folder as a working example

```
design-system-extraction-code/
├── SKILL.md
├── README.md
├── schemas/
│   ├── ...
├── scripts/
│   ├── ...
├── templates/
│   ├── ...
└── examples/
    └── <app-hostname>/
```

**For Claude Code: suggested order of fixes**

A numbered list prioritizing the issues to fix in the skill, ordered by
downstream impact. Format: `**#<N> (<short label>)** — <what to change and
where>`. End with: "All remaining medium/low items as a second pass."

---

## Output summary

After the phase completes, confirm:

- [ ] `<run-id>-feedback-skill-design-system-extraction-code.md` written

Tell the user the output file path. If any validator output or error log was
captured during the session, note whether it is referenced in the document.
