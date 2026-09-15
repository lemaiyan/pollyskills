#!/usr/bin/env python3
"""Validate every skill folder's SKILL.md frontmatter.

Walks the whole repo and treats any directory containing a SKILL.md as a
skill folder, so this doesn't care whether skills sit at the repo root or
under a platform folder like claude/. Checks, per skill folder:
- SKILL.md and README.md both exist
- SKILL.md starts with a YAML frontmatter block
- frontmatter has a non-empty `name` that matches the folder name
- frontmatter has a `description` long enough to plausibly trigger on
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIR_NAMES = {".git", "node_modules"}
MIN_DESCRIPTION_LEN = 20

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def find_skill_dirs(root):
    for skill_md in sorted(root.rglob("SKILL.md")):
        parents = skill_md.relative_to(root).parts[:-1]
        if any(part in SKIP_DIR_NAMES or part.startswith(".") for part in parents):
            continue
        yield skill_md.parent


def main():
    skill_dirs = list(find_skill_dirs(ROOT))

    if not skill_dirs:
        print("No skill folders found.")
        return 0

    errors = []

    for d in skill_dirs:
        rel = d.relative_to(ROOT)
        skill_md = d / "SKILL.md"
        readme = d / "README.md"

        if not readme.exists():
            errors.append(f"{rel}: missing README.md")

        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}/SKILL.md: missing or malformed YAML frontmatter")
            continue

        name = fm.get("name")
        description = fm.get("description")

        if not name:
            errors.append(f"{rel}/SKILL.md: frontmatter missing 'name'")
        elif name != d.name:
            errors.append(
                f"{rel}/SKILL.md: frontmatter name '{name}' "
                f"does not match folder name '{d.name}'"
            )

        if not description:
            errors.append(f"{rel}/SKILL.md: frontmatter missing 'description'")
        elif len(description) < MIN_DESCRIPTION_LEN:
            errors.append(
                f"{rel}/SKILL.md: 'description' looks too short to "
                f"trigger reliably ({len(description)} chars)"
            )

    if errors:
        print("Skill validation failed:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"All {len(skill_dirs)} skill folder(s) look valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
