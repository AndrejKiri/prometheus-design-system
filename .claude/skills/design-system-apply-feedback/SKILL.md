---
name: design-system-apply-feedback
description: >
  Takes feedback documents from a completed run and applies the fix proposals
  directly to the design-system-extraction-cowork and design-system-extraction-code
  skills. Reads [skill], [validator], [schema], [gen], and [figma] tagged fixes
  from the wrapup documents, edits the target files, bumps version metadata,
  rebuilds the skill zips, and commits the changes. Closes the self-improvement
  loop: run → wrapup → apply-feedback → improved skill → next run.
metadata:
  author: AndrejKiri
  version: '0.2'
  reference-implementation: https://github.com/AndrejKiri/prometheus-design-system
  depends-on:
    - design-system-extraction-cowork-wrapup
    - design-system-extraction-code-wrapup
---

# Design System Apply Feedback

Run this skill after both wrapup skills have produced their feedback documents
for a given run. It reads every tagged fix proposal and applies it to the live
skill files, then commits the result so the next run starts from an improved
baseline.

---

## Tag → file mapping

Every fix proposal in the feedback documents is tagged. Use this table to
determine which file to edit:

| Tag | Source | Target file(s) |
|-----|--------|---------------|
| `[skill]` in cowork feedback | cowork wrapup doc | `design-system-extraction-cowork/SKILL.md` |
| `[skill]` in code feedback | code wrapup doc | `design-system-extraction-code/SKILL.md` |
| `[validator]` in cowork feedback | cowork wrapup doc | `design-system-extraction-cowork/scripts/validate-handoff.py` |
| `[validator]` in code feedback | code wrapup doc | `design-system-extraction-code/scripts/validate-handoff.py` |
| `[schema]` | code wrapup doc | `design-system-extraction-code/schemas/<named schema>.json` |
| `[gen]` | code wrapup doc | `design-system-extraction-code/templates/gen.py.template` (create if missing) |
| `[figma]` | code wrapup doc | `design-system-extraction-code/templates/figma-plugin/code.js.template` or `manifest.json.template` |
| `[handoff-to-cc]` | cowork wrapup doc | `design-system-extraction-cowork/SKILL.md` (add Phase 1.5 section) |
| `[cowork]` | cowork wrapup doc | Flag as out of scope — document in a `KNOWN-LIMITATIONS.md` file in the cowork skill dir, do not attempt to fix in the skill |

All skill files are at `.claude/skills/<skill-name>/` relative to the project root.

---

## Phase 0 — Gather context

Ask the user for:

1. **Run identifier** — the run whose feedback to apply (e.g. `run1`). Used to
   locate the feedback documents.
2. **Feedback folder** — path to the folder containing the wrapup docs. Default:
   `skill-outputs/<run-id>/`.
3. **Which feedback to apply** — `both` (default), `cowork-only`, or
   `code-only`.
4. **Priority filter** — `critical-and-high` (default), `all`, or a comma-
   separated list of issue numbers (e.g. `1,2,5`). Applied independently to
   each feedback document.

Confirm with the user before making any edits.

---

## Phase 1 — Read and triage feedback

Read both feedback documents from the feedback folder:
- `<run-id>-feedback-skill-design-system-extraction-cowork.md`
- `<run-id>-feedback-skill-design-system-extraction-code.md`

For each document, extract every numbered section. For each issue:
- Extract: issue number, title, severity, fix proposals (one or more `[tag]`
  bullets under **Fix.**).
- Determine the target file from the tag → file mapping above.
- Apply the priority filter. Skip issues that don't pass.

Present the user with a triage table before making any edits:

```
COWORK FEEDBACK — applying N of M issues
  #1  [skill]      CRITICAL  <title>   → design-system-extraction-cowork/SKILL.md
  #2  [handoff-to-cc] HIGH   <title>   → design-system-extraction-cowork/SKILL.md
  #3  [validator]  HIGH      <title>   → design-system-extraction-cowork/scripts/validate-handoff.py
  (skipped: #4 MEDIUM, #5 LOW — below priority filter)

CODE FEEDBACK — applying N of M issues
  #1  [skill]      CRITICAL  <title>   → design-system-extraction-code/SKILL.md
  #2  [skill]      HIGH      <title>   → design-system-extraction-code/SKILL.md
  #3  [validator]  HIGH      <title>   → design-system-extraction-code/scripts/validate-handoff.py
  #4  [schema]     MEDIUM    <title>   → design-system-extraction-code/schemas/tokens.schema.json
  (skipped: #5 LOW — below priority filter)
```

