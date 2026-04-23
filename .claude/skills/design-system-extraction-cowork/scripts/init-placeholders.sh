#!/usr/bin/env bash
# Created by design-system-apply-feedback from run1 feedback
# Creates 1x1 placeholder JPEGs at every screenshot path referenced in audit-results.json.
# Sets screenshots_are_placeholders: true in audit-results.json via Python.
#
# Usage: bash init-placeholders.sh <project-folder>

set -euo pipefail

PROJECT_DIR="${1:-.}"
AUDIT_FILE="$PROJECT_DIR/audit-results.json"
SCREENSHOTS_DIR="$PROJECT_DIR/screenshots"
PLACEHOLDER_SRC="$(dirname "$0")/placeholder.jpg"

if [ ! -f "$AUDIT_FILE" ]; then
  echo "ERROR: audit-results.json not found in $PROJECT_DIR"
  exit 1
fi

mkdir -p "$SCREENSHOTS_DIR"

# Extract all screenshot paths from audit-results.json and copy placeholder
python3 - "$AUDIT_FILE" "$SCREENSHOTS_DIR" "$PLACEHOLDER_SRC" <<'PYEOF'
import json, sys, shutil
from pathlib import Path

audit_path = Path(sys.argv[1])
screenshots_dir = Path(sys.argv[2])
placeholder = Path(sys.argv[3])

data = json.loads(audit_path.read_text())

paths = []
for page in data.get("pages_audited", []):
    if "screenshot" in page:
        paths.append(page["screenshot"])
    for ss in page.get("additional_screenshots", []):
        if "path" in ss:
            paths.append(ss["path"])

created = 0
for p in paths:
    # Strip leading screenshots/ prefix if present
    bare = p.removeprefix("screenshots/")
    dest = screenshots_dir / bare
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.stat().st_size < 500:
        shutil.copy2(placeholder, dest)
        created += 1
        print(f"  placeholder: {p}")

# Set screenshots_are_placeholders flag
data["screenshots_are_placeholders"] = True
audit_path.write_text(json.dumps(data, indent=2))

print(f"\nCreated {created} placeholder(s). Set screenshots_are_placeholders=true in audit-results.json.")
print("Claude Code Phase 1.5 will backfill real screenshots.")
PYEOF
