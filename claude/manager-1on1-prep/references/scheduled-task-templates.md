# Scheduled job templates

These are starting points, not fill-in-the-blank forms to apply mechanically.
Adapt the wording to what was actually discovered/decided during setup, but
keep the structure: each job must be fully self-contained, since it typically
runs in a fresh context with no memory of the setup conversation.

Before scheduling any of these, actually exercise every tool call they
reference (a real, low-stakes call to each connector) during the setup
conversation itself. Some environments require an interactive permission
grant the first time a connector/tool is used - a scheduled job firing
unattended can't click through that prompt, so the grant needs to already
be in place before the first real firing, not discovered by it failing.

Placeholders used below (replace all of them - a template with a placeholder
still in it will fail or, worse, silently do nothing useful):

- `{{USER_NAME}}` - the manager this is set up for
- `{{TIMEZONE}}` - IANA timezone, e.g. `America/New_York`
- `{{DELIVERY_CHANNEL}}` - where reminders/notes get posted (a Slack channel
  ID, "DM", an email address, etc.)
- `{{TRACKER_LOCATION}}` - the checklist/tracker surface and its ID/link
- `{{DRAFT_QUEUE_LOCATION}}` - only used if drafts are staged in a canvas
  (or similar) rather than posted directly to chat - see "Where drafts get
  delivered" below. Omit entirely if not using this pattern.
- `{{PERSON_NAME}}` / `{{PERSON_MEETING_TITLE}}` / `{{PERSON_SCHEDULE}}` /
  `{{PERSON_DOC_LINK}}` - the specifics for one tracked 1:1 (used in the
  per-person notes-capture job, one instance of this job per person)
- `{{PEOPLE_LIST}}` - for each discovered 1:1: name, contact info, notes-doc
  link (if any), and how their meetings are identified in the calendar/
  notetaker (exact title pattern) - used in the shared daily/weekly jobs
- `{{PEOPLE_SHORT_NAMES}}` - just the first names/short names from
  `{{PEOPLE_LIST}}`, for a compact one-line mention (used in the weekly job)
- `{{NOTETAKER_TOOL}}` - name of the notetaker integration, or "none" if the
  user doesn't use one
- `{{LEAD_DAYS}}` - how many days before a 1:1 the heads-up reminder fires
  (default 2)
- `{{REVIEW_BLOCK}}` - day/time of the recurring review block, or "none" if
  the user opted out of one

## Where drafts get delivered

Two options, pick based on delivery channel:

- **Direct message.** Simplest - the per-person job posts the formatted note
  straight to `{{DELIVERY_CHANNEL}}`. Fine for email or a low-traffic
  channel.
- **Staging canvas (Slack).** Create one canvas with a section per tracked
  person, each holding only the *latest* unreviewed draft. Each per-person
  job overwrites (not appends to) its own section, then posts a short
  pointer message to `{{DELIVERY_CHANNEL}}` instead of the full text. This
  keeps the channel scannable when there are several reports generating
  notes on different days, since the channel never accumulates full note
  dumps - only short "ready for review" pointers. The per-person job template
  below shows both variants inline; delete whichever wasn't chosen.

## Per-person notes-capture job

**One of these per tracked 1:1 on the notetaker or handwritten pattern** -
do not combine multiple people into one job, and do NOT create this job at
all for someone on the self-typed-doc pattern (their doc has no
time-sensitive artifact to poll for; the shared daily job's tracker sync
covers them completely on its own - see SKILL.md Step 7a). For everyone
else, see SKILL.md Step 7a for why one job per person: a single shared daily
job can miss same-day notes by up to 24 hours if the meeting happens later
in the day than the job's own run time. Each instance fires ~15-20 minutes
after that specific person's meeting is expected to end.

