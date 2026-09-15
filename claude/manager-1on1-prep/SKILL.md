---
name: manager-1on1-prep
description: Sets up a personalized, ongoing 1:1-prep automation for people managers - discovers recurring 1:1s directly from the user's calendar, tracks action items sourced from their own notes (not blindly from an AI notetaker), and schedules reminders before each 1:1 plus a weekly action-items review. Use this whenever someone wants to automate 1:1 prep, stop losing track of action items from direct reports, get a reminder of what to raise before a one-on-one, build a "manager copilot," or turn an existing notes-plus-calendar habit into a recurring assistant - even if they never say the word "skill" or "automation." Phrases like "help me stay on top of my 1:1s", "I keep forgetting what my reports owe me", "remind me what to bring up before my 1:1 with X", "set up a weekly action-items review", or "can Claude prep me for one-on-ones" should all trigger this.
---

# Manager 1:1 Copilot

A manager's 1:1s only pay off if action items actually get followed up on. The
usual failure mode isn't a bad conversation - it's that three weeks later
nobody remembers who owed what, so the same topics quietly get raised again.
This skill sets up a small recurring automation that closes that loop: it
watches a manager's calendar for their 1:1s, keeps a running list of open
action items sourced from *their own* notes, and nudges them before each
meeting with what's still outstanding.

This is a **setup skill**, not a one-shot task. Running it once produces a
standing automation (typically one small scheduled job per tracked 1:1 for
notes-capture, plus one shared daily job and an optional weekly job - see
Step 7) that keeps working after the conversation ends. Treat the
instructions below as an interview + build process, not a single response
to generate.

This skill is built for Claude specifically - the scheduled jobs it produces
assume a Claude-based executor (this same model/product family) on each
firing, using Claude's own tool-calling conventions and MCP-style connectors.
Don't generalize the instructions for portability to other AI assistants
(e.g. ChatGPT) or non-Claude automation - write job prompts the way you
would for another Claude session, not for an arbitrary agent.

Two design principles run through everything below, worth stating up front:

- **Suggest, don't dictate, where data lives.** For any given choice - where
  notes are captured (Step 2), where the tracker lives (Step 3), how drafts
  get delivered (Step 7b) - recommend a sensible default and explain why,
  but the user picks. Different people will reasonably want their tracker
  in a Canvas vs. Notion vs. a plain doc, and their notes captured via a
  notetaker vs. typed vs. handwritten; none of these are "the right way,"
  they're preferences the automation needs to adapt to.
- **The scheduling *architecture* is standard; its granularity is per
  relationship.** The pattern in Step 7 (per-relationship notes-capture,
  shared daily sync, optional weekly rollup, optional reconciliation) is the
  reusable shape - don't reinvent it per user. But apply it at whatever
  granularity actually matches each relationship: a person whose meeting
  time or cadence is unusual, or whose roster-reconciliation checks need to
  run independently of everyone else's, can get their own instance of a job
  rather than being folded into a shared one, the same way notes-capture
  already is. Default to shared jobs where nothing distinguishes one
  relationship from another; split out a relationship into its own job when
  something about it (timing, an irregular cadence, wanting closer
  change-detection) genuinely calls for it.

## Before you start: what you need from the environment

This only works if the session has at least:

1. **A calendar connector** (Google Calendar, Outlook/Microsoft Graph, or
   similar) - used to discover 1:1s and, optionally, to book a recurring
   review block.
2. **Some way to deliver reminders** - Slack (DM or a channel) or email are
   the common ones.
3. **Some way to run code on a schedule without a human present** - in this
   environment that's the scheduled-task / trigger mechanism (e.g.
   `create_trigger`-style tools). Each firing is a fresh Claude session with
   no memory of this conversation, so the job's stored instructions need to
   be fully self-contained (see Step 7) - but they can and should assume
   Claude is what's executing them.

Optional, but worth asking about:

- **A notes/docs connector** (Google Drive, Notion, OneDrive) if the user
  keeps written 1:1 notes somewhere and wants the tracker to read from it.
- **A notetaker tool** (Granola, Otter, Fireflies, Fathom, or similar) if the
  user records meetings and wants a first-draft note generated automatically.

Don't assume any of the optional ones are present - ask. And don't assume the
required ones support everything they look like they should (see
"Check what your connector can actually do" below) - verify before you build
on top of them.

