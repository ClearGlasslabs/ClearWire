# Show HN post

**One shot only.** HN punishes resubmits. Submit Tuesday or Wednesday,
between 7–10am ET. Watch the front page for the next 4 hours and reply
to every comment within 15 minutes during that window.

---

## Title (under 80 chars; HN-style — no emojis, no clickbait)

```
Show HN: 5 Claude API automations I run my one-person business on
```

Backup titles if first one underperforms in /newest:

```
Show HN: I cancelled my $200/mo Zapier stack and replaced it with 80 lines of Python
Show HN: Claude-Automations-Starter – inbox triage, invoice nudges, weekly reviews
```

## URL field

Link directly to the GitHub repo. Not a landing page. HN penalizes
landing pages on Show HN.

```
https://github.com/[your-handle]/claude-automations-starter
```

## Text body (the post body; keep short)

```
Hi HN,

I run a one-person consulting business and was paying ~$200/mo for
Zapier + a couple of niche SaaS automations. They broke roughly twice
a month whenever an upstream API rotated.

Claude got good enough at structured output and tool use that I
replaced the whole stack with five Python scripts. Total runtime cost
is about $4/mo in API fees.

What's in the repo:

  1. Inbox triage — scores email on urgency/revenue/replyability,
     drafts replies for high-revenue threads. Voice samples passed in
     as context (this is what makes the drafts not sound robotic).
  2. Invoice follow-up — tiered messages (7d / 14d / 30d) with the
     last 3 messages with the client as context.
  3. Meeting notes — decisions + action items, with the prompt forced
     to mark ambiguity rather than smooth over it.
  4. Lead enrichment — one-page brief before sales calls. Brave Search
     for sources. "Don't guess" instruction in the prompt does real work.
  5. Weekly review — chief-of-staff style synthesis from your week's
     calendar / email / commits / revenue.

Each script is <150 lines. Prompts are in separate `.md` files so you
can edit them without touching code.

The thing I'd be most curious about is the prompts. Each one has 1–2
constraints that took me weeks to land. Section in each README labeled
"Why this works" if you want to skim.

MIT-licensed. Runs on your machine, your API key, no telemetry.
Issues and PRs welcome — especially prompt variants for the existing
workflows.

What you'd want me to add next?
```

## Anti-patterns to avoid

- Don't post a thread. HN doesn't have threads. Single text body.
- Don't link to your Gumroad product in the post body. HN will flag
  it as spam. The repo README has the link — that's enough.
- Don't reply to "this is just a wrapper" with anything other than:
  *"Yes. The wrapper is the product. Constraints + prompts + voice
  samples are 90% of the value here."*
- Don't karma-bait by replying to your own post or asking friends to
  upvote — HN detects this and will dead-list you.

## What success looks like

- 30+ upvotes in first 2 hours = stays on /newest, has a chance
- 80+ upvotes by hour 4 = front page candidate
- Front page = ~5,000 GitHub visits, ~300 stars, ~50 PDF downloads
- That's 50 emails into your sequence — enough to start measuring conversion

## What to do during the launch window

1. Pin a comment with the most useful link (probably the inbox triage README)
2. Reply to every top-level comment within 15 minutes for the first 4 hours
3. When someone asks "how does this compare to [X]?" — answer specifically,
   admit what X does better
4. When someone finds a bug, fix it on the spot and link the commit
5. Do NOT promote the paid product in any reply. Let the README do that.