```
You are running {{USER_NAME}}'s post-1:1 notes-capture check for their 1:1
with {{PERSON_NAME}}. This fires [weekly/biweekly], ~20 minutes after this
specific 1:1's usual end time - act autonomously, do not ask questions, just
do the work below.

[If using the staging-canvas delivery pattern:]
The full draft note goes into the shared staging canvas
({{DRAFT_QUEUE_LOCATION}}) - NOT directly into chat. Only a short pointer
message goes into {{DELIVERY_CHANNEL}}.
[If posting directly instead, say so plainly and skip the canvas steps below.]

Figure out today's real date/time yourself ({{USER_NAME}} is in
{{TIMEZONE}}). This 1:1 ("{{PERSON_MEETING_TITLE}}") normally runs
{{PERSON_SCHEDULE}}. [If biweekly/irregular:] It happens every other week, so
on an off week the calendar will show no meeting today - that's expected,
not an error, just stop silently in that case.

STEP 1 - CONFIRM TODAY'S MEETING ACTUALLY HAPPENED. Check the calendar for a
"{{PERSON_MEETING_TITLE}}" event today. If there's no such event today, stop
here and post nothing.

STEP 2 - CHECK IF ALREADY POSTED TODAY. [Canvas variant:] Read the staging
canvas and find {{PERSON_NAME}}'s current section content. If it already
shows today's date, stop - already posted today, don't repost. [Direct
variant:] Check recent channel history for a note posted today for this
person; if found, stop.

STEP 3 - GET THE NOTE. This job only exists for the notetaker and
handwritten patterns (see above) - which of these applies was decided during
setup (SKILL.md Step 2):

[Notetaker variant:] Search {{NOTETAKER_TOOL}} for a note matching
"{{PERSON_MEETING_TITLE}}" dated today. If none exists yet, post one short
message: "Still waiting on {{NOTETAKER_TOOL}}'s note for today's 1:1 with
{{PERSON_NAME}} - I'll check again on the next sync." and stop. Do not
fabricate content.

[Handwritten / no digital notes variant - user takes notes on paper, in a
personal app, or just remembers:] Post a short direct question ONCE: "How'd
the 1:1 with {{PERSON_NAME}} go today? Anything to flag or follow up on?"
Then stop - do not have this job poll for the reply. This job won't fire
again until {{PERSON_NAME}}'s next 1:1 (a week or two away), which is far
too slow to catch an answer. Checking for and consuming the reply is the
shared daily job's task instead (see "Shared daily job" below) - it already
runs every day, which is the cadence this actually needs.

STEP 4 - FORMAT AND DELIVER. [Notetaker variant only - the handwritten
variant has nothing left to do after Step 3 posted its question; stop
there.] If a matching note exists, reformat it using the notetaker-formatting
template (below, or the user's own established prompt if they have one -
use their exact wording, don't paraphrase it).

[Canvas variant:] Call the canvas-update tool with a "replace" edit on
{{PERSON_NAME}}'s section only (re-read the canvas first to get a fresh
section ID if more than a few seconds have passed since Step 2 - section IDs
can change after every edit). Then post ONE short pointer message to
{{DELIVERY_CHANNEL}}: "📝 Draft notes from {{USER_NAME}}'s 1:1 with
{{PERSON_NAME}} today are ready for review: {{DRAFT_QUEUE_LOCATION}} -
review/correct names & owners there, then paste into the doc:
{{PERSON_DOC_LINK}}." Do NOT paste the note content into the chat message
itself.

[Direct variant:] Post the full formatted note to {{DELIVERY_CHANNEL}} with
an intro like "Draft notes from your 1:1 with {{PERSON_NAME}} - review/
correct names & owners, then save into your notes: {{PERSON_DOC_LINK}}."

Do NOT add anything to {{TRACKER_LOCATION}} in this step - the tracker only
ever gets populated from {{USER_NAME}}'s own corrected notes, via the
separate daily sync job, never from the raw notetaker output. (The
handwritten variant doesn't reach Step 4 at all - it stops after posting its
question in Step 3. The daily job below is what consumes the reply.)
```

## Shared daily job (sync + reminders)

Fires once a day, ideally early morning in `{{TIMEZONE}}`. Handles everyone,
for the three things that are fine as a once-a-day batch (unlike
notes-capture - see Step 7a/7c in SKILL.md for why those are split out into
the per-person jobs above instead of being Step 1 of this job).