**Also verify permissions now, not at 6am.** The first time a given
connector/tool is used in this environment, it may require an interactive
permission grant (an OAuth consent screen, a tool-authorization prompt) -
something only a human present in the moment can click through. A scheduled
job firing unattended at 6am can't do that; if a connector's permission
hasn't been granted yet, that first automated run will simply fail or hang
waiting on an approval nobody's there to give. So during this setup
conversation, actually exercise every specific tool call the jobs will make
- not just one read-only "does this connector work at all" probe, since
permission grants are often scoped per action rather than per connector.
If a job needs to write a message, update a canvas, and create a scheduled
task, exercise a real instance of each of those three, not just a calendar
read - so any permission prompt surfaces now, while the user is right here
to approve it, rather than silently breaking the first unattended firing.
This is also worth mentioning explicitly if the user adds a new capability
later (a new connector, a newly-connected notetaker): that addition should
get exercised interactively once before you fold it into a scheduled job's
instructions.

## Step 1 - Discover the 1:1s instead of asking for a list

Resist the urge to ask "who are your direct reports?" as the first question.
People's calendars already encode this, and discovering it yourself produces
a better experience *and* catches meetings the user might not think to
mention. Search the primary calendar for events that look like a recurring
1:1: weekly or biweekly recurrence, exactly two attendees (the user plus one
other person), and a title pattern like `"<Name> / <Me>"`, `"<Me> <> <Name>"`,
`"1:1"`, `"1-1"`, or just two first names separated by a slash. Look back
4–6 weeks so you catch the pattern even if titles are inconsistent between
instances.

Present what you found back to the user as a confirm-or-correct list rather
than presenting it as fact - recurring-event detection has false positives
(a biweekly sync that isn't really a 1:1) and false negatives (a 1:1 that
skipped a couple of weeks). Something like: "I found these recurring 1:1s on
your calendar: A, B, C, D. Did I miss anyone, or include something that
isn't really a 1:1?" If your environment's structured-question tool is
available, this confirm-or-correct pattern is exactly what it's built for:
offer "Yes, that's everyone" as one option, plus the individual 1:1s you're
least sure about (the ones with irregular gaps, or a title that only loosely
matches) as their own options to flag; the tool's own free-text fallback
(e.g. an "other" choice) covers anything the user needs to type that isn't
one of the offered choices, so you don't need to enumerate every possible
correction yourself. Fall back to plain conversational text if no such tool
exists in this environment.

## Step 2 - Find out where their notes already live

Ask, don't assume, whether the user already has a notes system - and don't
assume the two obvious options (an AI notetaker, or nothing at all) are the
only possibilities. In practice you'll run into a handful of distinct
patterns, and each implies a different build:

- **An AI notetaker** (Granola, Otter, Fireflies, Fathom, etc.) generating a
  transcript-based summary. This is the case the trust boundary in Step 4 is
  really about - machine-generated attribution needs a human review pass.
- **A Drive/Docs folder** the user types into themselves, live or right
  after the meeting (often one doc or one folder per person - check whether
  a doc is already linked as an attachment on the recurring calendar event,
  a strong signal of an existing per-person doc). This is the user's *own*
  words, not a machine's guess - see Step 4 for why that changes how much
  review it needs.
- **A Notion database, Confluence space, or wiki** - same as above, just a
  different surface.