Wait for the user to confirm or adjust before proceeding.

---

## Phase 2 — Apply fixes

Work through the triaged list in order. For each fix:

### Editing existing files

Read the target file first. Apply the fix as described — add the section,
update the instruction, add the code snippet, add the schema field, etc.
Follow these rules:

- **SKILL.md edits:** insert new content at the location described in the fix
  (e.g., "add to Phase 2's typography section", "add a Gotchas section before
  Handoff"). Do not remove existing content unless the fix explicitly says to
  replace something. Preserve section order.
- **Validator edits:** add the check as a new block in the appropriate section
  of `validate-handoff.py`. Preserve existing checks. Add a comment above the
  new block referencing the issue number: `# Fix: issue #N from <run-id>`.
- **Schema edits:** add the new field at the location described. Preserve
  existing required/optional field lists.
- **Template edits:** add the snippet at the described location.

### Creating new files

If a fix requires a file that does not yet exist (e.g., a new script, a new
vocabulary file, `gen.py.template`), create it with the content described in
the fix. Place it in the directory specified in the tag → file mapping, or the
directory named in the fix proposal.

For new scripts, add an executable header:
```python
#!/usr/bin/env python3
# Created by design-system-apply-feedback from <run-id> feedback
```

### Handling `[cowork]` tags

Do not attempt to modify Cowork's sandbox. Instead, append to
`design-system-extraction-cowork/KNOWN-LIMITATIONS.md` (create if it does not
exist):

```markdown
## <Issue title>

**Source:** <run-id> feedback, issue #N
**Description:** <root cause from the feedback doc>
**Status:** Out of scope for skill-level fix — requires Cowork platform change.
**Workaround:** <the [handoff-to-cc] or [skill] workaround from the same issue, if one exists>
```

### After each file edit

Commit the change immediately. Do not batch. Commit message format:
```
fix(<skill-short-name>): <issue title, max 50 chars>

From <run-id> feedback issue #N. Severity: <CRITICAL|HIGH|MEDIUM|LOW>.
```

Where `<skill-short-name>` is `cowork` or `code`.

---

## Phase 3 — Bump version and rebuild zips

This phase is **mandatory** whenever Phase 2 touched at least one skill. Do not
skip it, even if only a single file was edited.

For **every skill that had any fix applied** (including `KNOWN-LIMITATIONS.md`
appends and template/script/schema additions), run these steps:

1. **Bump the patch version** in the skill's `SKILL.md` frontmatter.
   - Default: always **patch bump** (e.g. `0.1` → `0.2`, `0.2` → `0.3`).
   - Use semantic form `'<major>.<minor>'` in the YAML frontmatter.
   - Only do a minor/major bump if the user explicitly requests it.

2. **Rebuild the zip** at `.claude/skills/<skill-name>-v<new-version>.zip`.
   Remove the old version zip if the version number changed. The zip should
   contain the full skill directory:
   ```bash
   cd .claude/skills
   rm -f <skill-name>-v<old-version>.zip
   zip -r <skill-name>-v<new-version>.zip <skill-name>/
   ```

3. **Commit** the version bump and new zip together:
   ```
   chore(<skill-short-name>): bump to v<new-version> after <run-id> fixes
   ```

Apply steps 1–3 to each modified skill independently. If a run touched both
the cowork and code skills, both get a version bump and a fresh zip.

---

## Phase 4 — Summary

After all skills are updated, output a summary:

```
Applied fixes from <run-id>:

design-system-extraction-cowork  v<old> → v<new>
  ✓ #1 [skill] CRITICAL  <title>
  ✓ #2 [handoff-to-cc] HIGH  <title>
  ✓ #3 [validator] HIGH  <title>
  — #4 [cowork] MEDIUM  <title>  (logged to KNOWN-LIMITATIONS.md)
  ○ #5 LOW  (below filter, skipped)

design-system-extraction-code    v<old> → v<new>
  ✓ #1 [skill] CRITICAL  <title>
  ✓ #2 [skill] HIGH  <title>
  ✓ #3 [validator] HIGH  <title>
  ✓ #4 [schema] MEDIUM  <title>
  ○ #5 LOW  (below filter, skipped)

New zips:
  .claude/skills/design-system-extraction-cowork-v<new>.zip
  .claude/skills/design-system-extraction-code-v<new>.zip

Skipped issues are still in the feedback docs — run this skill again with
priority filter "all" or a specific issue list to apply them.
```
