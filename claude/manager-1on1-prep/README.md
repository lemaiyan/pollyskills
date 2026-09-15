# manager-1on1-prep

A Claude/Cowork skill that sets up a personal 1:1-prep automation for people
managers: it discovers your recurring 1:1s from your calendar, tracks open
action items sourced from your own (human-corrected) notes, and schedules
reminders before each 1:1 plus a weekly action-items review.

## What it does

Run the skill once in a conversation and it will:

1. Scan your calendar for recurring 1:1-shaped events and confirm the list
   of people with you.
2. Ask a handful of setup questions - where reminders should go (Slack DM,
   a new channel, email...), where the open-items tracker should live
   (Slack Canvas, a doc, etc.), whether to book a recurring "work through
   action items" block, and whether you use a notetaker tool (Granola,
   Otter, Fireflies, ...).
3. Stand up two recurring jobs:
  - **Daily** - drafts a note for any 1:1 that just happened (for you to
     review/correct, never auto-trusted), syncs the open-items tracker from
     your own corrected notes, reminds you a configurable number of days
     before each upcoming 1:1 of what's still open, and gives you a same-day
     briefing before each meeting.
  - **Weekly** - nudges you ahead of your recurring review block with a
     rollup of everything still open.

## Why the notetaker isn't trusted directly

AI notetakers are good but not perfect - they can mis-hear a name or guess
wrong about who owns a follow-up. This skill treats notetaker output as a
first draft only: it gets delivered to you for review, and the actual
tracker is only ever populated from your own notes once you've corrected and
saved them. This means there's a short lag between a meeting happening and
its action items showing up on the tracker - that's intentional, not a bug.

## Requirements

- A calendar connector (Google Calendar, Outlook, or similar) - required.
- A way to deliver reminders - Slack or email - required.
- A way to run recurring jobs without you present - in Claude/Cowork this is
  the built-in scheduled-task mechanism; elsewhere this could be cron, a
  scheduled GitHub Action, or your host's equivalent.
- Optional: a notes/docs connector (Google Drive, Notion, ...).
- Optional: a notetaker integration (Granola, Otter, Fireflies, ...).

## Installation

**Claude Code:** drop the `manager-1on1-prep/` folder into wherever your
Claude setup looks for skills (e.g. a project's `.claude/skills/`), or
install straight from the repo:

```bash
/plugin marketplace add lemaiyan/pollyskills
/plugin install manager-1on1-prep@pollyskills
```

**Claude.ai / Cowork:** upload the packaged `.skill` file via Skills in the
UI, if your org allows skill uploads. Grab a pre-built one from the
[latest release](https://github.com/lemaiyan/pollyskills/releases/latest),
or build it yourself with `scripts/package-skill.sh claude/manager-1on1-prep`
from the repo root.

Either way, once it's installed just ask Claude to set up your 1:1 prep -
the skill's description is written to trigger on natural phrasing like
"help me stay on top of my 1:1s" or "remind me what to bring up before my
1:1 with X."

## Limitations

- Whether notes can be auto-updated in an existing document depends entirely
  on what your connector supports - many Drive/Docs-style connectors can
  only create new files, not edit existing ones. The skill checks for this
  and falls back to delivering ready-to-paste text if editing isn't
  possible.
- Recurring-event detection on your calendar is a best-effort heuristic and
  gets confirmed with you before anything is built - it isn't perfect on
  irregularly-named events.
- This automates prep and tracking, not the conversation itself - it doesn't
  attend meetings or make management decisions for you.

## License

MIT - see the [repo license](../../LICENSE).
