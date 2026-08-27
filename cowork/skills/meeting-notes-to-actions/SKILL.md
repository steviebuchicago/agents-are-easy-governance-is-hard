---
name: meeting-notes-to-actions
description: Turn raw meeting notes or a transcript into a table of actions with named owners and due dates, flagging every action that has no clear owner. Use when asked to pull the actions out of these notes, extract action items, write up the meeting, turn a transcript into a to-do list, work out who owns what after a meeting, or find the follow-ups. Works from scrappy handwritten-style notes, a bulleted agenda, or a full transcript.
---

# Meeting Notes to Actions

Your job is to extract what was actually committed to, not to produce a tidy-looking list. A list that is 80% right and 20% invented is worse than a short list plus honest gaps, because the reader cannot tell which rows to trust.

## Before you start

Establish the **meeting date** and the **attendee names**. Both are usually in the notes. If the meeting date is not stated and the user has not supplied it, ask once. If you still do not have it, **do not convert any relative date** — reproduce every "next Tuesday" and "end of the month" verbatim and note it in *Could not determine*.

## What counts as an action

An action passes all three tests:

1. Someone is expected to do something
2. It is a change of state, not a discussion
3. It was said as a commitment or an instruction, not as an idea

Things that are **not** actions, and where they go instead:

- A decision already made → *Decisions*
- A question raised and left open → *Open questions*
- Context, opinion, background, or an FYI → leave it out entirely
- "Someone should probably look at X" → *Needs an owner*, not *Actions*

## Output shape

Produce exactly this, in this order. No summary paragraph before or after unless the user asks for one.

```
# Actions — [meeting name or topic], [meeting date]

## Actions
| # | Action | Owner | Due | Said |
| --- | --- | --- | --- | --- |
| 1 | [verb-first, ≤ 20 words] | [name] | [date or "Not stated"] | "[≤ 12-word quote]" |

## Needs an owner
[Actions with no explicitly named owner. Same columns, Owner left blank.]

## Decisions
- [≤ 15 words each. Only decisions stated as made.]

## Open questions
- [Question, and who raised it if stated.]

## Could not determine
- [Ambiguities, unconverted relative dates, anything you chose not to guess at. Write "Nothing." if empty.]
```

Sort *Actions* by due date ascending, undated last, then by owner.

## Hard rules

**Never invent an owner.** Use only a name that appears in the notes as the person taking the item. Do not infer ownership from seniority, from who spoke most, from whose area it falls in, or from who convened the meeting. If the notes assign work to a role or a team rather than a person — "legal to review", "the vendor confirms" — write it exactly as written and append `(role, not a person)`. Everything else with no named owner goes to *Needs an owner*.

**Never invent a date.** Use a date only when it is stated, or when it derives unambiguously from a stated relative date *and* you know the meeting date. Show derived dates with their source: `3 Sep (from "next Thursday")`. Anything else is `Not stated`. An action with no date is a real and common outcome; do not paper over it.

**Never change the strength of a commitment.** "Will try to" is not "will". "Should" is not "must". "If we get time" stays in the row. Tidying the language into confident prose changes what was agreed, which is the single most damaging thing this skill could do.

**One action per row.** Do not merge two distinct commitments to make the list shorter, and do not split one commitment into steps to make it look thorough. If the same action is stated twice, list it once and quote the clearer mention.

**Do not fill the table.** If the notes contain three actions, the table has three rows. If they contain none, write `No actions were committed to in these notes.` and go straight to *Decisions* and *Open questions*.

**When something is ambiguous, say so rather than resolving it.** An action whose owner, deliverable, or deadline is genuinely unclear belongs in *Needs an owner* or *Could not determine* — not in *Actions* with your best guess quietly filling the gap.

## Before you deliver

- Every name in the Owner column appears in the notes
- Every date is quoted or shown with its derivation
- Every row has a quote from the source, and the quote supports the row
- No row contains a word about commitment strength that the notes do not contain
- Items with no owner are in *Needs an owner*, not assigned to the meeting organiser
- *Could not determine* is present, even if it says "Nothing."

Close with one line stating the counts: actions, unowned actions, decisions, open questions. Nothing more.
