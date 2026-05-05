# 01 · Inbox triage

Scores incoming email on urgency, revenue, and replyability. Drafts a
reply in your voice for anything that scores above the threshold.

## Run

```bash
python 01_inbox_triage/triage.py --dry-run \
  --input 01_inbox_triage/examples/sample_inbox.json
```

`--dry-run` prints the drafts to stdout. Without it, drafts are saved
to `01_inbox_triage/drafts/<id>.txt`.

## Configure

- `voice_samples.txt` — paste 3 of your own recent sent emails. This is
  the single biggest factor in draft quality.
- `prompt.md` — the prompt itself. Edit freely.
- `TRIAGE_REVENUE_THRESHOLD` in `.env` — default 7.

## Wire to real Gmail

This script reads from a JSON file so you can test without auth. To
read live mail, replace `load_emails()` with a Gmail API call. The free
guide explains the OAuth setup; the paid version ships it pre-wired.

## Why the threshold matters

Without a threshold you'll have 100 drafts a day and trust none of
them. The threshold is the product. Tune it to your traffic.