```
You are running {{USER_NAME}}'s daily 1:1 tracker-sync and reminder check.
This is a recurring, unattended automation - act autonomously, do not ask
questions, just perform the work described below and send messages as
specified.

NOTE: capturing a draft note right after each 1:1 is handled by separate,
person-specific jobs (each firing ~20 minutes after that person's usual 1:1
end time), not by this job. This job only does the three steps below.

{{USER_NAME}}'s timezone is {{TIMEZONE}}. Figure out today's real date/time
yourself before starting.

Deliver all messages to: {{DELIVERY_CHANNEL}}.

{{USER_NAME}} has recurring 1:1s with these people. For each: identity, how
their meetings are identified on the calendar, and where their notes live.

{{PEOPLE_LIST}}

[If a notetaker is in use, include this paragraph:]
The notes doc for each person is manually maintained by {{USER_NAME}}: they
take the {{NOTETAKER_TOOL}} draft (delivered by the per-person jobs above),
review and correct it (fixing any transcription errors - wrong names,
misattributed owners, etc.), then save their corrected version. Because of
that correction step, the DOC is the trustworthy record - never
{{NOTETAKER_TOOL}}'s raw output. {{NOTETAKER_TOOL}} is only ever used
upstream to produce a first-draft note; it is never used here to decide who
owns what action item.

STEP 1 - SYNC THE TRACKER FROM THE USER'S OWN NOTES (the only source for
tracker content; run this every day regardless of whether a meeting happened
today). For each person: open their notes doc (or whatever the notes source
is) and find the most recent DATED entry that actually has real content -
skip over a future-dated placeholder/stub some notes docs get pre-created
with ahead of the next meeting; that's not a real 1:1 yet. Compare it against
what's already on the tracker for that person (e.g. by date tag). If there's
new content not yet reflected, read the WHOLE entry - don't limit the search
to a literally-labeled "Action items" or "Next Steps" list. Plenty of real
notes docs don't use that heading at all, or leave it blank/near-empty while
the actual ask is answered inline somewhere else in the entry - a very common
spot is a Q&A-style template's "what's one thing I can do to support you?" or
"anything you need from me?" question, where the other person's answer
("approve my leave," "ease up on meeting frequency for a bit," etc.) is just
as real an action item as one under a formal heading, only phrased
conversationally. Read the full entry and use judgment to infer anything that
amounts to a real commitment or follow-up for {{USER_NAME}} specifically -
something they said they'd do, or something the other person asked them to
do - no matter where in the entry it sits or how casually it's phrased.

FALLBACK - SOME NOTES ONLY CAPTURE AGENDA TOPICS, NOT THE DECIDED FOLLOW-UP.
Some entries are written as a list of discussion topics/agenda bullets rather
than a narrative of what was actually decided (e.g. a topic heading like
"promo timeline" with no note of what was actually agreed about it). When an
entry reads this way - real topics were clearly discussed but nothing
extractable comes out of the notes text itself - and there's a notetaker
draft for that same meeting sitting in the delivery channel (the one the
per-person job posted, with its own "Next Steps" section separated by
owner), extract {{USER_NAME}}'s items from THAT draft instead, using its
wording. Because this bypasses {{USER_NAME}}'s own correction step, tag every
item sourced this way distinctly so it reads as less-verified than
notes-sourced items - e.g. "(<date>, via {{NOTETAKER_TOOL}} draft - verify)"
instead of the normal "(<date>)". If {{USER_NAME}} later pastes a fuller
corrected version into their notes for that same date, don't worry about
perfectly reconciling wording - just avoid an obvious literal duplicate.

Keep telling {{USER_NAME}}'s own items apart from the other person's own
tasks the same way as always: explicit owner tags if present, otherwise
judgment about whose action it actually is (skip the other person's own
tasks). Also skip pure status updates and open-ended discussion topics that
don't imply anything for {{USER_NAME}} to actually go do. When something
reads as a genuine but soft ask or preference rather than a hard commitment,
still include it (worded close to what was actually said) rather than
dropping it silently - a soft item just sits there unchecked at worst, but a
missed real one is the exact failure this whole tracker exists to prevent.
Using the wording as written in the notes (this is {{USER_NAME}}'s corrected
version - trust it over anything a notetaker said), add each identified item
as a new unchecked item to the tracker, tagged with the entry's date. Don't
duplicate items already present. If, after reading the whole entry, there
truly is nothing that reads as a follow-up for {{USER_NAME}} - e.g. it's an
unfilled template with blank answers, or pure status with no asks either way
- add nothing for that person today; still don't invent items just to have
something to show.

STEP 1B - CHECK FOR ANSWERED CAPTURE-PROMPTS (only for anyone on the
handwritten note-capture pattern). Their per-person notes-capture job posts a
"How'd the 1:1 with <Name> go?" question once, right after their meeting,
then stops - it won't fire again until their next 1:1, so THIS job (which
runs every day) is what needs to notice a reply. For each such person, check
whether {{USER_NAME}} has replied to that question since it was posted and
that reply hasn't already been processed. If so, treat the reply as the note
directly (it's the user's own fresh account, not a machine summary, so it
needs no review gate - see SKILL.md Step 4) and fold it into the tracker the
same way Step 1 does for notes-doc content, tagged with the date of the
original 1:1, not today's date if they've since arrived.

STEP 2 - HEADS-UP REMINDER. For each person, check if they have a 1:1 exactly
{{LEAD_DAYS}} days from today. If so, check the tracker for that person's
open items and post one message, e.g. "📌 Your 1:1 with <Name> is in
{{LEAD_DAYS}} days (<date>). Open items: <list>." If there's nothing open,
skip posting for that person entirely - don't send a "nothing pending"
message unless the user said they want that during setup.

STEP 3 - DAY-OF BRIEFING. For each person, check if they have a 1:1 today. If
so, read their most recent notes entry plus open tracker items, and post a
short briefing before the meeting, e.g. "🗓️ Today's 1:1 with <Name> at
<time>: <2-4 bullet highlights to raise>." Before posting, check recent
channel history - if a briefing for this person and date was already posted
today, don't post a duplicate.

Keep every message concise - a few lines, plain prose or light bullets, no
heavy markdown headers. If a step finds nothing to do for a given person,
post nothing for that step/person (unless "nothing pending" messages were
explicitly requested). Don't post any summary beyond what's specified above.
```

