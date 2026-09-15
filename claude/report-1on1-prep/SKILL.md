---
name: report-1on1-prep
description: Sets up an ongoing 1:1-prep automation for someone preparing for their OWN recurring 1:1s with their manager (a report, not a manager tracking reports). Discovers the 1:1 from the user's calendar, keeps a running agenda of things to raise plus open follow-ups on both sides, and reminds them before each 1:1 what to bring up. Use whenever someone wants to prep better for a one-on-one with their boss, stop forgetting what they meant to ask, track commitments their manager made (or vice versa), or build a running agenda for their 1:1s - even without the word "skill" or "automation." Phrases like "help me prep for my 1:1 with my manager", "I keep forgetting what I wanted to bring up", or "remind me what my manager said they'd follow up on" trigger this. Mirror-image counterpart of a manager-side 1:1 tracker skill - use this one when the user is the report, not the manager.
---

# Report 1:1 Prep

Walking into a 1:1 with nothing prepared wastes it - for the report, not just
the manager. The usual failure mode is different from the manager's version
of this problem: it's not "I forgot to follow up on what I owe someone," it's
"I had three things I wanted to raise this week and by Tuesday afternoon I
can only remember one of them," or "my manager said they'd look into my
comp/timeline/promo case three weeks ago and I have no idea if that's still
open." This skill sets up a small recurring automation that fixes that: it
watches the user's calendar for their 1:1(s) with their manager, keeps a
running agenda of things to raise plus open follow-ups on both sides, and
reminds them before each meeting what's on it.

This is a **setup skill**, not a one-shot task. Running it once produces a
standing automation (typically one or two scheduled jobs) that keeps working
after the conversation ends. Treat the instructions below as an interview +
build process, not a single response to generate.

This skill is built for Claude specifically - the scheduled job it produces
assumes a Claude-based executor (this same model/product family) on each
firing, using Claude's own tool-calling conventions and MCP-style connectors.
Don't generalize the instructions for portability to other AI assistants
(e.g. ChatGPT) or non-Claude automation - write the job prompt the way you
would for another Claude session, not for an arbitrary agent.

Two design principles run through everything below, worth stating up
front:

- **Suggest, don't dictate, where data lives.** For any given choice - where
  notes are captured (Step 2), where the agenda/tracker lives (Step 3) -
  recommend a sensible default and explain why, but the user picks.
  Different people reasonably want their tracker in a Canvas vs. Notion vs.
  a plain doc, and their notes captured via a notetaker vs. typed vs.
  handwritten; none of these are "the right way," they're preferences the
  automation adapts to.
- **The scheduling *architecture* is standard; its granularity is per
  relationship.** The pattern in Step 7 (get-the-note, sync, heads-up,
  day-of briefing) is the reusable shape. Most people have one manager
  relationship so it collapses into a single job, but if someone tracks more
  than one (Step 1's matrixed-org case), apply the same standard shape once
  per relationship rather than cramming several into one job's logic -
  including, if it's ever useful, running change-detection independently per
  relationship rather than only as one combined check.

**If the user is the manager, not the report** - i.e. they want to track
*their reports'* action items rather than prepare for their own 1:1 with
their boss - that's the opposite direction this skill covers. Use (or point
them to) a manager-side 1:1 copilot skill instead. The two are complementary,
not the same skill in disguise: this one has a single ongoing relationship
and centers on "what do I want to raise / what's still open," while the
manager-side one tracks multiple reports and centers on "who owes me what."

## Before you start: what you need from the environment

This only works if the session has at least:

1. **A calendar connector** (Google Calendar, Outlook/Microsoft Graph, or
   similar) - used to discover the 1:1(s) with the user's manager.
2. **Some way to deliver reminders** - Slack (DM or a channel), email, or
   even just a chat message back to the user if this is being run
   interactively rather than on a schedule.
