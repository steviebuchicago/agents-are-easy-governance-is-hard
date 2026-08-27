# Contributing

Contributions are welcome, and you do not need to be an expert to make a good one. This is a teaching repo — clarity counts more than cleverness.

## What is especially wanted

**Governance failure modes you learned the hard way.** If you shipped an agent and something went wrong — a permission that was wider than you thought, a retry loop that ran up a bill, an audit trail that turned out to be missing the one field anyone asked for, a shadow run that gave a comforting number for the wrong reason — that experience is the most valuable thing you can bring here. Almost nobody writes these down, which is why everyone keeps rediscovering them.

You do not have to name an employer, a client, or a system. "An agent with write access to a shared drive, and what happened when a filename collided" is a complete and useful contribution.

## Also welcome

- Corrections. If something here is wrong, say so plainly and we will fix it.
- A first-run error that is not in [Your First Hour](docs/02-your-first-hour.md), with the fix that worked.
- A question your risk or compliance reviewer asked that is not in the [Governance Checklist](docs/04-governance-checklist.md).
- Cowork skills, in the shape of the two in [`cowork/skills/`](cowork/skills/) — real, constrained, and honest about what they will not do.
- Making an explanation shorter without losing anything.

## How

Open an issue if you want to discuss it first. Otherwise fork, branch, and open a pull request with a description of what changed and why.

For prose, match the voice already here: direct, concrete, no hype. Prefer a specific example to a general claim. If you state a number, be able to say where it came from.

For code, keep the examples small. [`examples/01-hello-agent/`](examples/01-hello-agent/) is deliberately minimal and should stay that way — anything that makes it more robust probably belongs in [`examples/02-governed-agent/`](examples/02-governed-agent/), which is the whole point of having both.

Please do not include real credentials, client data, or anything you would not want a search engine to index. Check your sample files before you push.

## Scope

This repo is for people at the beginning. Depth is good; complexity for its own sake is not. If a contribution needs a reader to already understand agent orchestration, it probably belongs in a different repo — and that is not a rejection of the idea, only of the venue.

Thank you for taking the time.
