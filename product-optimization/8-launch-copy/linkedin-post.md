# LinkedIn launch post

**Length:** ~300 words (LinkedIn's sweet spot for builder-voice posts)
**When:** Same day as the X thread. Different audience, same trust signal.
**Format:** No emojis, no "I help X do Y" line, no "thoughts?" closer.

---

I cancelled a $200/month Zapier subscription last quarter.

Not because Zapier is bad — it isn't. Because everything I was using it for was glue. Glue between Gmail, Stripe, Notion, my CRM. Every time an API rotated, the glue broke. Twice a month, on average.

The Claude API made the glue cheap enough to write myself.

So I rebuilt my entire ops layer in five Python scripts:

— Inbox triage that scores emails on revenue impact and drafts replies in my voice
— Invoice follow-up that tiers messages by days overdue
— Meeting notes that extract decisions and actions, not transcripts
— Lead enrichment that produces a one-page brief before any sales call
— Weekly review that's written like a chief of staff who isn't afraid to tell me when I wasted the week

Total: about 600 lines of Python. Costs me roughly $4 a month in API fees.

The thing I learned building these:

The model isn't the moat. The constraint is.

The inbox triage script only works because it has a revenue threshold. Without it I'd have a hundred drafts a day and trust none of them. The threshold is the product.

The meeting notes script only works because the prompt forces "AMBIGUOUS — needs clarification" instead of letting Claude smooth over confusion. The honesty is the product.

That's the pattern. The AI does the thinking. You keep the deciding.

I open-sourced all five today, MIT-licensed. Free for any solo founder, consultant, or one-person team to fork and run.

Repo's in the comments. If it saves you an hour this week, that's the goal.

---

**First comment** (post immediately after, gets the link out of the algorithm-suppressed main post):

```
Repo here for anyone who wants it: github.com/[your-handle]/claude-automations-starter

Free, MIT, runs on your machine with your own Anthropic API key. Setup
is `git clone` + drop in your key + run with `--dry-run`. Five minutes.

If you build something on top of it, tag me — I want to see what
people do with workflow #5 (the weekly review). That's the one that
changed how I run the business.
```

---

## Optional: companion long-form (publish 3 days later)

Title: **"Automate the thinking, not the deciding."**

500–700 words expanding the principle from the post. Same audience
will reshare. Use this as the connective tissue across the channel —
quote it in the YouTube video, drop it in the email sequence.
