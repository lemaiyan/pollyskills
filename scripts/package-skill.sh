#!/usr/bin/env bash
# Package a skill folder into a .skill file (a zip archive with SKILL.md at
# its root) for upload to Claude.ai / Cowork.
#
# Usage:
#   scripts/package-skill.sh <skill-folder>   # e.g. manager-1on1-prep
#   scripts/package-skill.sh --all            # package every skill in the repo
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$REPO_ROOT/dist"

package_one() {
  local skill_dir="${1%/}"
  local name
  name="$(basename "$skill_dir")"

  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "error: $skill_dir/SKILL.md not found, skipping" >&2
    return 1
  fi

  mkdir -p "$OUT_DIR"
  local out="$OUT_DIR/$name.skill"
  rm -f "$out"

  # README.md is for the repo/GitHub, .claude-plugin/ is Claude Code plugin
  # metadata - neither belongs in a Claude.ai/Cowork .skill upload.
  ( cd "$skill_dir" && zip -rq -X "$out" . -x "README.md" -x ".claude-plugin/*" )
  echo "Wrote $(realpath --relative-to="$REPO_ROOT" "$out" 2>/dev/null || echo "$out")"
}

if [ $# -ne 1 ]; then
  echo "Usage: $0 <skill-folder> | --all" >&2
  exit 1
fi

if [ "$1" = "--all" ]; then
  found=0
  while IFS= read -r -d '' skill_md; do
    package_one "$(dirname "$skill_md")"
    found=1
  done < <(find "$REPO_ROOT" -not -path '*/.git/*' -name 'SKILL.md' -print0)
  if [ "$found" -eq 0 ]; then
    echo "No skill folders (containing SKILL.md) found." >&2
    exit 1
  fi
else
  package_one "$1"
fi
