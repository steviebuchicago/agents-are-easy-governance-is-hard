<img src="images/three-ways-in.png" alt="Three ways in" width="100%">

# Cowork vs Claude Code vs the Agent SDK

Every comparison of these three turns into a feature matrix, and a feature matrix is useless here: all three run the same models and can technically do most of the same things. The question is not what each one *can* do. It is what relationship you want to have with the work — and, downstream of that, how much of the safety net you are willing to build yourself.

**One question resolves most of the argument:** how long does this work need to run without you in the room, and who is accountable when it is wrong?

- "It doesn't, and me" → **Cowork**
- "An afternoon, and me" → **Claude Code**
- "Indefinitely, and my employer" → **the Agent SDK**, and you should read the [Governance Checklist](04-governance-checklist.md) before you write a line

The rest of this document is the detail behind that.

---

## Claude Cowork

**What it is.** You describe a job in plain English and Claude does it, in a workspace that can see the folders and tools you have connected to it. When a set of instructions is worth keeping, you save it as a *skill* — a folder containing a `SKILL.md` file, which Claude loads when a request matches its description. No build step, no repository.

**Who it's for.** Anyone. The person who assembles the Monday report, the analyst with a folder of PDFs, the operations lead reconciling two spreadsheets at month end. No terminal, no Python.

**What you write.** Prose. A good skill reads like a brief to a competent new joiner: here is what the input looks like, here is exactly what the output must look like, here is what to do when something is missing. The craft is entirely in the constraints — see [`../cowork/`](../cowork/) for two worked examples.

**How it runs.** When you ask, or on a schedule you set. The output lands somewhere you can see it.

**How it fails.** Legibly. It misreads an input, or follows the instruction you actually wrote rather than the one you meant, and hands you something plausible and wrong. You catch it because a human reads the output. That human is the reason this tier is safe; remove the reader and the safety goes with them.

---

## Claude Code

**What it is.** Claude in your terminal, with your filesystem, your repository, your commands. You describe what you want; it reads files, writes code, runs it, reads the error, fixes it, and shows you the diff. You are in the loop at every meaningful step.

**Who it's for.** Anyone comfortable in a terminal. The real bar is "can install Python and read a diff," which more people clear than will admit it.

**What you write.** Prompts and corrections. The artifact is code and you own it afterwards. That is the honest difference from Cowork: Cowork gives you an answer, Claude Code gives you a thing that produces answers.

**How it runs.** While you are there.

**How it fails.** Quickly and visibly. It refactors something you did not ask it to touch, or runs against the wrong directory, and you have a mess in your working copy — which is why you use git and read the diff. The genuinely dangerous version is leaving it running with broad permissions on a machine that can reach something real.

---

## The Agent SDK

**What it is.** A library for building applications in which Claude is one component. You write the loop, the tools it may call, the error handling, the retries, the limits. Software engineering, with a model in the middle.

**Who it's for.** Engineers building something other people or other systems will depend on.

**What you write.** An application. The prompts are maybe a tenth of it; the rest is plumbing, and the plumbing is the job.

**How it runs.** Unattended, at scale, on a schedule or in response to events, over data nobody looked at first.

**How it fails.** Silently, at three in the morning, repeatedly. No human is reading the output — that is the entire point of building it — so a wrong answer propagates into whatever consumes it. This is why the five gates are not optional here. They are the replacement for the person who used to read the output.

---

## The thing that actually changed

Notice what did *not* change across those three: capability. What changed is who is holding the failure. In Cowork, the platform holds most of it and you hold the last mile by reading the result. In Claude Code, you hold it and you know you are holding it, because you are sitting right there. In the SDK, you hold all of it and nobody is sitting there.

**Every unit of control you take is a unit of governance you inherit.** That is the inverted responsibility the [README](../README.md) opens with, and it is why most teams should start one tier to the left of where their instinct points.

---

## If you're doing X, use Y

**A report you produce every Monday from the same handful of sources** → **Cowork skill.** What needs capturing is the *instruction*, not the code. Write it once, run it weekly, edit the prose when the format changes. The Python version becomes a small unmaintained application by the end of the quarter, and whoever inherits it cannot read the intent back out of it.

