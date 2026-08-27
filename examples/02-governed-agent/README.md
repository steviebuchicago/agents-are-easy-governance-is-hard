# 02 — Governed Agent

The same job as [`01-hello-agent`](../01-hello-agent/), the same prompt, the same byte-identical CSV — with the five gates that let it run somewhere that matters.

```bash
cd examples/02-governed-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

python agent.py                        # shadow: writes nothing, logs everything

python agent.py --live \
    --i-understand-this-writes \
    --approval CHG-2026-0412           # writes the CSV, if the approval checks out
```

---

## What changed

Nothing about the extraction. `MODEL`, `FIELDS`, `SYSTEM` and the body of `extract()` are the same lines they are in 01. Diff the two files and every difference is a gate.

That is the point of the pair. The governed version is not smarter and does not handle a single case the first one misses — run both against `sample_docs/` and the CSVs match to the byte. What the extra code buys is that someone can answer questions about the run afterwards.

The five gates live in `governance.py` so `agent.py` stays readable.

## Gate 1 — Permissions

`Allowlist` declares two roots: it reads `sample_docs/` and `approvals.json`, it writes `out/`. Everything else is denied, and every path goes through `.read()` or `.write()` before it reaches `open()` — including the audit log, because a logger that can write anywhere is a way to write anywhere.

Three details do the real work. Paths are `resolve()`d before comparison, so `sample_docs/../../../etc/passwd` is checked as `/etc/passwd` rather than as a string that starts with `sample_docs`. Read and write roots are separate, so the agent cannot write back over its own inputs. And the roots are constants in `agent.py`, never derived from the arguments they check — an allowlist built out of `argv` is a formality.

*The failure this prevents.* The boring version: someone adds `--output` to a scheduled job, fat-fingers the directory, and six weeks of extractions pile up where nobody reads them. The version that is not boring: the same process a year later, now holding a tool that takes a filename, and the filenames come from the documents it is reading. Nothing in 01 has an opinion about which paths are legitimate, because it runs with your credentials and can reach everything you can.

## Gate 2 — Budget

`Budget` holds three ceilings — calls, tokens, dollars — and whichever is hit first stops the run. `reserve()` prices the *next* call before it is made and refuses it if it would cross a line. A ceiling you only compare against after the money is gone is a report, not a cap.

On exceed it stops, not skips and not retries — the next document costs about what this one cost, so continuing is how a cap becomes a suggestion. A run that stopped early also does not write, even in live mode: a truncated CSV looks exactly like a complete one, so overwriting yesterday's good file with a half-finished one is a data loss nothing downstream can detect.

*The failure this prevents.* A malformed PDF returns something the parser rejects. The retry produces the same output, because the input has not changed. The loop runs all night and nobody finds out until the bill arrives, because a job that is burning money looks exactly like a job that is working.

## Gate 3 — Audit

`AuditLog` appends one JSON record per document, as it happens: UTC timestamp, run id, mode, the source filename and a SHA-256 of its contents, the decision, the confidence, the tokens consumed, the row itself — and the prompt version.

The prompt version is the field people leave out and then need most. An extraction is only explainable if you know which prompt produced it, and the prompt will have been edited twice by the time anyone asks.

Two smaller decisions are worth copying. The log opens, appends and closes per record rather than holding a handle, because buffering loses exactly the records you wanted — the interesting runs are the ones that die. And it refuses to log the document payload: pass a key named `text` or `content` and `record()` raises. An audit trail is read by more people than the source data is, so it has to prove a document was processed without becoming a second, less protected copy of it.

*The failure this prevents.* In June, someone asks why row 5 says `917.74` and not `1132.74`. The honest answer is "we think it worked" — the CSV has been overwritten twice and the prompt has changed since.

## Gate 4 — Shadow mode

Default. `python agent.py` runs the whole pipeline against real inputs and writes no CSV. Every row it would have written goes into the audit log instead.

Both modes render the CSV through the same `render_csv()` call; the only difference downstream is whether those bytes reach a file. That is checkable rather than asserted — the shadow run records an `output_sha256` that matches the hash of the file the live run writes.

It is default-on for a reason. Shadow that has to be switched on is shadow that is off, and retrofitting it means threading a flag through every write in the codebase and trusting nobody missed one.

