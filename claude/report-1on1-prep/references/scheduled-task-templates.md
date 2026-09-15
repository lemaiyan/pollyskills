# Scheduled job template

This is a starting point, not a fill-in-the-blank form to apply mechanically.
Adapt the wording to what was actually discovered/decided during setup, but
keep the structure: the job must be fully self-contained, since it typically
runs in a fresh context with no memory of the setup conversation.

Before scheduling this, actually exercise every tool call it references (a
real, low-stakes call to each connector) during the setup conversation
itself. Some environments require an interactive permission grant the first
time a connector/tool is used - a scheduled job firing unattended can't
click through that prompt, so the grant needs to already be in place before
the first real firing, not discovered by it failing.

Placeholders used below (replace all of them - a template with a placeholder
still in it will fail or, worse, silently do nothing useful):

- `{{USER_NAME}}` - the person this is set up for (the report, not the
  manager)
- `{{TIMEZONE}}` - IANA timezone, e.g. `America/New_York`
- `{{DELIVERY_CHANNEL}}` - where reminders/notes get posted (a Slack channel
  ID, "DM", an email address, etc.)
- `{{TRACKER_LOCATION}}` - the agenda/tracker surface and its ID/link
- `{{MANAGER_LIST}}` - for each tracked manager relationship (usually just
  one): name, how their meetings are identified in the calendar/notetaker
  (exact title pattern), and where notes for that relationship live (if any)
- `{{NOTETAKER_TOOL}}` - name of the notetaker integration, or "none" if the
  user doesn't use one
- `{{LEAD_DAYS}}` - how many days before a 1:1 the heads-up reminder fires
  (default 2)
- `{{CATEGORIES}}` - which of the three tracker categories are in use: raise
  / I-owe-them / they-owe-me, or just a single combined list

## Daily job

Fires once a day, ideally early morning in `{{TIMEZONE}}`.