- **Handwritten notes** (a paper notebook, a personal notes app with no API,
  notes scribbled mid-meeting that never get typed anywhere a connector can
  reach). This is a completely valid - and common - way to take 1:1 notes,
  and the automation needs to work around it rather than quietly assuming
  it doesn't exist. The right pattern here isn't to wait for a doc that will
  never appear; it's to have the scheduled job **ask the user directly**,
  shortly after the meeting, for a quick recap ("how'd it go with <Name> -
  anything to flag or follow up on?"), and build the tracker straight from
  their reply. That reply is itself the user's own fresh, reviewed words -
  see Step 4.
- **Nothing at all, not even mentally organized** - in which case offer to
  start the tracker from scratch (see Step 6) and rely on the same
  ask-after-the-meeting pattern above, or offer to skip a written-notes
  layer entirely and just use the tracker as the only record.

It's fine - expected, even - for a single user to mix patterns across
different reports (a notetaker for some 1:1s, handwritten for others). Ask
per relationship if the answer isn't obviously the same for everyone.

## Step 3 - Ask the judgment-call questions

These aren't things you can infer - they're genuine preferences that vary by
person and by org. Ask them together, using whatever your environment's
structured-question tool is (e.g. `AskUserQuestion`) rather than open text,
so the user can answer quickly:

1. **Where should reminders land?** DM, a dedicated channel (offer to create
   one - a private channel keeps this out of a busy DM history), or email.
2. **Where should the open-action-items tracker live?** A checklist-capable
   surface the user can tick off themselves is worth recommending over a
   plain document - Slack Canvas (native checkboxes), a Notion checklist
   database, or similar. A running document works too if the user prefers
   it or nothing checklist-native is available.
3. **Should there be a recurring calendar block** dedicated to working
   through open action items, and if so, what day/time? This is optional -
   some managers would rather just get reminders inline before each 1:1
   without a separate block.
4. **Does a notetaker exist, and should it feed the automation?** If yes,
   which tool, and - critically - see the trust boundary below before wiring
   it in.
5. **How many days before a 1:1 should the heads-up reminder fire?** Default
   to 2 if the user has no preference.

## Step 4 - The trust boundary: notetaker output vs. the user's own notes

This is the single most important design decision in this skill, learned the
hard way: **an AI notetaker's automatic summary can misattribute who owns an
action item, or mis-hear a name** (a "Tim" transcribed from a mumbled
"Kim," an action item attributed to the wrong person because the model
guessed from context rather than heard it clearly). If you wire the
notetaker's raw output straight into a persistent tracker, those errors
become invisible - the user just sees a checklist item with a wrong name
sitting there, and won't know to question it unless it looks obviously
wrong.

The fix is a human-in-the-loop step, and it's worth explaining to the user
*why* rather than just doing it silently:

- Treat the notetaker's output as a **first draft only**. After a meeting,
  format it nicely (see the template in
  `references/scheduled-task-templates.md`) and deliver it to the user for
  review - not for their entertainment, but as a real editorial checkpoint
  where they fix any name or attribution errors before anything gets
  written into their permanent notes.
- The **tracker only ever gets populated from the user's own notes**, once
  they've reviewed/corrected and saved them - never directly from the raw
  notetaker output. If the user hasn't gotten around to saving their notes
  yet, the tracker simply doesn't have that meeting's items yet. That's the
  correct behavior, not a bug - it's the cost of the correction step, and
  it's worth being upfront with the user about that lag when you set this
  up, so "why isn't this showing up yet" doesn't become a support question
  three days later.
- If the user explicitly says they don't want this caution (e.g. "I trust
  the notetaker, just wire it straight in"), that's their call to make -
  just make sure they've heard the tradeoff first.

If there's no notetaker at all - handwritten notes, a direct reply to the
job's "how'd it go" prompt, or notes the user types themselves into a doc -
this specific concern doesn't apply. The risk being guarded against is
*machine* mis-hearing/mis-attribution; a human typing or writing their own
account of their own meeting doesn't have that failure mode (it can still
contain an honest mistake, but that's true of any note-taking and isn't
something an extra review gate meaningfully catches). So for these sources,
build the tracker straight from what the user wrote or said - don't impose
the notetaker review step on content that never went through a notetaker.

## Step 5 - Check what your connector can actually do before promising it

Before telling the user "I'll update your notes doc automatically," verify
the connector genuinely supports editing existing file content - many
Drive/Docs-style connectors only expose read, create-new-file, rename, and
move, with no way to append to or edit a file that already exists. If that's
the case here, say so plainly and fall back to delivering ready-to-paste
content instead of claiming an update happened. Silently failing (or worse,
claiming success when nothing was written) is far worse than an honest "I
can't edit this doc directly, here's the text to paste in yourself" -
the user can work with an honest limitation; they can't work with a
notes doc that quietly never got updated.

## Step 6 - Build the tracker and (optionally) the calendar block

Create whatever checklist/tracker surface was chosen in Step 3, seeded per
person (one section/list per discovered 1:1). If the user has existing notes
with real open items already sitting in them, do a one-time backfill from
those - but only from the user's own written notes, per the trust boundary
above, and say clearly where each backfilled item came from (which meeting,
which date) so the user can sanity-check it.

If a recurring review block was requested, create it as an actual calendar
event with a weekly (or chosen) recurrence rule, at a time that doesn't
collide with what's already on the calendar.

## Step 7 - Set up the scheduled jobs

See `references/scheduled-task-templates.md` for full parameterized prompt
text to adapt. There are up to four kinds of job, and getting the *timing
architecture* right matters as much as the content of each job - a design
that looks reasonable on paper can still leave the user waiting a full day
for notes that should have shown up within the hour. Here's why, and what to
do instead.

