#!/usr/bin/bash
set -e
BUMP_RULE=$1
if [ -z "$BUMP_RULE" ]; then
  echo "Please specify bump rule: major, minor or patch"
  exit 1
fi

OLD_VERSION=$(poetry version --short)
poetry version $BUMP_RULE
NEW_VERSION=$(poetry version --short)

git commit -a -m "Version v$NEW_VERSION"
git tag "v$NEW_VERSION"

echo "To publish:"
echo "    git push && git push --tags"
