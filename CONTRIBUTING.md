# Contributing

Found a bug, ported a skill to another platform, or built something that
improves on one of these? Open a PR, or open an issue if you just want to
flag something.

## Adding or changing a skill

- Skills are grouped by platform in a top-level folder - [`claude/`](./claude)
  today, one folder per platform as others get added (e.g. a future
  `chatgpt/`). Each skill then lives in its own folder under that: a
  `README.md` (what it does, requirements, installation, limitations), a
  `SKILL.md` (the actual instructions the assistant follows), and an
  optional `references/` folder for supporting material.
- A Claude skill folder also carries a `.claude-plugin/plugin.json` (name,
  description, version, author) so it can be installed straight from this
  repo as a Claude Code plugin - see the root
  [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json),
  which needs a new entry for every skill you add.
- Keep a skill's `README.md` and `SKILL.md` in sync - the README is for
  humans deciding whether to install it, the SKILL.md is what the assistant
  reads.
- Porting a skill to a new platform entirely (not just tweaking an existing
  one)? Give it its own top-level folder, same shape as `claude/`, and note
  in the README what's platform-specific (scheduled tasks, connectors, etc.)
  versus portable as plain instructions.
- New skill folders should get a row in the relevant platform's table in the
  root [README.md](./README.md).
- `SKILL.md`'s frontmatter `name` must match its folder name, and
  `description` needs to be long/specific enough to actually trigger on. CI
  checks this (`scripts/validate_skills.py`) - run it locally before opening
  a PR:

  ```bash
  python3 scripts/validate_skills.py
  ```
- No other build step and no tests to run - these are instructions for
  Claude, not code. Read through your changes as if you were Claude
  following them cold, and check any example phrasing you include actually
  reads naturally.
- If you want to try installing your change as a packaged skill (the
  Cowork/Claude.ai upload path), build one with:

  ```bash
  scripts/package-skill.sh <skill-folder>   # or --all
  ```

  Output lands in `dist/`, which is gitignored - don't commit `.skill` files.

## Cutting a release

Pushing a tag like `v0.2.0` triggers `.github/workflows/release.yml`, which
validates every `SKILL.md`, packages all skills into `.skill` files, and
publishes a GitHub release with them attached - no manual `gh release
create` needed:

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Pull requests

- Keep PRs scoped to one skill (or the shared repo files) at a time where
  possible, it makes them easier to review.
- Describe what changed and why in the PR description; that's more useful
  here than a commit-by-commit history.
- The PR template has a short checklist - it's there as a reminder, not a
  gate.

## License

By contributing, you agree your contribution is licensed under the repo's
[MIT license](./LICENSE).