### 7a - One notes-capture job per person, not one shared daily batch

The tempting design is a single daily job that, among other things, looks
back ~24 hours for any 1:1 that "just happened" and drafts its note. Don't
do this if any of the tracked 1:1s can happen at a time of day *after* that
daily job's own run time. Concretely: if the daily job runs at 6:30am and
someone's 1:1 is at 11am, a note captured for an 11am meeting that happened
today won't get picked up until the *next* day's 6:30am run - up to 24 hours
of latency on something the user wanted "right after the meeting." This was
discovered by watching a real deployment miss same-day notes for exactly
this reason.

The fix: give each tracked 1:1 **its own scheduled job**, timed to fire
roughly 15–20 minutes after that specific person's meeting is expected to
end (leaving the notetaker time to finish processing). Compute this per
person from their actual recurring meeting time on the calendar - don't
assume every 1:1 is at the same time of day, and don't assume weekly when it
might be biweekly (check for gaps between instances; a series that looks
weekly at a glance can turn out to repeat every 14 days).

**This job only earns its keep for two of the three note-capture patterns
from Step 2.** Its whole reason to exist is racing a time-sensitive
artifact - a notetaker note that becomes available shortly after the
meeting, or a "how'd it go" question that needs an answer while the meeting
is still fresh. Someone on the **self-typed-doc pattern** has no such
artifact: their doc gets updated whenever they get to it, not faster because
something polled 20 minutes after the meeting ended. **Don't create this job
for that person at all** - the shared daily job's tracker sync (7c) already
covers them completely on its own. Skipping it isn't a compromise; it's the
correct design, and creating it anyway just produces a job that silently
no-ops forever.

For the other two patterns, each job should, in a fresh/memory-less run:

1. Confirm today's meeting for that person actually happened (check the
   calendar) - if not, stop silently. For a biweekly 1:1, an off-week is
   expected and not an error.
