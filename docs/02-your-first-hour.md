# Your First Hour

You will have a working agent in about fifteen minutes. The other forty-five are for understanding what you actually built, which is the part that matters.

No prior experience assumed. If you have never run a Python script, you are in the right place and nothing below is going to embarrass you.

---

## What you need

- **Python 3.11 or newer.** Check with `python3 --version`. If it reports 3.10 or lower, install a newer one before you go further — the examples are written and tested against 3.11.
- **A terminal.** Terminal on macOS, Windows Terminal or WSL on Windows, whatever you already use on Linux.
- **An Anthropic API key.** This is separate from a Claude subscription. It is a billing relationship for programmatic access, and it is what lets code you run talk to the model.
- **About fifteen minutes** of not being interrupted.

---

## Step 1 — Get an API key

Sign in at [console.anthropic.com](https://console.anthropic.com), go to API keys, and create one. It looks like `sk-ant-...`.

You can see the full key exactly once. Copy it somewhere before you close the dialog.

Two rules, both of which you will be glad of later:

1. **Never paste it into a source file.** Keys committed to git are the single most common way they leak, and they are not recoverable once public — you rotate them and hope.
2. **Check your billing setup.** Programmatic access needs credit. If the account has none, your first run fails in a way that looks like a code problem and is not.

---

## Step 2 — Get the code running

```bash
git clone https://github.com/steviebuchicago/agents-are-easy-governance-is-hard.git
cd agents-are-easy-governance-is-hard/examples/01-hello-agent

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python agent.py
```

The virtual environment is the two lines people skip and then spend twenty minutes debugging. It keeps this project's packages separate from everything else on your machine. Once activated, your prompt shows `(.venv)` — if it does not, the activation did not take, and `pip install` just put the package somewhere your script will not look.

The `export` line sets the key for **this terminal window only**. Open a new tab and it is gone. That is a feature, not a nuisance.

What you are about to run reads five invoices in `sample_docs/` — five different layouts, including one bad OCR scan — and writes `invoices.csv`.

---

## Step 3 — Watch it run

There is a pause of several seconds, and then one line:

```
wrote 5 rows to invoices.csv
```

That is the whole user interface, and the pause is the interesting part. Each invoice is a network round trip: text goes to the model, structured fields come back. That is why this takes seconds rather than milliseconds, and why running it over four thousand documents is a different proposition from four.

Open `invoices.csv`. One row per document: invoice number, vendor, dates, currency, total, and a confidence score the model assigned to its own extraction.

Now do the thing most people skip. **Look at the last row.** The fifth document is a bad OCR scan, and its confidence comes back around `0.41` while the others sit above `0.94`. The model is telling you, accurately, that it struggled.

Then notice what happened to that warning. The row is in the CSV, with the same columns as the other four, in the same file. Nothing read the 0.41. Nothing routed it anywhere. The information exists and the mechanism does not.

That gap is the entire subject of this repository, and we come back to it below.

You can also point it at your own folder: `python agent.py --input some_folder --output result.csv`.

---

## When it fails

It probably will, once. These five account for most first runs.

### 1. `AuthenticationError` / "Could not resolve authentication method"

The key is not reaching the process. In order of likelihood: you set it in a different terminal window; you closed and reopened the terminal; you included the quotes or a trailing space when you copied it; you set `ANTHROPIC_KEY` instead of `ANTHROPIC_API_KEY`.

Check with `echo $ANTHROPIC_API_KEY` — you should see `sk-ant-...` and nothing else.

A close cousin: an error mentioning **credit balance**. That is not authentication, that is billing, and the fix is in the console rather than the terminal.

### 2. `ModuleNotFoundError: No module named 'anthropic'`

The Python running your script is not the Python you installed into. This is the single most common setup failure and it has nothing to do with agents.

Fix: confirm `(.venv)` is in your prompt, then run `python -m pip install -r requirements.txt`. The `python -m` form installs into the interpreter you are actually using, which a bare `pip` does not guarantee.

If instead you get a `SyntaxError` pointing at code that looks perfectly valid, run `python --version`. An old interpreter reports new syntax as your mistake.

### 3. `RateLimitError` / `Error code: 429`

You sent requests faster than your account tier allows. You will not hit this on five sample invoices; you will hit it the first time you point `--input` at a real folder, because the loop makes one call per file with no pause in it.

Short fix: run it over fewer files. Real fix: catch the error, wait, and retry with the delay doubling each time.

Note what just happened. The script has no opinion about rate limits, so it inherited whatever the API decided. That is your first governance lesson and it arrived inside ten minutes.

### 4. It runs cleanly and writes `wrote 0 rows`

The loop found no files. It looks for `*.md` in the input folder, so a folder of PDFs, `.txt`, or `.docx` produces a valid, empty CSV and a cheerful success message.

Check the path, then the extensions. A run that processes nothing looks almost exactly like a run that worked — remember that, because it is the same shape as the failure at the end of this document.

If files were found but some vanished, you will see a `skipped <filename>: <error>` line for each. The loop catches per-document failures and carries on. That is the right behaviour, and also why a partial result can pass for a complete one.

### 5. `JSONDecodeError: Expecting value: line 1 column 1`

The model returned something that is not parseable JSON. The script already strips a markdown code fence, so the usual remaining causes are a sentence of preamble before the object, or a response cut off partway because a long document hit the token limit.

Fix: print the raw response before parsing and look at what came back. If it is truncated, raise `max_tokens`. If it is chatty, make the instruction harder — "Return a single JSON object and nothing else" beats "return JSON" — and if the API offers a structured-output or tool-call mechanism, use that instead. Constraining the shape beats asking politely.

One thing not to do: never `eval()` a model response. Use a JSON parser.

---

## The honest debrief

Take a minute with what you have. It is a loop, a prompt, a parser, and a file write. That is not a simplification — it is genuinely the shape of most production agents, and the fact that it is this small is the good news.

**What it can do,** and this is not nothing: read five invoices in five different layouts, written by three different organisations with no agreed format, and turn them into rows you can sort. No parsing rules, no template per vendor. Ten years ago that was a project with a budget. Today it is forty lines.

**What it cannot do:**

- **Act on what it knows.** It asks the model for a confidence score and gets an honest one. Then it writes the 0.41 row into the CSV next to the 0.97 rows and moves on. Nothing reads that number.
- **Remember.** Run it twice and you get two independent results, with no notion that it has seen the file before.
- **Stop itself.** There is no ceiling on how many calls it makes or what they cost. A retry around a call that fails deterministically runs until you notice.
- **Prove what it did.** Terminal scrollback is not a record. The CSV gets overwritten on the next run, and nothing anywhere links a row to the prompt that produced it.
- **Refuse.** `--output` goes straight to `open()`. It writes wherever you point it, and it opens whatever is in the input folder, because nothing in the program has an opinion about which paths are legitimate.

**And one specific thing that will break it in production.** Not a crash. Crashes are the easy failures, because they announce themselves.

It is that 0.41 row. In the CSV it has the same eight columns as every other row, in the same file, in the same format. Whatever consumes that file — a ledger import, a reconciliation, a person under time pressure — **cannot distinguish it from the four rows that are right**. The uncertainty was measured and then discarded at the moment it mattered.

Now add six weeks. Someone asks why a payable says one number and the invoice says another. The prompt has been edited twice since, the CSV overwritten a dozen times, and nothing recorded which document produced which row or which prompt was running that Tuesday. The honest answer is "we think it worked," and that answer is why the project does not get approved.

None of this is fixed by a better prompt. It is fixed by structure: bounding what the agent may touch, recording what it did and why, and running it on real inputs while it writes nothing.

---

## Next

**See what fixes it** → [`../examples/02-governed-agent/`](../examples/02-governed-agent/). Same prompt, same model, a byte-identical CSV, roughly ten times the code. Run `python agent.py` there: it processes the same five invoices while writing nothing, routes the 0.41 scan to review, and leaves a record you can read. Diff the two `agent.py` files — the extraction is the same code, and every difference is a gate.

**Understand why this matters** → [The Governance Gap](03-the-governance-gap.md), where most agent projects quietly stop.

**Still deciding what to build with** → [Cowork vs Claude Code vs Agent SDK](01-cowork-vs-code-vs-agents.md). If you need a weekly report rather than a service, you may not need this code at all.
