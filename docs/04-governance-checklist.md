<img src="images/five-gates.png" alt="Five things between your agent and production" width="100%">

# Governance Checklist

The copy-pasteable one. Five gates, each with the questions to answer, what finished looks like, and a checklist to drop straight into a ticket.

None of these is hard — each is roughly fifty lines. The difficulty is that they have to exist *before* you need them, and the moment you need them is always after you shipped.

---

## Gate 1 — Permissions

**What it is.** An explicit allowlist of what the agent may reach and what it may do, denied by default, checked in code before every action. Not an instruction in the prompt: a prompt is a request, a permission check is a boundary.

**Questions to answer**

- Which paths, tables, endpoints and recipients may it touch? Name them individually.
- What identity does it run as, and what *else* can that identity reach? An agent on a human's credentials inherits that human's whole life.
- Which of its actions cannot be undone?
- When it requests something off the list, does it refuse and continue, or refuse and halt? Pick deliberately.

**Done looks like.** Someone who has never read the code can open one file and state exactly what the agent may touch. Anything not on the list is refused, and a test proves it.

```markdown
- [ ] Allowlist exists in one file, readable by a non-engineer
- [ ] Default is deny; nothing is permitted implicitly
- [ ] Agent runs as its own identity, not a person's and not an admin
- [ ] Write and delete permissions listed separately from read
- [ ] Irreversible actions enumerated and individually justified
- [ ] Denied attempts are logged, not silently swallowed
- [ ] A test asserts that a denied action is actually denied
```

---

## Gate 2 — Budget

**What it is.** A hard ceiling on spend and volume — calls, tokens, wall-clock time, items processed — enforced by the code making the calls. A dashboard alert is not a budget; it tells you afterwards.

The cost that hurts is rarely the per-call one. It is the shape: a retry loop that never gives up, a batch that was forty documents in testing and forty thousand in production, a scheduled run that started twice because the first had not finished.

**Questions to answer**

- What is the ceiling per run, and per day?
- When it is reached, does it stop cleanly or degrade to a smaller scope?
- Do retries count against the cap? They must, or the cap protects nothing.
- What does one item actually cost, measured on real inputs rather than estimated?

**Done looks like.** You can state the maximum a single run can cost, and point at the code enforcing it.

```markdown
- [ ] Per-run and per-day ceilings defined as numbers
- [ ] Ceiling enforced in code, not by an alert
- [ ] Retries and continuations count against the ceiling
- [ ] Maximum items per run is bounded
- [ ] Cost per item measured on real data and written down
- [ ] Hitting the ceiling stops cleanly and notifies someone by name
- [ ] Concurrent runs of the same job are prevented
```

---

## Gate 3 — Audit

**What it is.** A durable record of what the agent did and what produced it, written outside the process, one entry per decision.

This is the only gate you cannot retrofit. Add a spending cap on Tuesday and it protects you from Tuesday. You cannot add Monday's records on Tuesday — they do not exist, and no amount of later diligence brings them back.

**Questions to answer**

- Could you answer "what did it do on 12 March at 14:00" in under ten minutes?
- Does each record identify the prompt version and model version that produced it?
- Is the log append-only, and stored where the agent cannot rewrite it?
- Does it hold data that should not be sitting in a log? An audit trail full of personal data is a new problem, not a solution.

**Done looks like.** A stranger can reconstruct one decision end to end — input, output, versions, timestamp — from the record alone.

```markdown
- [ ] One record per decision, not one per run
- [ ] Each record has: run id, timestamp, input reference, output, outcome
- [ ] Prompt version and model version recorded on every entry
- [ ] Shadow and live entries clearly distinguished
- [ ] Log is append-only and outside the agent's write permissions
- [ ] Retention period set, with a named owner
- [ ] Sensitive fields referenced by identifier, not copied into the log
- [ ] Someone has actually queried it for a specific past date
```

---

## Gate 4 — Shadow

**What it is.** The agent runs against real inputs, makes real decisions, and writes nothing — recording what it *would* have done, so you can compare it against what actually happened.

Shadow mode is an architectural property, not a testing phase. Added later, it means threading a flag through every call site, and someone will miss one. Build it the other way round: route every side effect through a single component, and let that component be the only thing that checks the flag.

**Questions to answer**

- How many items before go-live, and who decides that is enough?
- What is the agreement rate against the current baseline — usually, what people did?
- Of the disagreements, how many were the agent being right? That matters as much as the error rate.
- Can you re-enter shadow after a change? You will need to.

