# pollyskills

A growing collection of AI assistant skills I've built for my own day-to-day work and use daily. Organized by platform - each skill lives in its own folder with its own README and SKILL.md, install them individually, you don't need the whole repo.

## Skills

### Claude

| Skill | What it does |
|---|---|
| [`claude/manager-1on1-prep/`](./claude/manager-1on1-prep) | Runs 1:1 prep for a people manager, tracks open action items per report, reminds you before each 1:1, rolls up outstanding items before a weekly review. |
| [`claude/report-1on1-prep/`](./claude/report-1on1-prep) | Mirror image, for your own 1:1 with your manager (or two, if you're matrixed). Keeps a running agenda of what to raise and what's owed on both sides. |

More to come, for Claude and other platforms, as I build them. Writeups for individual skills, including the reasoning behind specific design decisions, get published at [blog.georgekamunya.com](https://blog.georgekamunya.com).

## Installing a skill

**Claude Code**, the fastest way - add this repo as a plugin marketplace and install straight from it:

```bash
/plugin marketplace add lemaiyan/pollyskills
/plugin install manager-1on1-prep@pollyskills
```

Or the manual way, which works anywhere Claude Code looks for skills:

1. Clone this repo, or just download the folder for the skill you want.
2. Drop it into a project's `.claude/skills/` directory (or `~/.claude/skills/` for a user-level install).
3. Ask Claude naturally to set it up, each skill's README has example phrasing.
4. Answer whatever setup questions it asks you.

**Claude.ai / Cowork** - these need a packaged `.skill` file rather than a raw folder:

```bash
scripts/package-skill.sh claude/manager-1on1-prep   # or --all
```

Upload the resulting file from `dist/` via Skills in the UI, if your org allows skill uploads.

## Platform

Skills are grouped by the assistant they're built for - currently just [`claude/`](./claude). A skill folder's own README notes what's platform-specific (scheduled-task mechanisms, connector integrations) versus portable as plain instructions elsewhere. Porting a skill to another platform (ChatGPT, Gemini, ...)? It gets its own top-level folder, same shape as `claude/`.

## Contributing

Found a bug, ported a skill to another platform, or built something that improves on one of these? Open a PR, or open an issue if you just want to flag something. I read both. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the structure a new skill should follow.

## License

MIT - see [LICENSE](./LICENSE). Applies to every skill in this repo unless a skill's own folder says otherwise.
