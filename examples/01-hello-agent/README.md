# 01 — Hello, Agent

Reads a folder of invoices, extracts structured fields from each one, writes a CSV. Forty lines, and it works.

```bash
cd examples/01-hello-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python agent.py
```

```
wrote 5 rows to invoices.csv
```

---

## What it does

`sample_docs/` holds five invoices from three fictional vendors, written the way invoices actually arrive: a markdown table, a fixed-width text dump, a freight bill, a second invoice from the same vendor in a different layout, and one bad OCR scan.

For each file, `agent.py` makes a single model call and asks for seven fields as JSON — invoice number, vendor, invoice date, due date, currency, total, and the model's own confidence in the extraction. The results go into `invoices.csv`.

```
source_file,invoice_number,vendor,invoice_date,due_date,currency,total_amount,confidence
01-northgate-supply-2418.md,NG-2418,Northgate Supply Co.,2026-03-14,2026-04-13,USD,2132.13,0.97
02-lakeshore-print-0917.md,0917-LPW,Lakeshore Print Works,2026-03-22,2026-04-21,USD,2655.3,0.96
03-ridgeline-logistics-55120.md,RL-55120,Ridgeline Logistics,2026-03-19,2026-04-18,USD,897.72,0.98
04-northgate-supply-2431.md,NG-2431,Northgate Supply Co.,2026-03-27,2026-04-26,USD,1411.56,0.94
05-ridgeline-logistics-scan.md,RL-55147,Ridgeline Logistics,,,USD,917.74,0.41
```

Point it at your own folder with `--input` and `--output`.

## What it gets right

This is not a strawman. It is a good piece of software for what it is, and most of what makes it good is what it leaves out.

**One call per document.** No chaining, no agent loop, no tool use. The job is "read this, return these fields," and that is one prompt. Reaching for an agent framework here would add moving parts to a problem that has none.

**No parsing rules.** The five documents share no layout. A regex approach would need a branch per vendor and would break the first time Northgate changed their template. The model reads all five formats with the same prompt, which is the actual reason this technique is worth using.

**Structured output as the interface.** Asking for JSON with a fixed key set means the boundary between the model and the rest of the program is a dict, not prose. Everything downstream is ordinary Python.

**It admits uncertainty.** The `confidence` field costs nothing to ask for, and on the OCR scan it comes back at 0.41 — the model correctly signals that it could not read the invoice number cleanly, could not tell 03/04/26 apart as March or April, and found two candidate totals on the page.

**It fails per document, not per run.** A file that will not parse prints a line and the loop continues. Four good rows beat zero good rows.

That combination — one call, no rules, typed output, graceful skip — is the right shape for this problem. If you built this in an afternoon you built the right thing.

## What this doesn't do

Everything above is true, and none of it is what stops this from running somewhere that matters. The gaps are not in the extraction:

- **It can write anywhere.** `--output` goes straight to `open()`. Pass it a path in a shared drive and it writes there. Nothing in the program has an opinion about which paths are legitimate.
- **It has no ceiling.** Point it at a folder of ten thousand documents, or add a retry around a call that fails deterministically, and it will keep spending until it finishes or you notice.
- **It leaves no record.** When someone asks in June why row 5 says 917.74 and not 1132.74, there is no answer. The prompt has been edited since, `invoices.csv` has been overwritten twice, and nothing recorded which version of which prompt produced which number.
- **It cannot be tested on real data safely.** The only way to see what it does to production inputs is to let it write to production outputs.
- **Nobody approved it.** It runs because it is on disk and someone typed the command.
- **It sees the 0.41 and writes the row anyway.** The confidence is in the CSV and nothing acts on it. The information exists; the mechanism does not.

Those six gaps are the whole subject of the next directory. [`02-governed-agent`](../02-governed-agent/) does the identical job — same prompt, same model, same seven fields, byte-identical CSV — and closes each of them.

Read the two `agent.py` files side by side. The extraction is the same code.
