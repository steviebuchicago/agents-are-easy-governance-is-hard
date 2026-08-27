"""Read a folder of invoices, extract structured fields, write a CSV.

Exactly the job 01-hello-agent does, and exactly the same CSV. The extraction
is unchanged -- same model, same prompt, same fields. Everything added here is
governance, and it all lives in governance.py so this file stays readable.

    export ANTHROPIC_API_KEY=sk-ant-...

    python agent.py                     # shadow mode: writes nothing, logs everything
    python agent.py --live \
        --i-understand-this-writes \
        --approval CHG-2026-0412        # writes the CSV, if the approval checks out

Shadow is the default. Live needs a flag, a confirmation, and an approval
record that someone other than this process created.
"""

import argparse
import json
import os
import sys

import anthropic

import governance as gov

# --- identical to 01-hello-agent -------------------------------------------

MODEL = "claude-sonnet-4-5"
MAX_OUTPUT_TOKENS = 512
FIELDS = ["invoice_number", "vendor", "invoice_date", "due_date",
          "currency", "total_amount", "confidence"]
SYSTEM = (
    "You extract billing fields from a single invoice and return one JSON object and "
    "nothing else. Keys: " + ", ".join(FIELDS) + ". Dates are ISO (YYYY-MM-DD). "
    "currency is a 3-letter code. total_amount is a plain number, no symbols or "
    "separators. confidence is your own 0-1 estimate that the extraction is correct. "
    "Use null for any field the document does not clearly state."
)

# --- governance configuration ----------------------------------------------

AGENT_ID = "invoice-extract"

# Bumped by hand whenever SYSTEM changes. Approvals are granted against this
# exact string, so editing the prompt without bumping it, or bumping it without
# re-approving, means the next live run refuses. That friction is the feature:
# it is what stops a reviewed agent quietly becoming an unreviewed one.
PROMPT_VERSION = "invoice-extract/2026-03-30"

# Below this, the extraction is recorded for a human to look at. Note what this
# does NOT do: it does not withhold the row. The CSV is byte-identical to 01's.
# The difference is that afterwards you can say which four rows were shaky.
REVIEW_THRESHOLD = 0.80

# The permission roots. These are configuration and are never derived from the
# arguments they are used to check -- an allowlist built out of argv is not an
# allowlist, it is a formality.
INPUT_DIR = "sample_docs"
OUTPUT_DIR = "out"
APPROVALS_FILE = "approvals.json"

client = anthropic.Anthropic()