**A one-off cleanup of a messy dataset — 4,000 rows, inconsistent dates, three spellings of every vendor** → **Claude Code.** It is exploratory, you will change your mind four times about what "clean" means, and you want the intermediate results in front of you. The right answer here is deterministic code — a mapping table, a regex, a join — that you can re-run and diff. Claude Code writes that code rather than being it, and that distinction matters more than it sounds.

**A customer-facing service that answers questions about someone's account** → **Agent SDK**, and budget most of your effort for the parts that are not the model. It runs unattended, touches records belonging to someone who is not you, and the first genuinely wrong answer is an incident rather than a bug. If you cannot yet name what it may read and what it may never write, you are not ready to start.

**Automating something across your own files** — renaming, reconciling two folders, pulling figures out of a stack of statements → **Cowork.** The data is yours, the blast radius is a directory you control, and you will look at the result. This is the best first use of any of this, and the one most people skip past.

**A workflow ten colleagues need to run the same way** → **Cowork skill, shared.** The alternative is ten people running ten slightly divergent copies of your script, one of them still on last year's template. A skill is a readable, shared definition of how we do this thing, and the people who depend on it can trust it without reading code. If it has to be embedded in a system rather than run by a person, see the unattended case below.

**Building a tool, migrating a codebase, writing tests for a service you inherited** → **Claude Code.** The work is code, the review is a diff, you need to be in the loop. None of this needs an agent framework, and reaching for one adds a runtime you then have to operate.

**Something that must run at 03:00 with nobody watching, feeding a system downstream** → **Agent SDK.** Unattended plus consumed-by-a-machine is precisely where the five gates earn their cost. If a human reads the output over coffee, a scheduled Cowork task is a real option and far cheaper. The test is whether a wrong answer gets noticed *before* something acts on it.

**Anything that spends money, sends external messages, or writes to a system of record** → **the SDK tier**, however simple the logic is. The governance requirement sets the tier, not the technical one. A ten-line agent that can email clients is a harder problem than a thousand-line agent that writes a CSV to your desktop.

---

## The migration path

Start in Cowork. Not as a beginner's tier — as a probe. Twenty minutes there teaches you what a fortnight of building would also have taught you, and a surprising share of the time you discover the real requirement was a saved search and a template. Then graduate when the work tells you to, not when the architecture diagram does.

**You have outgrown Cowork when:**

- You paste the same correction into the skill every week. A repeated correction is a deterministic rule, and deterministic rules belong in code.
- The output feeds a system rather than a person, so nothing reads it before it is acted on.
- It has to run against data you are not allowed to see, or at a time you are not there.
- Someone asks what it did in March and "it was in my workspace" is not an acceptable answer.

**You have outgrown Claude Code when:**

- Someone who is not you needs to run it, and you have started writing them instructions.
- It needs to run without a terminal open.
- You are writing the same wrapper for the third time.
- You have begun building a queue, a retry loop, or a place to put the logs. You are writing the SDK version already; do it deliberately rather than by accident.

**And the migration nobody makes:** downward. If your SDK application is one prompt against one folder, and the gates you wrote are boilerplate nothing has ever exercised, you built a tier too high. Deleting it and writing a skill is a legitimate outcome, and cheaper than maintaining it for three years.

---

## Reasons not to use each one

**Not Cowork when** the output must be byte-identical every run; when the task is arithmetic, joins, or sorting that deterministic code does better and cheaper; when nobody reads the result before it is used; or when you need an audit trail with properties the platform does not give you. Paying for nondeterminism to do a job a SQL query does perfectly is the most common misuse of this tier.

**Not Claude Code when** you need distribution. It is not a delivery mechanism — "it works on my machine, run these six commands" is not a product, and the governance model is you, personally, watching. Also not when the thing it can reach is larger than the thing you intend it to change.

**Not the Agent SDK when** what you actually needed was a report. You inherit every permission boundary, every audit record, every spending cap and every retry policy, and a fair share of those days goes into rebuilding a worse version of scheduling that already existed. Reach for it when unattended operation or system integration is a real requirement, not when it sounds more serious.

---

## Where to go next

Never done any of this → [Your First Hour](02-your-first-hour.md). Have a demo you cannot get approved → [The Governance Gap](03-the-governance-gap.md). Ready to build the bridge → [Governance Checklist](04-governance-checklist.md), plus [`../examples/01-hello-agent/`](../examples/01-hello-agent/) and [`../examples/02-governed-agent/`](../examples/02-governed-agent/) side by side.