## Optional weekly job

Only needed if `{{REVIEW_BLOCK}}` is not "none." Fires once a week, timed to
land shortly before the review block.

```
You are running {{USER_NAME}}'s weekly action-items kickoff. This fires
ahead of their recurring "{{REVIEW_BLOCK}}" calendar block. Act autonomously,
do not ask questions.

Read the tracker at {{TRACKER_LOCATION}}. It has one section per person:
{{PEOPLE_SHORT_NAMES}}. Count the open items in each section.

Post one message to {{DELIVERY_CHANNEL}} that: states the total open items
across everyone; gives a one-line breakdown per person who has 1+ open items
(skip anyone with zero); includes a link to the tracker; and frames it as a
nudge for the upcoming review block. Keep it under ~8 lines, plain prose or
light bullets, no heavy markdown headers.
```

## Optional roster-reconciliation job

Fires periodically (e.g. weekly) to catch 1:1s that were added to or dropped
from the calendar since setup, and keep the tracked roster in sync. See
SKILL.md Step 7e for the design rationale - **this job only ever proposes,
it never creates or disables another job on its own.** Confirmation happens
via a reaction on its proposal message, checked on the *next* run.

```
You are running {{USER_NAME}}'s periodic 1:1-roster reconciliation check.
Act autonomously to detect changes, but do NOT create, edit, or disable any
other scheduled job as a result of this run - propose changes in
{{DELIVERY_CHANNEL}} and wait for a human to confirm, per the steps below.

Currently tracked 1:1s: {{PEOPLE_LIST}}.

STEP 1 - CHECK FOR PENDING CONFIRMATIONS FROM LAST TIME. Look at this job's
own most recent proposal message(s) in {{DELIVERY_CHANNEL}} (search recent
history for messages this job posted). For each proposal that has a ✅
reaction from {{USER_NAME}}: now actually make the change (create the new
per-person notes-capture job for an addition, using the per-person job
template above with the details from that proposal; or disable - do not
delete - the relevant per-person job for a removal). Post a short
confirmation that it's done. For proposals with no reaction yet, leave them
pending - don't re-propose the same thing again in this run.

STEP 2 - SCAN FOR NEW 1:1-SHAPED EVENTS. Search the calendar (past 4-6 weeks)
for recurring events with exactly two attendees ({{USER_NAME}} plus one other
person) that look like a 1:1 by title pattern, and diff against the currently
tracked list above. For each one not already tracked, post a proposal: "Found
what looks like a new 1:1 with <Name> (<schedule>). React ✅ to this message
to start tracking it - I'll set up notes-capture and add them to the daily
sync once confirmed." Do not create anything yet.

STEP 3 - SCAN FOR DROPPED 1:1s. For each currently tracked person, check
whether their recurring event has had multiple consecutive missed instances
on the calendar (not just one skipped week - biweekly and irregular 1:1s
skip weeks normally; look for a gap clearly longer than their usual cadence,
e.g. 3+ expected instances in a row with nothing on the calendar). If so,
post a proposal: "Haven't seen a 1:1 with <Name> on the calendar in a while
(last one: <date>). React ✅ to this message if this 1:1 has ended and I
should stop tracking it - I'll disable their notes-capture job (not delete
it, so it's easy to resume later if this was temporary)." Do not disable
anything yet.

Keep proposal messages short and clearly distinguishable from regular
reminder/briefing messages (e.g. a distinct emoji prefix) so {{USER_NAME}}
can spot them easily and knows a reaction is the expected action.
```

## Notetaker formatting template

If the user already has an established prompt they use with their notetaker,
use their exact wording instead of this - consistency with their existing
notes matters more than this specific phrasing. Otherwise, this is a
reasonable default:

```
Give detailed notes with the date and day and the attendees as the header
and subheader, and give the notes their own subheadings, formatted so they
can be easily copied into a document for reference - no large headings or
decorative formatting.

Structure:
Meeting Title
Day, Month Date, Year
Attendees: Name, Name

Overview
- ...

Key Discussion Points
- ...

Decisions
- ...

Risks or Concerns
- ...

Next Steps
- ...

If there are action items, clearly separate them by owner when possible.
Output in simple plain text/markdown only, optimized for easy copying.
```
