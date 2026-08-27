"""The five gates between an agent that works and an agent that is allowed to run.

Nothing here makes the agent smarter. Every line exists to answer a question
somebody will ask after the fact:

    Allowlist   what may it touch?          -> deny by default, allow by path
    Budget      what may it spend?          -> stop, do not overrun
    AuditLog    what did it do, and why?    -> append-only JSONL, one row per document
    RunMode     is it right, on real data?  -> shadow by default, writing is the exception
    approval    who said yes?               -> a record someone else created, not a flag

It is deliberately plain Python with no dependencies. A real platform gives you
most of this for free; the point of writing it out is that if you are holding
the Agent SDK, nobody is giving it to you.
"""

import csv
import hashlib
import io
import json
import os
import time
from datetime import date, datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Failures are their own type so agent.py can distinguish "governance stopped
# this on purpose" from "the code broke". They are not the same event and they
# should never be reported to a human as if they were.
# ---------------------------------------------------------------------------


class GovernanceError(Exception):
    """Base class: the run was stopped by a gate, not by a bug."""


class PermissionDenied(GovernanceError):
    """A path outside the allowlist was requested."""


class BudgetExceeded(GovernanceError):
    """The next call would cross a ceiling, so it was not made."""


class ApprovalError(GovernanceError):
    """Live mode was requested without a valid human approval."""


# ---------------------------------------------------------------------------
# GATE 1 -- PERMISSIONS
#
# The failure this prevents: the agent is handed a path from a config file, an
# argument, or a filename inside a document, and follows it. Nothing in the
# process is scoped -- it runs with your credentials, so it can reach every
# file your account can reach. "It only ever reads sample_docs" is true right
# up until an argument says otherwise.
# ---------------------------------------------------------------------------


class Allowlist:
    """Deny by default. A path is usable only if it sits under a declared root.

    Read roots and write roots are separate on purpose: this agent reads its
    input directory and writes its output directory, and there is no reason it
    should ever be able to write back over its own inputs.
    """

    def __init__(self, read_paths, write_paths):
        # resolve() at construction so the roots are absolute and symlink-free.
        # Comparing a relative root against an absolute path silently never
        # matches, which fails open in the worst way -- it looks like it works.
        self._read = [Path(p).resolve() for p in read_paths]
        self._write = [Path(p).resolve() for p in write_paths]
        for root in self._write:
            # A write root that does not exist cannot be resolved consistently
            # across platforms, so create it here rather than letting the first
            # write decide where it lands.
            root.mkdir(parents=True, exist_ok=True)

    def _check(self, path, roots, kind):
        # resolve() collapses ".." and follows symlinks BEFORE the comparison.
        # Checking the string you were given instead of the path it resolves to
        # is the single most common way an allowlist is defeated:
        # "sample_docs/../../../etc/passwd" passes a naive prefix check.
        candidate = Path(path).resolve()
        for root in roots:
            if candidate == root or candidate.is_relative_to(root):
                return candidate
        raise PermissionDenied(
            f"{kind} denied: {candidate}\n"
            f"  allowed {kind} roots: {', '.join(str(r) for r in roots) or '(none)'}"
        )

    def read(self, path):
        """Return the resolved path, or raise. Call this before every open()."""
        return self._check(path, self._read, "read")

    def write(self, path):
        """Return the resolved path, or raise. Call this before every write."""
        return self._check(path, self._write, "write")

    def describe(self, kind):
        """Printed at the top of every run. An allowlist nobody sees is an
        allowlist nobody notices has quietly grown."""
        roots = self._read if kind == "read" else self._write
        return ", ".join(str(p) for p in roots) or "(none)"


# ---------------------------------------------------------------------------
# GATE 2 -- BUDGET
#
# The failure this prevents: a malformed document makes the model return
# something the parser rejects, the loop retries, the retry produces the same
# result, and the job runs all night. Nobody finds out until the bill arrives,
# because a job that is spending money looks exactly like a job that is working.
# ---------------------------------------------------------------------------

