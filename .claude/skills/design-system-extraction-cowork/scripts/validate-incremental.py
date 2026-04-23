#!/usr/bin/env python3
# Created by design-system-apply-feedback from run1 feedback
"""
Incremental Validator — audit-results.json only
================================================
Use during Phase 1 to validate audit-results.json in isolation, without
needing tokens.json or components.json to exist yet.

Delegates to validate-handoff.py --partial so all audit checks are identical
to the full validator; the only difference is that missing optional files are
silently skipped instead of generating a warning.

Usage:
    python validate-incremental.py <project-directory>

Exit codes:
    0 = audit-results.json passes all checks
    1 = one or more checks failed
    2 = audit-results.json not found or invalid JSON
"""

import subprocess
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-incremental.py <project-directory>")
        sys.exit(2)

    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.is_dir():
        print(f"Error: '{project_dir}' is not a directory")
        sys.exit(2)

    full_validator = Path(__file__).parent / "validate-handoff.py"
    result = subprocess.run(
        [sys.executable, str(full_validator), str(project_dir), "--partial"],
        check=False,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