```
You are running {{USER_NAME}}'s daily 1:1-prep check. This is a recurring,
unattended automation - act autonomously, do not ask questions, just perform
the work described below and send messages as specified.

{{USER_NAME}}'s timezone is {{TIMEZONE}}. Figure out today's real date/time
yourself before starting.

Deliver all messages to: {{DELIVERY_CHANNEL}}.

{{USER_NAME}} has recurring 1:1(s) with their manager(s):

{{MANAGER_LIST}}

The running agenda/tracker is at {{TRACKER_LOCATION}}, organized as:
{{CATEGORIES}}.

[If a notetaker is in use, include this paragraph - otherwise omit Step 1
entirely and renumber:]
Any notes doc for a relationship is manually maintained by {{USER_NAME}}: they
take the {{NOTETAKER_TOOL}} draft, review and correct it (fixing any
transcription errors - wrong names, misattributed commitments, wrong
dates/numbers, etc.), then save their corrected version. Because of that
correction step, the DOC is the trustworthy record - never
{{NOTETAKER_TOOL}}'s raw output. {{NOTETAKER_TOOL}} is only used to produce a
first-draft note to hand to {{USER_NAME}}; it is never used to decide what
either side committed to.

STEP 1 - GET THE NOTE FOR MEETINGS THAT JUST HAPPENED. For each manager
relationship, check the calendar for a 1:1 that ended within roughly the
last 24 hours. If one happened, what you do next depends on that
relationship's note-capture pattern (decided during setup - SKILL.md Step
2):

[Notetaker variant - delivery only, does not touch the tracker:] Pull the
matching {{NOTETAKER_TOOL}} note and reformat it using the template in the
"Notetaker formatting template" section below. Post it to
{{DELIVERY_CHANNEL}} with an intro like "Draft notes from your 1:1 with
<Manager> - review/correct anything before it's the record of what was
said, then save it: <doc link if any>. I'll fold anything new into your
agenda/tracker once it's saved." If no matching note exists for a meeting
that clearly happened, say so explicitly rather than staying silent - don't
fabricate content either way. Do not add anything to the tracker in this
step - that only happens in Step 2, from the user's own saved version.

[Self-typed doc variant - no notetaker, user types their own notes:] Nothing
to do here; Step 2 reads that doc directly since it's already the user's own
words, with no separate draft/review needed.

[Handwritten / no digital notes variant:] Post a short direct question
instead of trying to fetch anything: "How'd the 1:1 with <Manager> go today?
Anything to flag on either side?" On each subsequent firing, check whether
{{USER_NAME}} has replied since that question was posted (not just on this
firing - the reply might come later) and, once they have, treat it as the
note directly in Step 2 - it's the user's own fresh account, so it needs no
review gate before going into the tracker.

STEP 2 - SYNC THE TRACKER FROM THE USER'S OWN NOTES (the only source for
tracker content from meetings; run this every day regardless of whether a
meeting happened today). For each relationship: open the notes doc (or
whatever the notes source is) and find the most recent DATED entry that
actually has real content - skip a future-dated placeholder/stub some notes
docs get pre-created with ahead of the next meeting; that's not a real 1:1
yet. Compare it against what's already on the tracker (e.g. by date tag). If
there's new content not yet reflected, read the WHOLE entry - don't limit the
search to a literally-labeled "Action items" or "Next Steps" list. Plenty of
real notes don't use that heading at all, or leave it blank/near-empty while
the actual commitment is answered inline somewhere else in the entry - a
common spot is a Q&A-style template's "anything you need from me?" or "what
should I flag?" question, where the answer is just as real an item as one
under a formal heading, only phrased conversationally. Read the full entry
and use judgment to infer anything that's a genuine commitment or follow-up,
no matter where it sits or how casually it's phrased.

FALLBACK - SOME NOTES ONLY CAPTURE AGENDA TOPICS, NOT THE DECIDED FOLLOW-UP.
Some entries are a list of discussion topics rather than a narrative of what
was actually decided (a topic heading like "promo timeline" with no note of
what got agreed). When that's the case, and there's a notetaker draft for the
same meeting sitting in the delivery channel with its own "Next Steps"
section, extract from THAT instead, using its wording. Because this bypasses
{{USER_NAME}}'s own review step, tag every item sourced this way distinctly -
e.g. "(<date>, via {{NOTETAKER_TOOL}} draft - verify)" instead of the normal
"(<date>)" - so it's clearly less-verified than notes-sourced items. If a
fuller corrected version lands in the notes later for that same date, don't
worry about reconciling wording perfectly, just avoid an obvious duplicate.

Sort each identified item into the right category ({{CATEGORIES}}) using the
wording as written in the notes (this is {{USER_NAME}}'s corrected version -
trust it over anything a notetaker said, except per the fallback above), and
add each as a new unchecked item, tagged with the entry's date. Don't
duplicate items already present. If, after reading the whole entry and
checking the fallback, there's truly nothing new to extract - e.g. it's an
unfilled template with blank answers, or pure status with no asks either way
- add nothing for that relationship today; don't invent items just to have
something to show. If the delivery channel also supports the user dropping in
ad hoc notes between meetings (e.g. "remind me to bring up X next time"),
also check for any such messages since the last run and fold them into the
"things to raise" category the same way - these come from the user directly,
so no review step is needed for them.

STEP 3 - HEADS-UP REMINDER. For each relationship, check if there's a 1:1
exactly {{LEAD_DAYS}} days from today. If so, pull the current tracker
contents for that relationship and post one message, e.g. "📌 Your 1:1 with
<Manager> is in {{LEAD_DAYS}} days (<date>). On your list: <items>." If
there's nothing on the tracker for that relationship, skip posting entirely
- don't send a "nothing pending" message unless the user asked for that
during setup.

STEP 4 - DAY-OF BRIEFING. For each relationship, check if there's a 1:1
today. If so, read the most recent notes entry plus the current tracker
contents, and post a short briefing before the meeting, e.g. "🗓️ Today's 1:1
with <Manager> at <time>: <2-4 bullet highlights - what's still open on both
sides, plus anything you flagged to raise>."

Keep every message concise - a few lines, plain prose or light bullets, no
heavy markdown headers. If a step finds nothing to do for a given
relationship, post nothing for that step/relationship (unless "nothing
pending" messages were explicitly requested). Don't post any summary beyond
what's specified above.
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

Decisions / Commitments (by who)
- ...

Things to Raise Next Time
- ...

Output in simple plain text/markdown only, optimized for easy copying.
```
