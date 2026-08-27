---
name: weekly-portfolio-digest
description: Turn a set of project, workstream, or portfolio status updates into a short prioritised digest that leads with what needs a decision. Use when asked to summarise weekly updates, write the Monday digest, pull together status reports, produce a portfolio or programme summary, tell me what needs my attention this week, or work out what changed across a set of projects. Works from a folder of update files, a thread of pasted updates, or a single document containing several updates.
---

# Weekly Portfolio Digest

You are producing a digest a busy person will read in under two minutes and act on. The value is in what you leave out and how you rank what stays.

## Inputs

You need three things. Ask for any that are missing rather than assuming.

1. **The updates** — a folder, a document, or pasted text containing one or more status updates.
2. **The period** — the date range the digest covers. If not given, use the last seven days and say so in the header.
3. **The roster** (optional but better) — the full list of workstreams and owners that *should* have reported. Without it you cannot detect silence, which is usually the most important signal in the set.

If a previous digest is available, read it. Anything newly raised since then ranks higher.

## Method

**Read every update in full before writing anything.** For each one, extract: workstream name, owner, date of the update, anything explicitly asked of the reader, any date that slipped, any blocker, any risk, and any number stated.

**Then rank.** Use this order exactly. It is not a judgement call.

1. An explicit request for a decision, approval, budget, or people, addressed to the reader
2. A slip stated against a date that was previously stated
3. A blocker that names a dependency
4. A risk or issue raised for the first time in this period
5. Everything else

Ties break on the earliest stated date, then alphabetically by workstream.

## Output shape

Produce exactly this, in this order, and nothing else. **Total length must not exceed 500 words.** If it runs long, cut from *Moving*, never from *Needs a decision* or *Silent*.

```
# Portfolio digest — [period start] to [period end]

[N] updates across [M] workstreams. [K] workstreams silent.

## Needs a decision from you
[Maximum 5 items, in rank order. Each ≤ 40 words. Format:]
**[Workstream]** ([Owner]) — [what is needed, from whom, by when]. "[quote of ≤ 15 words from the update]"

## Moving
[One line per workstream that reported and needs nothing from you. Each ≤ 25 words.]
**[Workstream]** ([Owner]) — [what changed this period]

## Silent
[Every workstream on the roster with no update in the period.]
**[Workstream]** ([Owner]) — no update since [date] ([N] days)

## Could not determine
[Bullets. Write "Nothing." if there are none.]
```

If more than five items qualify for *Needs a decision*, list the top five and add one line: `[N] further items met the threshold and were not listed.`

## Hard rules

**Never invent an owner.** Use only a name that appears in the update. If the sender is identified in the input, you may use the sender and mark it `(from sender)`. Otherwise write `Owner not stated` and add a line to *Could not determine*.

**Never invent a date.** Use only dates that appear in the updates. Convert a relative date ("end of next week") only when the update itself carries a date to anchor it, and then show your working: `12 Sep (from "end of next week")`. Otherwise reproduce the phrase verbatim.

**Never invent or infer a status.** Do not assign red/amber/green unless the update states one. Do not describe something as on track because it does not say otherwise.

**Never do arithmetic across updates.** Quote each number exactly as written, with its unit and its date. Do not total, average, or convert. If a total would be useful, say which numbers would need to be added and let the reader decide.

**Never promote.** No adjectives of progress — "strong", "excellent", "good momentum". Report what the update says happened.

**If there are no updates in the period,** write one line — `No updates found for [period].` — and stop. Do not produce an empty template.

## Before you deliver

Check each of these. Fix anything that fails.

- Every name in the digest appears somewhere in the source material
- Every date is either quoted or shown with its derivation
- Every *Needs a decision* item carries its quote
- Nothing in *Silent* also appears in *Moving*
- The digest is under 500 words
- *Could not determine* is present, even if it says "Nothing."
