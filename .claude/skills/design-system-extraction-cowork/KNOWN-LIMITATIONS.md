# Known Limitations — design-system-extraction-cowork

Issues that require Cowork platform changes and cannot be fixed at the skill level.

---

## save_to_disk returns opaque ID, not a filesystem path

**Source:** run1 feedback, issue #2
**Description:** `mcp__Claude_in_Chrome__computer` with `action: screenshot, save_to_disk: true` returns an ID like `"ss_01JDV9X7…"` with no `path` field. The file is not accessible anywhere in the sandbox filesystem (`/tmp`, `/home`, `/sessions/…`). The ID is a Cowork-internal handle only.
**Status:** Out of scope for skill-level fix — requires Cowork platform change (expose filesystem path in tool result, or add a `get_saved_screenshot(id)` companion tool that returns path + bytes).
**Workaround:** Use the Playwright capture script in Phase 1.5 (`scripts/capture-screenshots.mjs`) instead of `save_to_disk`. Do not use `save_to_disk` as a primary capture mechanism.

---

## Browser-side base64 payloads are filtered from javascript_tool responses

**Source:** run2 feedback, issue #1
**Description:** Round-tripping screenshot bytes via `canvas.toDataURL()` or any other base64 payload through `mcp__Claude_in_Chrome__javascript_tool` is filtered out of the response before it reaches the model. Combined with the `save_to_disk` opaque-ID limitation above, there is no path inside Cowork to land a JPEG on the user's disk.
**Status:** Out of scope for skill-level fix — requires Cowork platform change (either lift the base64 filter, or expose a "save browser screenshot to workspace file" primitive).
**Workaround:** Phase 1 in Cowork is now Degraded Screenshot Mode by default — emit 1×1 placeholders + rich DOM observations + `additional_screenshots[].state` keys, and let Claude Code's Phase 1.5 backfill real images via Playwright.
