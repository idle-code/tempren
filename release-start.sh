#!/usr/bin/bash
set -e

BUMP_RULE=$1
if [ -z "$BUMP_RULE" ]; then
  echo "Please specify bump rule: major, minor or patch"
  exit 1
fi

NEXT_VERSION=$(poetry version --dry-run --short "$BUMP_RULE")

git flow release start "v$NEXT_VERSION"
poetry version "$BUMP_RULE"
git commit -a -m "Version updated to v$NEXT_VERSION"

echo "Type release-finish.sh to make the release"
