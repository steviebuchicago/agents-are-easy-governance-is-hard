"""Read a folder of invoices, extract structured fields, write a CSV.

One model call per document. Works, in about forty lines.

    export ANTHROPIC_API_KEY=sk-ant-...
    python agent.py
    python agent.py --input sample_docs --output invoices.csv
"""

import argparse
import csv
import json
import pathlib

import anthropic

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

client = anthropic.Anthropic()


def extract(text):
    """One model call per document. Returns the fields above as a dict."""
    reply = client.messages.create(
        model=MODEL, max_tokens=MAX_OUTPUT_TOKENS, system=SYSTEM,
        messages=[{"role": "user", "content": text}],
    )
    body = reply.content[0].text.strip().strip("`").removeprefix("json").strip()
    return json.loads(body)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", default="sample_docs")
    ap.add_argument("--output", default="invoices.csv")
    args = ap.parse_args()

    rows = []
    for path in sorted(pathlib.Path(args.input).glob("*.md")):
        try:
            rows.append({"source_file": path.name, **extract(path.read_text("utf-8"))})
        except Exception as err:
            print(f"skipped {path.name}: {err}")

    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_file"] + FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
