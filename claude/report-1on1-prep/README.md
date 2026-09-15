# report-1on1-prep

A Claude/Cowork skill that sets up a personal 1:1-prep automation for anyone
preparing for their *own* recurring 1:1 with their manager - the mirror
image of a manager-side tracker, for the report rather than the manager. It
discovers your recurring 1:1 from your calendar, keeps a running agenda of
things you want to raise plus open follow-ups on both sides, and reminds you
before each 1:1 what's on it.

## What it does

Run the skill once in a conversation and it will:

1. Scan your calendar for a recurring 1:1-shaped event with your manager
   (and confirm it, rather than just asking you who your manager is) -
   including a check for a second tracked relationship if you're in a
   matrixed org with more than one.
2. Ask a handful of setup questions - where reminders should go (Slack DM, a
   new channel, email...), where your running agenda/tracker should live,
   whether you want it split into "things to raise" / "I owe them" / "they
   owe me" or kept as one simple list, whether you can add to the agenda
   anytime (not just around a meeting), and whether you use a notetaker tool
   (Granola, Otter, Fireflies, ...).
3. Stand up a recurring job that: drafts a note for any 1:1 that just
   happened (for you to review/correct, never auto-trusted), syncs your
   agenda/tracker from your own corrected notes, reminds you a configurable
   number of days before each upcoming 1:1 of what's on it, and gives you a
   same-day briefing before each meeting.

## Why the notetaker isn't trusted directly

AI notetakers are good but not perfect - they can mis-hear a name, a date, or
guess wrong about who committed to what. This skill treats notetaker output
as a first draft only: it gets delivered to you for review, and your actual
agenda/tracker is only ever populated from your own notes once you've
corrected and saved them. This means there's a short lag between a meeting
happening and anything new showing up on the tracker - that's intentional,
not a bug, and matters here for the same reason it matters on the manager
side: an unreviewed misattribution ("my manager promised X") that goes
straight into your record of the relationship is worse than a one-time
transcription slip you'd normally just re-read and fix.

## Requirements

- A calendar connector (Google Calendar, Outlook, or similar) - required.
- A way to deliver reminders - Slack or email - required.
- A way to run a recurring job without you present, if you want this
  automated rather than run on demand - in Claude/Cowork this is the
  built-in scheduled-task mechanism; elsewhere this could be cron, a
  scheduled GitHub Action, or your host's equivalent.
- Optional: a notes/docs connector (Google Drive, Notion, ...).
- Optional: a notetaker integration (Granola, Otter, Fireflies, ...).

## Installation

**Claude Code:** drop the `report-1on1-prep/` folder into wherever your
Claude setup looks for skills (e.g. a project's `.claude/skills/`), or
install straight from the repo:

```bash
/plugin marketplace add lemaiyan/pollyskills
/plugin install report-1on1-prep@pollyskills
```

**Claude.ai / Cowork:** upload the packaged `.skill` file via Skills in the
UI, if your org allows skill uploads. Grab a pre-built one from the
[latest release](https://github.com/lemaiyan/pollyskills/releases/latest),
or build it yourself with `scripts/package-skill.sh claude/report-1on1-prep`
from the repo root.

Either way, once it's installed just ask Claude to help you prep for your
1:1s - the skill's description is written to trigger on natural phrasing
like "help me prep for my 1:1 with my manager" or "remind me what I wanted
to bring up next time."

## Relationship to manager-1on1-prep

This is the complementary, opposite-direction skill to `manager-1on1-prep`
(which is for a manager tracking action items across multiple reports). If
someone wants to track what *their reports* owe *them*, point them at that
skill instead - the two are designed to coexist (a manager could use one for
their reports and the other for their own 1:1 with their boss) but shouldn't
be merged, since the framing and the tracked categories genuinely differ.

## Limitations

- Whether notes can be auto-updated in an existing document depends entirely
  on what your connector supports - many Drive/Docs-style connectors can
  only create new files, not edit existing ones. The skill checks for this
  and falls back to delivering ready-to-paste text if editing isn't
  possible.
- Recurring-event detection on your calendar is a best-effort heuristic and
  gets confirmed with you before anything is built - it isn't perfect on
  irregularly-named events, and it won't guess which of two similar-looking
  meetings is really your manager 1:1 without asking.
- This automates prep and tracking, not the conversation itself - it doesn't
  attend the meeting or negotiate on your behalf.

## License

MIT - see the [repo license](../../LICENSE).
