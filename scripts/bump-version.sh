#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
VERSION_FILE="$REPO/VERSION"

OLD=$(tr -d '[:space:]' < "$VERSION_FILE")
IFS='.' read -r major minor patch <<< "$OLD"
NEW="$major.$minor.$((patch + 1))"

echo "$NEW" > "$VERSION_FILE"

# Replace version string in all HTML files
find "$REPO" -name "*.html" -exec sed -i "s/v${OLD}/v${NEW}/g" {} +

cd "$REPO"
git add VERSION
git add $(find . -name "*.html" | sed 's|^\./||')
git commit -m "chore: bump version to v$NEW"

echo "Bumped $OLD → $NEW"