3. **Some way to run code on a schedule without a human present**, if the
   user wants this automated rather than run on demand - in this
   environment that's the scheduled-task / trigger mechanism (e.g.
   `create_trigger`-style tools). Each firing is a fresh Claude session with
   no memory of this conversation, so the job's stored instructions need to
   be fully self-contained (see Step 7) - but they can and should assume
   Claude is what's executing them.

Optional, but worth asking about:

- **A notes/docs connector** (Google Drive, Notion, OneDrive) if the user
  wants their running agenda and notes to live in a doc they can also open
  and edit by hand.
- **A notetaker tool** (Granola, Otter, Fireflies, Fathom, or similar) if
  meetings are recorded and the user wants a first-draft note generated
  automatically.

Don't assume any of the optional ones are present - ask. And don't assume the
required ones support everything they look like they should (see "Check what
your connector can actually do" below) - verify before you build on top of
them. This can also run perfectly well with nothing but a calendar and a way
to send the user a message - see "Adapting to a minimal toolset" below.

**Also verify permissions now, not at 6am.** The first time a given
connector/tool is used in this environment, it may require an interactive
permission grant (an OAuth consent screen, a tool-authorization prompt) -
something only a human present in the moment can click through. A scheduled
job firing unattended can't do that; if a connector's permission hasn't been
granted yet, that first automated run will simply fail or hang waiting on an
approval nobody's there to give. So during this setup conversation, actually
exercise every specific tool call the job will make - not just one
read-only "does this connector work at all" probe, since permission grants
are often scoped per action rather than per connector. If the job needs to
send a message and update a doc, exercise a real instance of each, not just
a calendar read - so any permission prompt surfaces now, while the user is
right here to approve it. The same applies if the user adds a new capability
later (a new connector, a newly-connected notetaker): exercise it
interactively once before folding it into the scheduled job's instructions.

## Step 1 - Discover the 1:1(s) instead of asking who the manager is

Resist the urge to open with "who's your manager?" Search the user's primary
calendar for recurring events that look like a 1:1 with their manager: weekly
or biweekly recurrence, exactly two attendees (the user plus one other
person), and a title pattern like `"<Me> / <Manager>"`, `"<Manager> <> <Me>"`,
`"1:1"`, `"1-1"`, or similar. Look back 4–6 weeks so you catch the pattern
even if titles are inconsistent between instances.

Most people have exactly one such relationship, but not everyone does -
someone in a matrixed org might have a recurring 1:1 with both a "formal"
manager and a project/dotted-line lead. Present whatever you find back as a
confirm-or-correct list rather than fact: "I found a recurring 1:1 with
<Name> - is that your manager? I also see one with <Other Name> that looks
similar - is that a second manager relationship I should track too, or a
different kind of meeting?" Don't assume the first plausible match is the
only one, and don't assume every 1:1-shaped meeting on the calendar is with
a manager (a peer 1:1 or a mentoring chat can look identical from the
outside). If your environment's structured-question tool is available, use
it for this confirm-or-correct step - offer "Yes, that's my manager" plus
whichever secondary matches you're unsure about as their own options, and
let the tool's own free-text fallback handle anything the user needs to type
that isn't one of the offered choices. Fall back to plain conversational
text if no such tool exists in this environment.

## Step 2 - Find out where their notes already live

Ask, don't assume - and don't assume the two obvious options (an AI
notetaker, or nothing at all) are the only possibilities. In practice you'll
run into a handful of distinct patterns, and each implies a different build:

- **An AI notetaker** (Granola, Otter, Fireflies, Fathom, etc.) generating a
  transcript-based summary. This is the case the trust boundary in Step 4 is
  really about - machine-generated attribution needs a human review pass.
- **A running doc or list the user types themselves** - sometimes shared
  with their manager, sometimes private. (Check whether something is already
  linked as an attachment on the recurring calendar event - a strong signal
  of an existing doc, and worth noting whether it's shared or private, since
  that changes what's appropriate to write into it automatically, per Step
  4's note on shared docs.) This is the user's own words, not a machine's
  guess - see Step 4 for why that changes how much review it needs.
- **Handwritten notes** (a paper notebook, a personal notes app with no API,
  notes scribbled mid-meeting that never get typed anywhere a connector can
  reach). This is a completely valid - and common - way to take 1:1 notes.
  The right pattern isn't to wait for a doc that will never appear; it's to
  have the scheduled job **ask the user directly**, shortly after the
  meeting, for a quick recap ("how'd it go with your manager - anything to
  follow up on, on either side?"), and build the agenda straight from their
  reply. That reply is itself the user's own fresh, reviewed words - see
  Step 4.
- **Nothing at all, not even mentally organized** - in which case offer to
  start the tracker from scratch (see Step 6) and rely on the same
  ask-after-the-meeting pattern above, or offer to skip a written-notes
  layer entirely and just use the running agenda as the only record.

If a notes doc is shared with the manager, be more careful about what gets
written into it automatically (see Step 4) - a personal, private list of
"things I'm annoyed about" or "what I want to ask for" doesn't belong in a
doc the manager can also open.

## Step 3 - Ask the judgment-call questions

These aren't things you can infer - ask them together, using whatever your
environment's structured-question tool is (e.g. `AskUserQuestion`) rather
than open text, so the user can answer quickly:

1. **Where should reminders land?** DM, a dedicated channel, or email.
2. **Where should the running agenda/tracker live?** A checklist-capable
   surface the user can add to and tick off themselves is worth recommending
   - a Slack Canvas, a Notion checklist, or similar. A running document works
   too. Unlike the manager-side version of this problem, this tracker
   usually has three lightweight categories rather than one flat list:
   things the user wants to *raise* (their own agenda, which should be easy
   to add to at any time, not just right after a meeting), things *they*
   owe their manager, and things their *manager* owes them. Not everyone
   wants all three - ask, or default to a single combined list if the user
   would rather keep it simple.
3. **Should adding to the agenda be easy to do anytime, not just around a
   meeting?** Part of the value here is capturing "I want to bring this up
   next time" the moment it occurs to the user, mid-week, not just during a
   scheduled check-in. If the delivery channel supports it (e.g. a Slack
   channel the user can post into), mention that they can just drop a note
   there anytime and you'll fold it into the agenda - this is a real
   improvement over a purely scheduled, backward-looking tracker.
4. **Does a notetaker exist, and should it feed the automation?** If yes,
   which tool, and - critically - see the trust boundary below before
   wiring it in.
5. **How many days before a 1:1 should the heads-up reminder fire?** Default
   to 2 if the user has no preference.

## Step 4 - The trust boundary: notetaker output vs. the user's own notes

Same underlying risk as on the manager side, worth explaining again because
it's easy to underrate for a "personal" use case: **an AI notetaker's
automatic summary can misattribute who said or committed to what, or mis-hear
a name or a number** (a mumbled "end of Q3" heard as "end of Q2," a
commitment the manager made getting summarized as something the user
themselves offered to do, or vice versa). If that goes straight into a
tracker the user later treats as "what my manager promised me," an
unreviewed transcription error doesn't stay a one-time slip - it becomes a
belief the user carries into a career conversation, with nothing prompting
them to double check it.

The fix is the same pattern as the manager-side skill: treat the notetaker's
output as a first draft only. Deliver it to the user for review (see the
formatting template in `references/scheduled-task-templates.md`), and only
add anything to the running agenda/follow-ups once it comes from the user's
own reviewed and saved notes - never straight from the notetaker's raw
summary. If the user explicitly says they don't want this caution ("I trust
it, just wire it straight through"), that's their call - just make sure
they've heard the tradeoff first, and tag anything added this way as
unreviewed so they can trace it back to the source meeting if something ever
looks off.

If there's no notetaker at all - handwritten notes, a direct reply to the
job's "how'd it go" prompt, or notes the user types themselves into a doc -
this specific concern doesn't apply. The risk being guarded against is
*machine* mis-hearing/mis-attribution; a human typing or writing their own
account of their own meeting doesn't have that failure mode (it can still
contain an honest mistake, but that's true of any note-taking and isn't
something an extra review gate meaningfully catches). So for these sources,
build the agenda/tracker straight from what the user wrote or said - don't
impose the notetaker review step on content that never went through a
notetaker.

## Step 5 - Check what your connector can actually do before promising it

Before telling the user "I'll update your notes doc automatically," verify
the connector genuinely supports editing existing file content - many
Drive/Docs-style connectors only expose read, create-new-file, rename, and
move, with no way to append to or edit a file that already exists. If that's
the case here, say so plainly and fall back to delivering ready-to-paste
content instead of claiming an update happened. An honest "I can't edit this
doc directly, here's the text to paste in yourself" is far better than a
notes doc that quietly never gets updated while the user assumes it is.

## Step 6 - Build the running agenda/tracker

Create whatever surface was chosen in Step 3, structured around however many
of the three categories the user wanted (raise / I-owe / they-owe). If the
user has existing notes with things already sitting in them unresolved, do a
one-time backfill - but only from the user's own written notes, per the
trust boundary above, and tag each backfilled item with which meeting/date it
came from so the user can sanity-check it.

Unlike the manager-side version of this skill, a dedicated recurring
"review block" calendar event usually isn't needed here - the review *is*
the 1:1 itself. Don't create one unless the user specifically asks for a
separate personal prep block (some people do want, say, 15 minutes blocked
the morning of, purely for themselves).

## Step 7 - Set up the scheduled job(s)

See `references/scheduled-task-templates.md` for full parameterized prompt
text to adapt. In short, this usually collapses into a single daily-ish job
(there's normally only one relationship to check, unlike the manager-side
skill's per-report loop):

- **Gets the note for any 1:1 that happened recently**, and what this means
  depends on which note-capture pattern applies (Step 2): if a notetaker is
  in play, drafts a note and delivers it to the user for review (see Step 4,
  never auto-saved); if the user types their own notes into a doc, just
  reads that doc directly (no separate draft/review needed); if notes are
  handwritten or nonexistent, asks the user directly for a quick recap and
  treats their reply as the note (see "Adapting to a minimal toolset" below
  - the same ask-directly pattern applies here whether or not the rest of
  the toolset is minimal, since someone can have full Slack/Drive access and
  still just prefer pen and paper).
- **Syncs the running agenda/tracker** from whatever the user's own notes
  currently say (not from the notetaker), and from anything the user has
  told the automation directly in the meantime if that capture path exists
  (Step 3, question 3).
- **Sends the heads-up reminder** for any 1:1 coming up in N days, listing
  the current agenda and open items on both sides.
- **Sends a same-day briefing** before any 1:1 happening today, pulling in
  what was discussed/committed last time.

If the user has more than one tracked manager relationship (Step 1), the same
job just loops over each one - it doesn't need a second, separate weekly job
the way the manager-side skill does, since there's no cross-report rollup to
produce.

Every value this job needs - the manager's name, doc links, channel/tracker
IDs, timezone, the reminder lead time, whether a notetaker is in play - must
be filled in literally in the job's stored instructions. Scheduled jobs
typically fire as a fresh, memory-less run each time: they can't see this
conversation, so nothing here can be left implicit or "inferred from
context" the way it can in an interactive turn. Write the instructions as if
handing them to a new hire who's never seen this conversation.

## Step 8 - Confirm, and offer a test firing

Summarize what got built (tracker link, channel/DM choice, job schedule) back
to the user in plain language. If your environment supports firing a
scheduled job on demand, offer to do that once as a live test rather than
waiting for the first real firing - it's the fastest way to catch a wrong ID
or a misjudged date filter while the user is still around to look at the
result with you. If a structured-question tool is available, use it here
too - e.g. "Looks good, go ahead" / "Run a test firing first" / "I want to
change something" as the offered choices - rather than asking the user to
type out a free-form reply to a yes/no question.

## Adapting to a minimal toolset

Someone might have only a calendar and no Slack, no notes app, no notetaker.
That's fine - the whole thing still works with just a calendar and a way to
send the user one message:

- Delivery becomes email (or whatever's available), and the tracker itself
  can live there too - e.g. one ongoing email thread that gets replied to
  with the current state, since most email connectors can't edit a sent
  message in place.
- With no notetaker (whether that's because there's no toolset for one, or
  because the user just takes handwritten notes even though other tools are
  available), there's no draft-note step - instead, the job can simply ask
  the user for a couple of bullet points after each 1:1 and only build the
  agenda/tracker from their reply. Since the job fires once and the reply
  might come later, have it check on each subsequent firing whether an
  earlier question has since been answered, rather than only asking once
  and moving on.
- With nothing existing to backfill from, just start the tracker empty
  rather than inventing history.

Say plainly what's different because of the reduced toolset (no clickable
checkboxes over email, a short lag waiting on the user's own notes) rather
than quietly delivering a worse experience than what was implied.

## Common things that go wrong (and how to avoid them)

- **Trusting notetaker attribution over the user's own corrected notes.**
  Covered above - this is the one to get right, same as on the manager side.
- **Assuming everyone either uses an AI notetaker or has nothing at all.**
  Handwritten notes and self-typed docs are common and legitimate note-taking
  styles (Step 2) - defaulting to "wait for the notetaker" for someone who
  writes on paper means the automation just never produces anything, silently.
- **Assuming a connector's permission grant will just be there for a
  scheduled run.** Covered above - exercise every tool interactively during
  setup, and again for anything added later, before folding it into a
  scheduled job.
- **A permission grant that quietly expires or gets revoked later.** Setup
  isn't the only time this can bite - a token can lapse months in. If a real
  firing hits a permission error, say so plainly in its output (same
  principle as "silent partial success" below) rather than swallowing it, so
  the user finds out from a message instead of from a gap in their agenda.
- **Assuming a connector can edit files it can only read/create.** Test this
  assumption, don't infer it from the connector's name.
- **Writing personal agenda items into a doc the manager can also see.**
  Check whether a notes doc is shared before writing anything into it that
  the user might not want their manager reading directly (e.g. "ask about
  promo timeline" phrased bluntly).
- **Treating this like the manager-side skill with the loop count set to
  one.** It's not just "one report" - the framing is different (the user's
  own agenda and open questions, not tracking someone else's accountability),
  and the running-agenda-anytime capability (Step 3, question 3) is a
  genuinely different feature worth offering, not just a smaller version of
  the manager tracker.
- **Being noisy.** A reminder every single day when there's nothing new
  becomes something people stop reading. Skip the message entirely when
  there's nothing to report, rather than sending a "nothing pending" message
  by default.
- **Silent partial success.** If a notetaker has no matching entry for a
  meeting that clearly happened, or a doc can't be reached, say so in the
  job's output rather than staying silent.
- **Depending on a literal "Action items"/"Next Steps" heading to find
  items.** This is a real, observed failure mode: plenty of people's actual
  notes leave that section blank or skip the heading entirely, while a real
  commitment is sitting in plain sight elsewhere in the same entry - often
  the answer to a Q&A-template question like "anything you need from me?" A
  job that only scans for a specifically-labeled list will silently miss
  these and quietly go stale while still "running successfully" every day.
  Extraction needs to read the whole entry and infer commitments the way a
  person skimming the notes would, not pattern-match on a heading.
- **Some notes only capture agenda topics, not what was decided.** An entry
  that lists topic headings ("promo timeline," "blocker on X") with no note
  of what was actually agreed isn't sparse because nothing happened - a real
  decision was made, it just never got written down. If a notetaker draft for
  that same meeting exists in the delivery channel, its own "Next Steps"
  section is a legitimate fallback (see the daily job template's FALLBACK
  paragraph), but tag anything pulled from it distinctly since it skips the
  user's own review step. Don't treat an agenda-style entry as "nothing to
  sync" just because it isn't a narrative.

## Reference

- `references/scheduled-task-templates.md` - parameterized prompt text for
  the daily job, plus the notetaker-formatting template, ready to fill in
  with the specifics discovered during setup.
