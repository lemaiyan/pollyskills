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

## Commit messages and releases

Releases are handled by [release-please](https://github.com/googleapis/release-please) (`.github/workflows/release-please.yml`), which reads
[Conventional Commits](https://www.conventionalcommits.org/) to figure out
the next version and changelog. First line of the commit message is
`<prefix>: <summary>`:

| Prefix | Effect | Example |
|---|---|---|
| `fix:` | patch bump (0.1.0 -> 0.1.1) | `fix: correct broken LICENSE link in skill READMEs` |
| `feat:` | minor bump (0.1.0 -> 0.2.0) | `feat: add chatgpt platform folder` |
| `feat!:` or a `BREAKING CHANGE:` footer | major bump (0.1.0 -> 1.0.0) | `feat!: restructure skill folder layout` |
| `chore:`, `docs:`, `refactor:`, `style:`, `test:`, `ci:` | no version bump, still listed in the changelog | `docs: clarify installation steps` |

Scoping is optional, e.g. `fix(readme): ...`, if you want to be more specific.

Every push to `main` updates (or opens) a "chore: release X.Y.Z" PR that
accumulates the changelog. Merging that PR is what actually cuts the
release: release-please tags it and publishes the GitHub release, then a
second job in the same workflow validates every `SKILL.md`, packages all
skills into `.skill` files, and attaches them to that release - no manual
tagging or `gh release create` needed.

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
