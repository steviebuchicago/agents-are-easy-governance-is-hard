<img src="docs/images/hero.png" alt="Agents are easy. Governance is hard." width="100%">

# Agents Are Easy. Governance Is Hard.

**A working agent takes an afternoon. Getting it allowed to run takes the rest of the quarter.**

This repo is for the person who has just been asked to "do something with AI agents" and wants to know what they're actually signing up for. It covers the three ways to work with Claude — **Cowork**, **Claude Code**, and the **Agent SDK** — when each one is right, and the part every tutorial leaves out.

The centerpiece is two examples that do **exactly the same thing** — byte-for-byte identical output. One is 40 lines of executable code. The other is 325. That difference is the entire subject of this repo.

---

## The one-paragraph version

Getting a language model to read a document, decide something, and take an action is genuinely easy now. You can do it in an afternoon, and it will work, and you will be pleased. Then you try to put it somewhere real — where it touches customer records, or spends money, or sends things to people — and you discover the actual job. Who approved this? What can it reach? What happens when it's wrong? How would anyone know? What did it do last Tuesday, and can you prove it?

None of those are model problems. All of them are engineering problems, and they're the ones nobody blogs about.

---

## Start here

**Never used any of this?** → [Your First Hour](docs/02-your-first-hour.md) — from nothing to a working agent, with the honest version of what you just built.

**Deciding which tool?** → [Cowork vs Claude Code vs Agent SDK](docs/01-cowork-vs-code-vs-agents.md) — a real decision guide, not a feature matrix.

**Already have a demo and need to ship it?** → [The Governance Gap](docs/03-the-governance-gap.md) and the [Governance Checklist](docs/04-governance-checklist.md).

**Want to see the difference, not read about it?** → [`examples/`](examples/) — the same agent, twice.

---

## Three ways in

<img src="docs/images/three-ways-in.png" alt="Three ways in: Cowork, Claude Code, Agent SDK" width="100%">

They are not three products competing for the same job. They are three different relationships between you and the work.

| | **Cowork** | **Claude Code** | **Agent SDK** |
| --- | --- | --- | --- |
| **You are** | Delegating a task | Working alongside it | Building a product |
| **Who uses it** | Anyone | Anyone comfortable in a terminal | Engineers |
| **You write** | A skill, in plain English | Prompts, and it writes the code | An application |
| **It runs** | When you ask, or on a schedule | While you're there | Unattended, at scale |
| **Time to useful** | Minutes | Minutes | Days |
| **Governance you get** | Whatever the platform provides | Whatever the platform provides | **Whatever you build** |

That last row is the important one, and it's inverted from what people expect. **The more control you take, the more responsibility you inherit.** The Agent SDK gives you the most power and the least safety net — every permission boundary, every audit record, every spending cap is something you write yourself.

Most teams should start one step to the left of where their instinct says.

Full guide: [Cowork vs Claude Code vs Agent SDK →](docs/01-cowork-vs-code-vs-agents.md)

---

## The two examples

The whole argument of this repo, in two directories.

### [`01-hello-agent`](examples/01-hello-agent/) — 40 lines, and it works

Reads a folder of documents, extracts structured data, writes a CSV. Run it and it does the thing. This is the afternoon version, and there is nothing wrong with it — it is a completely reasonable piece of software.

### [`02-governed-agent`](examples/02-governed-agent/) — same job, 8x the code

Identical capability. Identical output. What's added:

- **Permissions** — an explicit allowlist of what it may touch, denied by default
- **Budget caps** — it stops rather than running up a bill
- **Audit log** — every decision, with the prompt version that produced it
- **Shadow mode** — it can run for real and write nothing, logging what it *would* have done
- **A human gate** — going live is a decision someone makes, not a flag someone flips

Read them side by side. The second one isn't smarter — run both and you get identical CSVs, verified byte for byte. It's *accountable*, and that's what the extra 285 lines buy.

---

## The gap

<img src="docs/images/the-gap.png" alt="From 'it works' to 'in production'" width="100%">

Note that the bridge in that picture isn't finished. That's not a mistake in the image — it's the most accurate thing in this repo.

