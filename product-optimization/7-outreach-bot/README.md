# Outreach drafter

Generate 10 personalized outreach drafts a day to land the first
testimonials. NOT a spam tool — the script drafts, you send manually.

## The job

You need 3–5 testimonials before the Gumroad page converts cold
traffic. The fastest way: hand free copies to solo founders and
consultants who are publicly complaining about the problem this product
solves, in exchange for an honest review.

Goal: 10 messages a day for 7 days = 70 sends → ~10–15 replies →
3–5 testimonials.

## Run

```bash
python outreach.py --leads leads.example.csv --dry-run
```

`--dry-run` prints to stdout. Without it, drafts go to `drafts/`.

## Lead CSV format

| field | meaning |
|---|---|
| `name` | First + last |
| `handle` | Username, no `@` for filenames |
| `platform` | `x` / `linkedin` / `email` / `reddit` |
| `why_them` | One sentence: why this person specifically |
| `public_signal` | Something they posted publicly to reference in line 1 |
| `contact` | URL or email — where you'll actually send |

## Why it has to be specific

A generic "loved your work, want a free copy?" gets 0 replies. A
message that opens with their actual tweet from last week, references
the actual problem they described, and offers to solve it — that gets
20–30% reply rates.

The bot can't find the public signal for you. You have to do that part
manually. That's the work.

## Rules

- Send max 10 per day per platform (avoid spam flags)
- Send manually. Read each draft before pasting.
- Track in a spreadsheet: name, sent date, reply, tester status, testimonial received
- After 7 days, review what worked. Tweak the prompt. Run another 7-day batch.
