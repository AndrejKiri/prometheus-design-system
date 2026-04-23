# Known Limitations — design-system-extraction-cowork

Issues that require Cowork platform changes and cannot be fixed at the skill level.

---

## save_to_disk returns opaque ID, not a filesystem path

**Source:** run1 feedback, issue #2
**Description:** `mcp__Claude_in_Chrome__computer` with `action: screenshot, save_to_disk: true` returns an ID like `"ss_01JDV9X7…"` with no `path` field. The file is not accessible anywhere in the sandbox filesystem (`/tmp`, `/home`, `/sessions/…`). The ID is a Cowork-internal handle only.
**Status:** Out of scope for skill-level fix — requires Cowork platform change (expose filesystem path in tool result, or add a `get_saved_screenshot(id)` companion tool that returns path + bytes).
**Workaround:** Use the Playwright capture script in Phase 1.5 (`scripts/capture-screenshots.mjs`) instead of `save_to_disk`. Do not use `save_to_disk` as a primary capture mechanism.