Almost every AI agent project that stalls stalls **here**, and it stalls for the same reason every time: the demo was built to prove the capability, and proving the capability is not the same as earning the right to run. The evidence a risk committee needs doesn't exist, because nobody built the thing that would have produced it.

The way out is not a better demo. It's building the bridge on purpose, early, as part of the architecture rather than a phase at the end.

[The Governance Gap →](docs/03-the-governance-gap.md)

---

## What governance actually means

The word sounds like paperwork. It isn't. It's five concrete mechanisms, and they're all code.

<img src="docs/images/five-gates.png" alt="Five things between your agent and production" width="100%">

| Gate | The question it answers | Without it |
| --- | --- | --- |
| **Permissions** | What may it touch? | It can reach anything its credentials can |
| **Budget** | What may it spend? | A retry loop becomes an invoice |
| **Audit** | What did it do, and why? | "We think it worked" |
| **Shadow** | Is it right, on real traffic? | You find out in production |
| **Human gate** | Who said yes? | An engineer merged a PR |

Each one is maybe fifty lines. None of them is hard. **The hard part is that they have to exist before you need them**, and the moment you need them is always after you've shipped.

[Governance Checklist →](docs/04-governance-checklist.md) — the copy-pasteable version.

---

## The five things people get wrong

**1. Starting with the Agent SDK.** If a Cowork skill would do the job, use a Cowork skill. Reaching for the SDK first means writing your own permissions, audit, and retry logic to accomplish something that needed none of it.

**2. Treating shadow mode as a testing phase.** It's an architectural property. If "log what you would have done instead of doing it" is something you add later, you will not add it — it requires threading a flag through every call site and someone will miss one.

**3. Confusing "the model was right" with "the system was right."** The model returning a correct answer is one component working. Whether the right thing happened depends on routing, permissions, error handling, and what occurs when the model is *not* right.

**4. Building the happy path first.** The interesting behavior is all in refusal: what happens on an ambiguous input, a partial failure, a timeout mid-write. Build those first and the happy path falls out.

**5. Assuming autonomy is the goal.** An agent that handles 70% of cases and cleanly escalates the other 30% is worth vastly more than one that attempts 100% and is quietly wrong on 8%. Escalation is a feature.

---

## Repo layout

```
agents-are-easy-governance-is-hard/
├── docs/
│   ├── 01-cowork-vs-code-vs-agents.md   which tool, and why
│   ├── 02-your-first-hour.md            zero to working
│   ├── 03-the-governance-gap.md         why projects stall
│   └── 04-governance-checklist.md       the practical list
├── examples/
│   ├── 01-hello-agent/                  40 lines, works
│   └── 02-governed-agent/               same job, accountable
└── cowork/skills/                       two no-code skills
```

---

## Prerequisites

Python 3.11+ and an Anthropic API key for the examples. Nothing else. The Cowork skills need no code at all.

```bash
git clone https://github.com/steviebuchicago/agents-are-easy-governance-is-hard.git
cd agents-are-easy-governance-is-hard/examples/01-hello-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python agent.py
```

Then read [`examples/02-governed-agent`](examples/02-governed-agent/) and see what you were missing.

---

## Who this is for

Engineers who've been handed an AI mandate. Technology leaders who need to know what to ask for. Anyone who has built a demo that impressed people and then could not get it approved.

It is deliberately basic. If you want the deep version — agent fleets, document pipelines, regulated-industry deployment — that's the companion repo: [claude-agents-for-wealth-management](https://github.com/steviebuchicago/claude-agents-for-wealth-management).

---

## License

MIT — see [LICENSE](LICENSE).

## About

Built by **Stephen A. Barry** — Chief Technology Officer in asset and wealth management, and Professor of AI in the University of Chicago's MS in Applied Data Science.

I've spent twenty-five years in financial services technology and I now teach the applied version of this at the graduate level. I wrote this repo because the gap between "the agent works" and "the agent is allowed to run" is where I watch most projects die, and almost nobody writes it down.

[LinkedIn](https://www.linkedin.com/in/stevebarry25/) · [GitHub](https://github.com/steviebuchicago)
