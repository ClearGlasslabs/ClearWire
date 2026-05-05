# 02 · Invoice follow-up

Drafts an escalating follow-up message for each overdue invoice. Tiers
by days late: 7 (warm), 14 (direct), 30 (firm).

## Run

```bash
python 02_invoice_followup/followup.py --dry-run \
  --csv 02_invoice_followup/invoices.example.csv
```

## Wire to Stripe (optional)

Replace `load_invoices()` with a Stripe API query for unpaid invoices.
The CSV format is what the Stripe response gets normalized into anyway.

## Why context matters

Feed the script the last message you exchanged with the client. Without
it you get a generic dunning-bot tone. With it you get a message that
sounds like the actual relationship.