def extract(text, budget):
    """One model call per document. The call itself is unchanged from 01.

    The only additions are the two budget lines around it: price the call
    before making it, book what it actually cost after.
    """
    # ~4 characters per token is a rough but conservative English estimate, and
    # we assume the model fills max_tokens on the way out. Guessing high means
    # we stop one document early; guessing low means the cap does not hold.
    budget.reserve(len(text) // 4, MAX_OUTPUT_TOKENS)

    reply = client.messages.create(
        model=MODEL, max_tokens=MAX_OUTPUT_TOKENS, system=SYSTEM,
        messages=[{"role": "user", "content": text}],
    )
    budget.record(reply.usage.input_tokens, reply.usage.output_tokens)

    body = reply.content[0].text.strip().strip("`").removeprefix("json").strip()
    return json.loads(body), reply.usage.input_tokens + reply.usage.output_tokens


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", default=INPUT_DIR)
    ap.add_argument("--output", default=f"{OUTPUT_DIR}/invoices.csv")
    ap.add_argument("--audit", default=f"{OUTPUT_DIR}/audit.jsonl")
    ap.add_argument("--live", action="store_true",
                    help="write the CSV for real (requires the two flags below)")
    ap.add_argument("--i-understand-this-writes", dest="confirmed", action="store_true",
                    help="second confirmation, so --live cannot be an up-arrow away")
    ap.add_argument("--approval", default=os.environ.get("AGENT_APPROVAL"),
                    help="change reference from approvals.json, e.g. CHG-2026-0412")
    ap.add_argument("--max-calls", type=int, default=25)
    ap.add_argument("--max-tokens", type=int, default=60_000)
    ap.add_argument("--max-usd", type=float, default=1.00)
    return ap.parse_args()


def main():
    args = parse_args()
    run_id = gov.new_run_id()

    # GATE 1 -- permissions. Reads its inputs and its approval registry, writes
    # only into OUTPUT_DIR. Anything else is denied, including --output /etc/passwd.
    allow = gov.Allowlist(read_paths=[INPUT_DIR, APPROVALS_FILE],
                          write_paths=[OUTPUT_DIR])

    try:
        # GATES 4 and 5 -- shadow by default; live needs a human approval record.
        # Resolved before any work starts: a run that is going to be refused
        # should be refused before it has spent anything.
        mode = gov.RunMode.decide(
            live=args.live,
            confirmed=args.confirmed,
            approval_token=args.approval,
            registry_path=APPROVALS_FILE,
            allowlist=allow,
            agent_id=AGENT_ID,
            prompt_version=PROMPT_VERSION,
        )
        input_dir = allow.read(args.input)
        output_path = allow.write(args.output)
    except gov.GovernanceError as err:
        # Refusals are not crashes. Exit 2 so a scheduler can tell the
        # difference between "the gate said no" and "the code fell over".
        print(f"refused: {err}", file=sys.stderr)
        return 2

    # GATE 2 -- budget. GATE 3 -- audit.
    budget = gov.Budget(args.max_calls, args.max_tokens, args.max_usd)
    audit = gov.AuditLog(args.audit, allow, run_id, PROMPT_VERSION, mode.label)
    summary = gov.RunSummary(run_id, mode.label)

    print(f"run {run_id}")
    print(f"  mode    {mode.describe()}")
    print(f"  reads   {allow.describe('read')}")
    print(f"  writes  {allow.describe('write')}")
    print(f"  budget  {budget.describe()}")
    print(f"  audit   {audit.path}")
    print()

    rows = []
    for path in sorted(input_dir.glob("*.md")):
        # Re-checked per file even though the directory was allowlisted: a glob
        # returns whatever is on disk, and a symlink dropped into sample_docs
        # is an input the agent did not choose.
        source = allow.read(path)
        text = source.read_text(encoding="utf-8")

        # The digest, not the document. Enough to prove later which bytes
        # produced which row, without the log becoming a copy of the invoices.
        ref = gov.document_reference(source, text)

        try:
            fields, tokens = extract(text, budget)
        except gov.BudgetExceeded as err:
            # Stop. Not skip, not retry -- the next document costs the same as
            # this one, so continuing is how a cap becomes a suggestion.
            summary.stopped_reason = str(err)
            audit.record(**ref, decision="halted", reason=str(err),
                         confidence=None, tokens=0)
            print(f"  STOP  {source.name}: {err}")
            break
        except Exception as err:
            summary.processed += 1
            summary.failed += 1
            audit.record(**ref, decision="failed", reason=type(err).__name__,
                         confidence=None, tokens=0)
            print(f"  fail  {source.name}: {err}")
            continue

        row = {"source_file": source.name, **{k: fields.get(k) for k in FIELDS}}
        confidence = fields.get("confidence")

        # A missing confidence is a low confidence. Treating "the model did not
        # say" as "the model was sure" is how the ambiguous cases get through.
        needs_review = confidence is None or confidence < REVIEW_THRESHOLD

        summary.processed += 1
        summary.extracted += 1
        summary.review += int(needs_review)
        rows.append(row)

        # One record per document, written now rather than at the end, and
        # carrying the row itself -- in shadow mode this IS the output.
        audit.record(**ref, decision="review" if needs_review else "accepted",
                     confidence=confidence, tokens=tokens, row=row)
        print(f"  {'REVIEW' if needs_review else 'ok    '}  {source.name}"
              f"  {row['invoice_number']}  {row['total_amount']}")

    # Rendered identically in both modes, so shadow exercises the same code
    # path as live. The only difference is whether these bytes reach a file.
    csv_text = gov.render_csv(rows, ["source_file"] + FIELDS)

    # A run that stopped early does not write, even in live mode. A truncated
    # CSV looks exactly like a complete one -- same header, fewer rows -- so
    # overwriting yesterday's good file with a half-finished one is a silent
    # data loss that nothing downstream can detect. Stopping means stopping.
    wrote = mode.live and not summary.stopped_reason
    if wrote:
        with open(output_path, "w", newline="", encoding="utf-8") as handle:
            handle.write(csv_text)
    elif mode.live:
        print(f"  not written: run stopped early, {output_path} left untouched")

    # A run-level record so an auditor can tie a CSV on disk back to this run
    # and these decisions by hashing the file.
    audit.record(decision="run_complete", processed=summary.processed,
                 extracted=summary.extracted, review=summary.review,
                 failed=summary.failed, wrote=wrote,
                 output=str(output_path), output_sha256=gov.digest(csv_text),
                 tokens=budget.tokens, spend_usd=round(budget.spent_usd, 6),
                 approval=(mode.approval or {}).get("token"))

    print(summary.render(budget, output_path, wrote=wrote))
    return 1 if summary.stopped_reason else 0


if __name__ == "__main__":
    sys.exit(main())
