# 05 · Weekly review

Sunday-night chief-of-staff synthesis. Honest, not encouraging.

## Run

```bash
python 05_weekly_review/review.py \
  --week 05_weekly_review/examples/week.json \
  --out reviews/2026-W18.md
```

## Wire to your stack

The script takes a JSON blob with whatever you can pull from:
- Calendar (Google Calendar, Cal.com, etc.)
- Sent email count by category
- GitHub commits per day per repo
- Stripe revenue
- Free-text notes from you

Build a small script per data source, dump them all into `week.json`,
schedule the whole pipeline as a Sunday-night cron.

## The "be honest" instruction

Default LLM tone is encouraging-coach. You want a chief of staff who
will tell you when you spent the week on busywork. The prompt forces
this and it works.