**Done looks like.** You can show, over real traffic, the gap between what the agent would have done and what was done, with every disagreement enumerated and explained.

```markdown
- [ ] Every side effect routed through one component
- [ ] That component is the only place the shadow flag is checked
- [ ] Shadow runs write a full record of intended actions
- [ ] Baseline for comparison defined before the run starts
- [ ] Agreement rate and disagreement list reviewed by a human
- [ ] Disagreements categorised: agent wrong, agent right, genuinely ambiguous
- [ ] Shadow can be re-enabled after go-live without a code change
```

---

## Gate 5 — Human gate

**What it is.** Two things sharing a name. First, **going live is a decision a named person makes**, on the record, looking at evidence — not a flag someone flips in a config file. Second, **at runtime**, the cases the agent must not decide alone have a route to a person.

**Questions to answer**

- Who approves, and what are they actually looking at?
- Which cases always escalate — by value, by novelty, by the agent's own uncertainty?
- Does the reviewer have enough context to decide, or are they clearing a queue at forty items an hour? A rubber stamp is worse than no gate: it manufactures the appearance of oversight.
- How is it reversed, by whom, and how fast?

**Done looks like.** A named person approved it, the evidence they saw is stored, escalation has been exercised on a real case, and someone who is not the author can turn it off.

```markdown
- [ ] Named approver, with a date and stored evidence pack
- [ ] Approval bound to the prompt and model version it was granted for
- [ ] Approval expires; it is not a permanent grant
- [ ] Escalation thresholds written down as rules, not judgement
- [ ] Escalated cases reach a person who can act on them
- [ ] Human overrides are recorded with the same detail as agent decisions
- [ ] Kill switch exists, documented, executable without a deploy
- [ ] Someone other than the author knows how to use it
- [ ] Escalation path tested with a real case before go-live
```

---

## When you cannot do all five

You will not always get the time. Do them in this order.

**1. Permissions. 2. Audit.** Always these two first. Permissions bound how bad it can get; audit is the only one that cannot be added retroactively. Between them they answer the two questions every incident review asks: how bad could this have been, and what actually happened.

**3. Budget.** Cheap, quick, and it covers the least dangerous but most embarrassing failure.

**4. Human gate.** Partly process rather than code, so a short-term version costs nothing: a named approver, an evidence pack, a written reversal procedure.

**5. Shadow.** Last to triage, first in the architecture, and that tension is real. If you must defer it, defer it *by leaving the seam in*: route side effects through one component today, even if that component always executes. Adding the flag then becomes an afternoon rather than an excavation.

If you can do none of them, reduce scope until the agent proposes rather than acts. Drafting for a person needs far less machinery than sending. That is a legitimate first release, not a failure.

---

## Questions your risk or compliance reviewer will ask

A good answer is a pointer to a mechanism: a file, a config key, a log query, a number, a person's name. "We would notice" is not an answer. "We are careful" is not an answer.

1. **What is the most sensitive data this can reach?** Good: the field, the allowlist entry permitting it, and what it demonstrably cannot reach.
2. **What can it do that cannot be undone?** Good: a short list, each item with either a human gate or a tested reversal procedure.
3. **How do you know it is right, and how did you measure that?** Good: a number from a labelled sample or shadow run, with sample size, date, and error rate by case type.
4. **What happens when it is wrong — who finds out, how fast?** Good: the detection mechanism and a time. The best answer describes an error that already happened.
5. **Show me everything it did on this date.** Good: you run the query while they watch. This is the audit test, and usually the one that fails.
6. **Who approved this going live, and what did they see?** Good: a name, a date, a stored evidence pack.
7. **What is the most it can spend in a day, and what enforces that?** Good: a number and a file path. An alert is not enforcement.
8. **What happens when the model version changes underneath you?** Good: the version is pinned, and a regression set gets re-run before moving. "We always use the latest" is a red flag.
9. **How is it turned off, by whom, and how long does that take?** Good: a documented procedure, someone on call who can run it without a deploy, an answer in minutes.
10. **Who is accountable for its output, and do they know?** Good: a named person who agreed in writing. If the answer is "the team", the answer is nobody.

---

Why projects stall without this: [The Governance Gap](03-the-governance-gap.md).

What it looks like in code: [`../examples/02-governed-agent/`](../examples/02-governed-agent/) is [`../examples/01-hello-agent/`](../examples/01-hello-agent/) with all five gates and nothing else added.
