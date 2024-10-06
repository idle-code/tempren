#!/usr/bin/bash
set -e

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ $CURRENT_BRANCH != release/* ]]; then
  echo "You have to be on release branch to finish the release"
  exit 1
fi

NEW_VERSION=$(poetry version --short)

pytest
mypy

git commit -a -m "Version v$NEW_VERSION"
git tag "v$NEW_VERSION"
git flow release finish


confirm() {
  QUESTION=$1
  read -rp  "$QUESTION (y/n): " RESPONSE
  case $RESPONSE in
      [Yy]* ) return 0;;
      [Nn]* ) return 1;;
      * ) echo "Please answer y or n." && confirm "$QUESTION" ;;
  esac
}

if confirm "Do you want to push the changes?"; then
  git push
  git push --tags
else
  echo "To publish:"
  echo "    git push && git push --tags"
fi