# Dollars per million tokens. These are configuration, not facts -- check them
# against current pricing before trusting the cap, because a ceiling computed
# from stale numbers is a ceiling in the wrong place.
USD_PER_MTOK_INPUT = 3.00
USD_PER_MTOK_OUTPUT = 15.00


class Budget:
    """Three ceilings: calls, tokens, dollars. Whichever is hit first stops the run."""

    def __init__(self, max_calls, max_tokens, max_usd):
        self.max_calls = max_calls
        self.max_tokens = max_tokens
        self.max_usd = max_usd
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    @property
    def tokens(self):
        return self.input_tokens + self.output_tokens

    @property
    def spent_usd(self):
        return (self.input_tokens * USD_PER_MTOK_INPUT
                + self.output_tokens * USD_PER_MTOK_OUTPUT) / 1_000_000

    def reserve(self, est_input_tokens, max_output_tokens):
        """Price the NEXT call and refuse it if it would cross a ceiling.

        This runs before the call, never after. A ceiling you only compare
        against after the money is gone is a report, not a cap. The estimate is
        deliberately pessimistic -- assume the model fills max_tokens -- because
        the cost of stopping one document early is a rerun, and the cost of the
        other mistake is an invoice.
        """
        projected_tokens = self.tokens + est_input_tokens + max_output_tokens
        projected_usd = self.spent_usd + (
            est_input_tokens * USD_PER_MTOK_INPUT
            + max_output_tokens * USD_PER_MTOK_OUTPUT
        ) / 1_000_000

        if self.calls + 1 > self.max_calls:
            raise BudgetExceeded(f"call cap reached ({self.max_calls} calls)")
        if projected_tokens > self.max_tokens:
            raise BudgetExceeded(
                f"token cap would be crossed "
                f"({projected_tokens:,} projected > {self.max_tokens:,} allowed)"
            )
        if projected_usd > self.max_usd:
            # Four decimal places everywhere money is printed. Rounding a cap of
            # $0.003 to "$0.00" in the message that explains the refusal makes
            # the refusal look like a bug.
            raise BudgetExceeded(
                f"spend cap would be crossed "
                f"(${projected_usd:,.4f} projected > ${self.max_usd:,.4f} allowed)"
            )

    def record(self, input_tokens, output_tokens):
        """Book the actual usage the API reported. Estimates are for deciding;
        this is what the audit log and the summary are allowed to claim."""
        self.calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def describe(self):
        return (f"{self.calls}/{self.max_calls} calls, "
                f"{self.tokens:,}/{self.max_tokens:,} tokens, "
                f"${self.spent_usd:,.4f}/${self.max_usd:,.4f}")


# ---------------------------------------------------------------------------
# GATE 3 -- AUDIT
#
# The failure this prevents: someone asks what the agent did on the 14th and
# why row 38 says 917.74. Without a record the honest answer is "we think it
# worked", which is not an answer anyone can act on, and the run cannot be
# reproduced because the prompt has been edited twice since.
#
# The prompt version is the field people leave out and then need most. An
# extraction is only explainable if you know which prompt produced it.
# ---------------------------------------------------------------------------

# Keys that would drag document content into the log. An audit trail is read by
# more people than the source data is -- support, auditors, whoever inherits
# this -- so it must record that a document was processed without becoming a
# second, less protected copy of it.
_PAYLOAD_KEYS = {"text", "document", "content", "body", "payload", "raw", "source_text"}