*The failure this prevents.* You find out the extraction is wrong on real documents by looking at the damage. With shadow mode you run a week of real traffic, diff the intended output against what a human actually keyed, and have that argument before anything is at stake.

## Gate 5 — The human gate

`--live` alone is refused. `--live --i-understand-this-writes` is also refused. Going live needs `--approval CHG-2026-0412`, and the code opens `approvals.json` and checks it.

The second flag is not security — it is a speed bump against the up-arrow, so `--live` cannot be the last thing you typed. The approval is the gate, and it fails closed on every branch: missing file, unparseable file, unknown token, wrong agent, expired approval.

The branch that matters most is the prompt version. Each approval is bound to the exact `PROMPT_VERSION` it was granted for, so editing `SYSTEM` without bumping the version — or bumping it without re-approving — makes the next live run refuse. What was reviewed is no longer what would run. That friction is what stops a reviewed agent quietly becoming an unreviewed one.

`approvals.json` is a stand-in for whatever your organisation already uses — a change record, a ticket, a signed control entry. The format does not matter. What matters is that the agent reads it, that a different person created the entry, and that it expires.

*The failure this prevents.* "Who approved this?" has no answer, so the answer becomes the name of whoever ran it. A flag an engineer can flip is not a gate.

## What a run tells you

```
--------------------------------------------------------------------
run 20260827T031852Z-889dff  |  mode: shadow
--------------------------------------------------------------------
  documents processed     5
  rows extracted          5  (would have been written to ./out/invoices.csv)
  routed to human review  1
  failed                  0
  budget consumed         5/25 calls, 1,224/60,000 tokens, $0.0065/$1.0000
  elapsed                 0.0s
  no file written -- shadow mode. Re-run with --live ...
--------------------------------------------------------------------
```

One document routed to review: the OCR scan comes back at 0.41 confidence, below the 0.80 threshold. Note what review does *not* do — it does not withhold the row, so the CSV stays identical to 01's. The difference is that afterwards you can say which row was shaky. Wiring that flag to a real queue is a product decision; governance is what makes the evidence exist to wire it to.

A missing confidence counts as a low one. Treating "the model did not say" as "the model was sure" is how the ambiguous cases get through.

## The line count

| | 01 | 02 | |
| --- | ---: | ---: | --- |
| `agent.py`, executable lines | 40 | 121 | |
| `governance.py`, executable lines | — | 204 | |
| **executable lines, total** | **40** | **325** | **8.1x** |
| comments and docstrings | 9 | 236 | |
| blank | 14 | 122 | |
| **lines in the files** | **63** | **683** | **10.8x** |

Check it with `wc -l agent.py governance.py`. The front page rounds this to "40 lines and 400"; the precise version is 40 executable lines becoming 325, and about 10x either way you count.

Be suspicious of that multiplier, because a good share of it is not insight. Roughly 130 of the 325 lines are plumbing a managed platform hands you for nothing: matching paths, appending JSONL with timestamps and run ids, arithmetic against a price table, rendering a summary, argparse wiring. You write it here because you picked the Agent SDK, and the SDK's bargain is all the control and all the responsibility.

The other 200 are not boilerplate and no platform will write them for you: what counts as review, what an approval is bound to, what stops a run, what never reaches the log.

## Try the refusals

```bash
python agent.py --live                                   # missing confirmation
python agent.py --live --i-understand-this-writes        # missing approval
python agent.py --live --i-understand-this-writes --approval CHG-2026-0288
                                                         # expired, and stale prompt version
python agent.py --output /etc/passwd                     # outside the write allowlist
python agent.py --input ../../../etc                     # outside the read allowlist
python agent.py --max-calls 2                            # budget stops the run
```

Each refusal exits 2. A budget halt exits 1 — a scheduler should be able to tell "the gate said no" apart from "the code fell over," and both apart from success.

## What this still isn't

One process on one machine. No queue, no retry with backoff, no secret management, no rotation on the audit log, no alerting when the review count spikes, and an approval registry that is a JSON file rather than a system with its own access control. All real gaps, and none of them changes the argument: the distance between 01 and 02 is not capability.
