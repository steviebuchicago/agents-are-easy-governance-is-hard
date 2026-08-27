# Cowork Skills

Two working skills, and the reasoning about when a skill is the right answer.

## What a skill is

A skill is a folder with a `SKILL.md` file in it. The file has a short YAML header — a `name` and a `description` — and then instructions written in plain English.

Claude reads the descriptions of the skills available to it. When what you ask matches one, it loads that skill's instructions and follows them. You never invoke a skill by name; you describe the job the way you would to a colleague.

That makes the `description` the most important line in the file. It is not documentation, it is the trigger. A vague description means the skill never fires, and you conclude it does not work when in fact it was never asked.

The body is where the value is, and the craft is constraint. "Summarise these updates" produces something. "Maximum 500 words, five items in the priority section, every item carries a quote, never name an owner who is not in the source" produces something you can rely on. Encouragement is not instruction. Wherever the output could go wrong, write the rule.

## The two here

**[`skills/weekly-portfolio-digest/`](skills/weekly-portfolio-digest/SKILL.md)** — takes a set of status updates and produces a prioritised digest that leads with what needs a decision, reports what moved, and names what went silent. Ranking is a fixed rule, not a judgement call, and it will not invent an owner, a date, or a status.

**[`skills/meeting-notes-to-actions/`](skills/meeting-notes-to-actions/SKILL.md)** — turns raw notes or a transcript into a table of actions with owners, dates, and a source quote on every row. Anything without a named owner is flagged rather than assigned to whoever seems likely.

Both are built on the same idea: an honest gap beats a confident guess.

## Installing them

The shape is the same everywhere: **a directory named for the skill, containing `SKILL.md`**. Copy the whole directory, not just the file.

- **For yourself, everywhere** — `~/.claude/skills/<skill-name>/`.
- **For one piece of work** — `.claude/skills/<skill-name>/` inside the folder you are working in.
- **For a team** — the same folder goes into a plugin, which is how you distribute skills to people who should not be copying directories around.

Check it took: ask Claude what skills it has. If yours is not listed, the location is wrong. If it is listed but never fires, the description is wrong — rewrite it in the words a colleague would use, not the words you would put in a document title.

Edit them freely. The second version of a skill, written after you watch the first get something wrong, is always the better one.

## Skill or code?

**A skill, when** the output is read by a person, the input shape varies, being mostly right is fine because the reader is the check, and the rule you are encoding is easier to write than to specify.

**Code, when** the output feeds another system, the result must be identical every run, the work is arithmetic or joins or sorting, or nobody reads it before something acts on it.

The failure mode worth naming: using a skill to do a job a spreadsheet formula does perfectly. You are paying for nondeterminism and getting nothing for it.

## The governance part

A skill inherits whatever governance the platform provides. You do not write permissions, audit records, or spending caps — which is why this tier is fast, and what you give up for the speed.

The deal holds as long as a human reads the output before anything acts on it. The moment it stops holding, you have moved tiers whether you meant to or not, and the [Governance Checklist](../docs/04-governance-checklist.md) starts applying to you.

More on choosing: [Cowork vs Claude Code vs Agent SDK](../docs/01-cowork-vs-code-vs-agents.md).