def digest(text):
    """Short SHA-256 of some text. Truncated to 16 hex characters because this
    identifies a document, it does not protect one."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def document_reference(path, text):
    """A stable identifier for a document that is not the document.

    The digest lets an auditor prove which exact bytes produced a row: rehash
    the file, compare. If the file changed, the hashes diverge and the record
    is still honest about what it saw.
    """
    return {
        "source_file": Path(path).name,
        "sha256": digest(text),
        "bytes": len(text.encode("utf-8")),
    }


class AuditLog:
    """Append-only JSONL. One record per document, written as it happens."""

    def __init__(self, path, allowlist, run_id, prompt_version, mode):
        # Even the audit log goes through the allowlist. A logger that can write
        # anywhere is a way to write anywhere.
        self.path = allowlist.write(path)
        self.run_id = run_id
        self.prompt_version = prompt_version
        self.mode = mode

    def record(self, **fields):
        """Append one record. Raises rather than quietly dropping a payload key."""
        leaked = _PAYLOAD_KEYS & set(fields)
        if leaked:
            # Fail loudly at the call site. A log that silently strips fields
            # trains people to stop reading it.
            raise ValueError(f"refusing to log document payload: {sorted(leaked)}")

        entry = {
            # UTC, ISO 8601. Local timestamps in an audit log are a dispute
            # waiting to happen the first time the run crosses a DST boundary.
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": self.run_id,
            "mode": self.mode,
            # The single field that makes a past decision reproducible.
            "prompt_version": self.prompt_version,
            **fields,
        }
        # "a" is the whole mechanism: open, append, close, per record. Slower
        # than holding a handle, and it means a crash mid-run keeps every record
        # written before it. Buffering an audit log loses exactly the records
        # you wanted, because the interesting runs are the ones that die.
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# GATE 4 -- SHADOW MODE
#
# The failure this prevents: you find out the extraction is wrong on real
# documents by looking at the damage. Shadow mode runs the whole pipeline
# against real inputs and writes nothing, so you can diff a week of intended
# output against what a human actually did before anything is at stake.
#
# It is default-on here for a reason. Shadow that must be switched on is shadow
# that is off, and retrofitting it means threading a flag through every write
# in the codebase and trusting that nobody missed one.
# ---------------------------------------------------------------------------


class RunMode:
    """Shadow unless three independent things say otherwise."""

    def __init__(self, live, approval=None):
        self.live = live
        self.approval = approval

    @property
    def label(self):
        return "live" if self.live else "shadow"

    @classmethod
    def decide(cls, *, live, confirmed, approval_token, registry_path,
               allowlist, agent_id, prompt_version):
        """Default to shadow. Going live needs a flag, a confirmation, and a ticket.

        Each of the three is weak alone. Together they mean nobody writes to
        production because they had the wrong shell history.
        """
        if not live:
            return cls(live=False)

        if not confirmed:
            # The second flag is not security -- it is a speed bump against the
            # up-arrow. It exists so --live cannot be the last thing you typed.
            raise ApprovalError(
                "--live also requires --i-understand-this-writes.\n"
                "  Shadow mode writes nothing; live mode writes the CSV for real."
            )

        approval = require_approval(
            token=approval_token,
            registry_path=registry_path,
            allowlist=allowlist,
            agent_id=agent_id,
            prompt_version=prompt_version,
        )
        return cls(live=True, approval=approval)

    def describe(self):
        if not self.live:
            return "shadow (default) -- no file will be written"
        a = self.approval
        return (f"live -- authorised by {a['token']}, approved by {a['approved_by']} "
                f"on {a['approved_on']}, expires {a['expires_on']}")


# ---------------------------------------------------------------------------
# GATE 5 -- THE HUMAN GATE
#
# The failure this prevents is the one that ends careers: the agent went live
# and the only record of the decision is a merged pull request. "Who approved
# this?" has no answer, so the answer becomes the name of whoever ran it.
#
# The distinction that matters: --live is a flag, and a flag is something one
# engineer can flip at 6pm. This checks an approval record that a different
# person had to create, and it fails closed on every branch -- missing file,
# unparseable file, unknown token, expired token, wrong prompt version.
#
# That last one is the part people skip. The approval is bound to the exact
# prompt version it was granted for. Edit the prompt without re-approving and
# the run refuses to go live, because the thing that was reviewed is not the
# thing that would now run.
# ---------------------------------------------------------------------------


def require_approval(*, token, registry_path, allowlist, agent_id, prompt_version):
    """Return the approval record, or raise. There is no third outcome."""
    if not token:
        raise ApprovalError(
            "live mode requires --approval CHG-...\n"
            "  A flag an engineer can flip is not a gate. Point this at a change "
            "reference someone else signed off."
        )

    path = allowlist.read(registry_path)
    try:
        registry = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ApprovalError(f"no approval registry at {path}") from None
    except json.JSONDecodeError as err:
        # An unreadable registry is a refusal, not a warning. The alternative is
        # a corrupt file that silently grants everything.
        raise ApprovalError(f"approval registry at {path} is not valid JSON: {err}") from None

    matches = [a for a in registry.get("approvals", []) if a.get("token") == token]
    if not matches:
        raise ApprovalError(f"approval {token} is not in {Path(path).name}")
    approval = matches[0]

    if approval.get("agent") != agent_id:
        raise ApprovalError(
            f"approval {token} covers agent '{approval.get('agent')}', not '{agent_id}'"
        )

    if approval.get("prompt_version") != prompt_version:
        raise ApprovalError(
            f"approval {token} was granted for prompt version "
            f"'{approval.get('prompt_version')}' but this run uses '{prompt_version}'.\n"
            "  The prompt changed since it was reviewed. Re-approve, or run in shadow."
        )

    # Approvals expire because "we approved that in 2024" is not consent to run
    # it today against data nobody has looked at since.
    expires = date.fromisoformat(approval["expires_on"])
    if date.today() > expires:
        raise ApprovalError(f"approval {token} expired on {expires.isoformat()}")

    return approval


# ---------------------------------------------------------------------------
# The summary. Governance that nobody reads is paperwork; the run has to end
# with something a human can act on without opening the log.
# ---------------------------------------------------------------------------


class RunSummary:
    """Counts for the end-of-run report."""

    def __init__(self, run_id, mode):
        self.run_id = run_id
        self.mode = mode
        self.started = time.time()
        self.processed = 0
        self.extracted = 0
        self.review = 0
        self.failed = 0
        self.stopped_reason = None

    def render(self, budget, output_path, wrote):
        # Three outcomes, not two: written, deliberately not written (shadow),
        # and not written because the run stopped. Collapsing the last two into
        # "no output" is how a halted run gets mistaken for a clean one.
        if wrote:
            verb = "written to"
        elif self.stopped_reason:
            verb = "NOT written, run incomplete;"
        else:
            verb = "would have been written to"
        lines = [
            "",
            "-" * 68,
            f"run {self.run_id}  |  mode: {self.mode}",
            "-" * 68,
            f"  documents processed     {self.processed}",
            f"  rows extracted          {self.extracted}  ({verb} {output_path})",
            f"  routed to human review  {self.review}",
            f"  failed                  {self.failed}",
            f"  budget consumed         {budget.describe()}",
            f"  elapsed                 {time.time() - self.started:.1f}s",
        ]
        if self.stopped_reason:
            # A truncated run that reports like a complete one is worse than a
            # crash, because the CSV looks finished.
            lines.append(f"  STOPPED EARLY           {self.stopped_reason}")
        if not wrote and self.mode == "shadow":
            lines.append("  no file written -- shadow mode. Re-run with --live "
                         "--i-understand-this-writes --approval CHG-...")
        lines.append("-" * 68)
        return "\n".join(lines)


def new_run_id():
    """Correlates the CSV, the audit records and whatever the operator remembers."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + os.urandom(3).hex()


def render_csv(rows, fieldnames):
    """Build the CSV in memory so shadow and live produce it identically.

    Shadow mode must exercise the same code path as live mode, or it is testing
    something other than what will run. The only difference between the two
    branches downstream is whether these bytes reach a file.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