2. Check whether a note for today has already been captured (e.g. by
   checking the draft's current date-stamp) so a re-run or a late-firing
   duplicate doesn't double-post.
3. Get the note:
  - **Notetaker in play:** look up the matching note for today. If it
     isn't ready yet, post a short "still waiting on the note" message and
     stop - don't fabricate content, and don't stay silent either (see
     "Common things that go wrong").
  - **Handwritten / no digital notes:** post a short direct question once
     - "How'd the 1:1 with <Name> go? Anything to flag or follow up on?" -
     and stop. Don't try to poll for the reply from *this* job: it only
     fires again in a week (or two), which is much too slow to catch a
     same-day or next-day answer. Checking for and consuming that reply is
     the shared daily job's responsibility instead (7c) - it already runs
     every day, which is the cadence this actually needs.
4. Format it using the notetaker-formatting template (Step 4/references) and
   deliver it as a first draft only - never write it into the permanent
   tracker directly (see Step 4's trust boundary).

This means a manager with 6 direct reports ends up with 6 small, cheap,
precisely-timed jobs instead of 1 job trying to serve 6 different schedules
at once. That's the right trade - each job is trivial to reason about and
only ever fires when its specific person's meeting could plausibly have just
ended.

### 7b - Where the draft note gets delivered

A plain chat message works, but if the delivery channel is Slack, consider a
**dedicated Canvas as a review-queue staging area** instead: one section per
person, each holding only the *latest* unreviewed draft (overwritten, not
appended, each time a new one lands). This keeps the channel itself from
filling up with long note dumps - the channel gets a short pointer message
("draft ready for review: <canvas link>") while the canvas holds the actual
content. It's a good fit specifically because these drafts are disposable
staging content, not a permanent record (the user's own doc is the permanent
record) - so overwrite-in-place is the correct behavior, not data loss.

### 7c - A shared daily job for the things that are genuinely fine as a batch

Unlike notes-capture, these three things don't race against a specific
meeting's end time, so one daily job (running once, early morning, in the
user's timezone) can safely handle all of them for everyone:

- **Sync the tracker** from whatever the user's own notes currently say (not
  from the notetaker) - see Step 4's trust boundary. For anyone on the
  self-typed-doc pattern, this step is their *only* capture mechanism (they
  have no per-person job at all - see 7a) so make sure it runs for them
  unconditionally, not just as a fallback. Don't restrict the extraction to a
  literally-labeled "Action items"/"Next Steps" section - read the whole
  entry and infer real commitments and follow-ups by meaning, since plenty of
  people's real notes leave that heading blank or skip it entirely while the
  actual ask is answered conversationally elsewhere (a Q&A-style "what's one
  thing I can do to support you?" answer is a classic hiding spot). See the
  "Common things that go wrong" section below.
- **Check for answered capture-prompts.** For anyone on the handwritten
  pattern, check whether their per-person job's "how'd it go" question (7a
  step 3) has since been answered - this job runs daily regardless of that
  person's meeting cadence, so it's the right place to catch a reply that
  comes in a day or two later, not the per-person job itself (which won't
  fire again until their next 1:1). Once answered, treat the reply as the
  note and fold it into the tracker sync above.
- **Heads-up reminder** for any 1:1 coming up in N days, listing what's still
  open for that person.
- **Same-day briefing** before any 1:1 happening today, drawn from the most
  recent notes entry and open tracker items.

### 7d - Optional weekly job

Nudges the user ahead of their recurring review block (if they have one)
with a rollup of open items across everyone.

### 7e - Optional roster-reconciliation job

1:1s get added and dropped over time - a new report joins, someone's 1:1
moves to a different day, a relationship ends. Rather than requiring the
user to remember to come back and ask for the automation to be updated,
offer a periodic job that keeps the roster of tracked 1:1s in sync with the
calendar on its own. The critical design constraint: **this job proposes,
it never silently self-mutates.** It should never create or disable another
job without a human confirming first - an automation that quietly starts
tracking (or stops tracking) a relationship on its own is a good way to
either leak the wrong information to the wrong channel or silently lose
coverage of a real 1:1. Concretely:

- Periodically re-scan the calendar for recurring 1:1-shaped events (same
  heuristic as Step 1) and diff against the current list of tracked people.
- For anything new: post a proposal ("Found what looks like a new 1:1 with
  <Name>, <schedule>. React ✅ to this message to add it.") rather than
  creating its job immediately.
- For anything that's disappeared from the calendar for a while (a few
  missed instances, not just one skipped week - biweekly and irregular
  1:1s naturally skip weeks): post a proposal to stop tracking it, again
  gated on a reaction.
- On its next run, check for that confirmation reaction before actually
  creating/disabling anything.
- **Prefer disabling a job over deleting it** for removals - disabling is
  reversible and preserves the job's configuration and history if the
  relationship resumes later (e.g. someone returns from leave), where a
  delete is not.

This job is optional - a lighter-weight alternative for a user who doesn't
want yet another automation is to just mention, when handing off the setup,
that they can ask for a new person to be added or an existing one removed at
any time, and you'll take care of updating the relevant jobs then.

Default to **one shared reconciliation job scanning the whole roster** -
simpler, and fine for most managers. Offer a **per-person reconciliation
check** instead (or in addition) as an option, not a default, for cases
where it genuinely earns its keep: a large roster where one shared scan gets
noisy or slow, or a specific relationship with an irregular enough cadence
that it benefits from being watched on its own schedule rather than lumped
into a periodic sweep. Same principle as everywhere else in this skill - the
standard shape, applied at whatever granularity the situation calls for, and
the user's call which they'd rather have.

### Filling in the details

Every value these jobs need - names, doc links, channel/tracker IDs,
timezone, the reminder lead time, whether a notetaker is in play - must be
filled in literally in the job's stored instructions. Scheduled jobs typically
fire as a fresh, memory-less run each time: they can't see this conversation,
so nothing here can be left implicit or "inferred from context" the way it
can in an interactive turn. Write the instructions as if handing them to a
new hire who's never seen this conversation.

## Step 8 - Confirm, and offer a test firing

Summarize what got built (tracker link, channel/DM choice, calendar block if
any, job schedule) back to the user in plain language. If your environment
supports firing a scheduled job on demand, offer to do that once as a live
test rather than waiting for the first real firing - it's the fastest way to
catch a wrong ID or a misjudged date filter while the user is still around
to look at the result with you. If a structured-question tool is available,
use it here too - e.g. "Looks good, go ahead" / "Run a test firing first" /
"I want to change something" as the offered choices - rather than asking the
user to type out a free-form reply to a yes/no question.

## Common things that go wrong (and how to avoid them)

- **Trusting notetaker attribution over the user's own corrected notes.**
  Covered above - this is the one to get right.
- **A single daily batch job for notes-capture.** Covered in Step 7a - it
  silently adds up to a day of latency for any meeting that happens later
  in the day than the batch's own run time. If you notice a user saying
  "I had a 1:1 but never got the note," check whether this is the cause
  before assuming something else is broken.
- **Assuming every recurring 1:1 is weekly.** Some are biweekly or on an
  irregular cadence. Check actual gaps between recent instances on the
  calendar rather than assuming from a single occurrence, and make sure
  the relevant job knows to no-op silently (not error) on an off-week.
- **Assuming a connector's permission grant will just be there for a
  scheduled run.** Covered above - exercise every tool interactively during
  setup, and again for anything added later, before folding it into a
  scheduled job.
- **A permission grant that quietly expires or gets revoked later.** Setup
  isn't the only time this can bite - a token can lapse months in. If a real
  firing hits a permission error, that's not something the job can fix
  itself; say so plainly in its output (same principle as "silent partial
  success" below) rather than swallowing the error, so the user finds out
  from a message instead of from a multi-week gap in their notes.
- **Creating a per-person notes-capture job for someone on the self-typed-doc
  pattern.** Covered in Step 7a - that job has nothing time-sensitive to do
  for them and just becomes a permanent no-op. The shared daily job's
  tracker sync already covers this pattern completely.
- **Having the per-person job poll for a reply to its own "how'd it go"
  question.** Covered in Step 7a/7c - that job doesn't fire again until the
  next 1:1 (a week or two later), far too slow to catch a reply. The daily
  job should own checking for and consuming that reply.
- **Assuming everyone either uses an AI notetaker or has nothing at all.**
  Handwritten notes and self-typed docs are common and legitimate - see Step
  2's note-capture patterns. Defaulting to "wait for Granola" for someone
  who takes notes on paper means the automation just never produces
  anything, silently.
- **A roster-reconciliation job that self-mutates.** It should only ever
  propose adding/removing a tracked 1:1 and wait for confirmation (Step 7e)
  - never create or disable jobs unilaterally.
- **Assuming a connector can edit files it can only read/create.** Test this
  assumption, don't infer it from the connector's name.
- **Hardcoding today's discovered people/docs/IDs into a "one size fits all"
  template** if you're packaging this for someone else's org later - every
  identifier belongs in the parameters, not the prose.
- **Being noisy.** A job that posts "nothing pending" every single day for
  a report where the user rarely has open items becomes something people
  stop reading. Consider making low-noise mode (skip the message entirely
  when there's nothing to report) the default, and only mention it stayed
  quiet if the user asks why they haven't heard anything.
- **Silent partial success.** If the notetaker has no matching entry for a
  meeting that clearly happened, or a doc can't be reached, say so in the
  job's output rather than saying nothing - a manager who never got a note
  for a real meeting needs to know it didn't happen, not just experience an
  absence.
- **Depending on a literal "Action items"/"Next Steps" heading to find action
  items.** This is a real, observed failure mode, not a hypothetical one: a
  lot of people's actual notes either leave that section blank/near-empty (a
  spreadsheet link, a stray dash) or don't use that heading at all, while a
  genuine ask for the user is sitting in plain sight elsewhere in the same
  entry - very often the answer to a Q&A-template question like "what's one
  thing I can do to support you?" ("approve my leave," "ease off on meeting
  frequency for a bit"). If the sync job only scans for a specifically-labeled
  list, these get silently missed and the tracker quietly goes stale even
  though the job is "running successfully" every day. Extraction needs to
  read the whole entry and infer commitments semantically, the same way a
  person skimming the notes would, not pattern-match on a heading or an
  explicit owner tag. A job that runs without errors every day but stops
  finding new items is a stronger signal something's wrong with *how* it
  reads notes than that people have simply stopped generating action items.
- **Some notes only capture agenda topics, not what was decided.** A doc
  entry that lists "promo timeline," "Series B next steps," or similar as
  topic headings, with no note of what was actually agreed, isn't sparse
  because nothing happened - real decisions were made in the meeting, they
  just never got written into the notes. If a notetaker draft for that same
  meeting exists in the delivery channel, its own "Next Steps" section is a
  legitimate fallback source (see the "FALLBACK" paragraph in the daily job
  template) - but tag anything pulled from it distinctly (e.g. "via
  {{NOTETAKER_TOOL}} draft - verify") since it skips the user's own
  correction step. Don't silently treat an agenda-style entry as "nothing to
  sync" just because it isn't a narrative.

## Reference

- `references/scheduled-task-templates.md` - parameterized prompt text for
  the per-person notes-capture job, the shared daily sync/reminders job, the
  optional weekly job, the optional roster-reconciliation job, and the
  notetaker-formatting template, ready to fill in with the specifics
  discovered during setup.
