<img src="images/the-gap.png" alt="From 'it works' to 'in production'" width="100%">

# 03 — The Governance Gap

**Why the demo that impressed everyone in March is still not running in October.**

Look at that bridge again. It doesn't reach. That is the single most accurate picture in this repo, and it is not an accident of the image generator — it is what most AI agent projects actually look like eighteen months in.

This document is about why, and what to do instead.

---

## The pattern

It goes the same way almost every time.

**Week one.** Someone builds an agent that does something genuinely useful. It reads the documents, or drafts the summaries, or scores the leads. It works. People are impressed, because it *is* impressive.

**Week three.** The demo gets shown to a wider group. Everyone wants it. Someone senior asks when it can be turned on.

**Week six.** The first real conversation with whoever owns the system it needs to touch. It goes badly, and not because anyone is being obstructive:

> **Them:** What does it have access to?
> **You:** It uses my credentials right now, but we'd give it a service account.
> **Them:** With what permissions?
> **You:** Whatever it needs to read the documents and write the results.
> **Them:** So read and write on the whole store.
> **You:** …for now.
> **Them:** How accurate is it?
> **You:** About 94%.
> **Them:** On what?
> **You:** Our test set.
> **Them:** Who made the test set?
> **You:** We did.
> **Them:** What happens when it's wrong?
> **You:** It would write the wrong value.
> **Them:** How would we know?
> **You:** …

**Week twelve.** The project is described as "on hold pending security review."

**Month eighteen.** It is quietly not mentioned any more.

Nobody in that story did anything wrong. The builder built a real thing. The reviewer asked exactly the right questions. The demo died because it was **built to prove a capability, and proving a capability is not the same as earning the right to run.**

---

## Why "it works" is the wrong finish line

A working demo answers one question: *can the model do this?*

Production asks a completely different set, and none of them are about the model:

- **What can it reach?** Not what does it use — what *could* it reach if it went wrong, or if someone influenced its input.
- **What can it spend?** An agent in a retry loop is a machine for converting bugs into invoices.
- **What did it do?** Not "did it work" — what specific decision did it make on the fourteenth of last month, and why.
- **How do you know it's right?** Measured on real traffic, not on the examples you built it with.
- **Who said yes?** Not who deployed it. Who *decided*.

The uncomfortable part: **you cannot answer any of those retroactively.** They're not questions you research when asked. They're questions your architecture either answers or doesn't. If you didn't build an audit log, you cannot produce last month's decisions. If you never ran in shadow, you have no accuracy figure that means anything. The evidence doesn't exist because nothing was built to produce it.

That's the gap. Not a review you failed — a set of artifacts you never made.

---

## The three false beliefs that create it

**"We'll add governance once it's proven."** This sounds like sequencing and is actually a trap. Governance is not a layer you apply on top of a working system; several of the five gates are structural. Shadow mode in particular has to exist at the boundary where actions happen, and retrofitting it means threading a flag through every call site — where someone will miss one, and the first shadow run will write to production. Build the log path first and make the live path the special case.

**"The model is the hard part."** The model is the part that already works. Anthropic solved it. What's left is permissions, error handling, retries, idempotency, observability, cost control, and the human process around all of it. That's ordinary engineering, and ordinary engineering is most of the project.

**"Autonomy is the goal."** An agent that handles 70% of cases and cleanly escalates the rest is worth far more than one that attempts 100% and is quietly wrong on 8% — because the first one's failures are visible and the second one's are not. Silent wrongness at scale is the actual risk, and the way you avoid it is by making refusal a first-class outcome rather than a fallback.

---

## What closing the gap actually costs

Be honest with yourself and with whoever is funding this.

**In code:** roughly ten times the lines. That's what [`examples/02-governed-agent`](../examples/02-governed-agent/) exists to demonstrate — same job, same output, byte-for-byte identical CSV, about 8x the executable code. Some of that is boilerplate a mature platform gives you for free; a lot of it isn't.

**In time:** the shadow run is the expensive part, and it's expensive in *human weeks*, not compute. Somebody reads the logs. That's the real bill.

**In patience:** you will spend a stretch running something that produces no value while it proves it would have. That's hard to defend to a sponsor who saw a working demo months ago. The only argument that lands is the honest one: *the alternative is discovering the error rate in production.* One of those is a schedule problem, the other is an incident.

---

## What to do instead

**Build the second gate first.** Not all five on day one — but write the audit log before you write the write path. It costs almost nothing at the start and is nearly impossible to add convincingly later.

**Make shadow mode the default.** In both examples here, and in every agent you build, the default invocation should write nothing. Going live should require an explicit, awkward, deliberate flag. Friction in that specific place is a feature.

**Scope the first go-live absurdly narrow.** One document type. One folder. One sender. Whatever the smallest slice is where the cost of being wrong is boring. Get a track record on that before you ask for anything harder. A narrow win compounds; a broad failure ends the program.

**Have the security conversation in week one, not week six.** Bring the questions above to them before you build. Ask what evidence they would need in order to say yes. Then build the thing that produces it. This single change — treating the reviewer as a requirements source rather than a gate at the end — is the highest-leverage move available to you.

**Write down what wrong looks like, and what it costs.** Not "the model might hallucinate." Concretely: *the wrong customer's data gets written to this field, it's silent, and nobody finds out for a year.* Once that sentence exists, the whole architecture follows from it, and you can tell which errors deserve a human and which deserve a retry.

---

## The reframe

Most people read "agents are easy, governance is hard" as a complaint. It isn't.

It's the good news. The hard part used to be *making the thing work at all* — and that part is largely solved, which is why your demo took an afternoon. What's left is the kind of problem our profession has been solving for fifty years: access control, audit, cost management, staged rollout, change approval. We know how to do this. It's unglamorous and entirely learnable.

The projects that succeed aren't the ones with the cleverest agents. They're the ones where somebody looked at the working demo and asked, in week one, *what would it take for this to be allowed to run?* — and then built that.

The bridge is the deliverable. The thing on either side of it was never the hard part.

---

**Next:** [04 — Governance Checklist](04-governance-checklist.md) — the concrete version, in a list you can paste into a ticket.

**See it:** [`examples/02-governed-agent`](../examples/02-governed-agent/) — the same agent, accountable.
