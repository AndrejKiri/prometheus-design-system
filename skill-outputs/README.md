# skill-outputs/

Archived outputs from AI skill runs against the Prometheus UI. Each run is a numbered subfolder that captures the full artifact set produced by a pair of skills: the visual UI audit ([design-system-extraction-cowork](../.claude/skills/)) and the design-token/component extraction ([design-system-extraction-code](../.claude/skills/)).

Runs are numbered sequentially. A run corresponds to one end-to-end execution of both skills against a specific target URL and commit of the Prometheus web UI.

## Contents

| Folder | Target URL | Date | Status |
|--------|-----------|------|--------|
| [run1/](run1/) | https://prometheus-e83j.onrender.com | 2026-04-21 | Complete |

## How a run is structured

Each run folder contains:

- **Raw skill output zips** — the files handed off by Cowork and Claude Code
- **Unpacked combined output** — the full artifact tree ready to browse locally or serve as a static site
- **Feedback documents** — post-run analysis of skill friction points and proposed fixes

See the README inside each run folder for artifact-level detail.
