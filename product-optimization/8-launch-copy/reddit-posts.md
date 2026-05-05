# Reddit posts (bonus — high-leverage, low-effort)

Three subreddits, three slightly different angles. Post on different
days (one per day) so they don't trigger Reddit's cross-posting filter.

---

## r/ClaudeAI

**Title:** I open-sourced 5 Claude API workflows I run my one-person business on

**Body:**

```
Five scripts I use every day. Inbox triage, invoice follow-up, meeting
notes, lead enrichment, weekly review.

Each one is <150 lines of Python with the prompt in a separate .md
file. The interesting part is in the prompts:

- Inbox triage passes 3 of my own sent emails as voice samples. Without
  them, drafts sound like a chatbot.
- Meeting notes prompt forces "AMBIGUOUS — needs clarification" instead
  of letting Claude smooth over confusion.
- Lead enrichment prompt says "If you don't know, write 'unknown'. Do
  not guess." Hardest line to land but it's what makes the brief usable.
- Weekly review prompt: "If I spent the week on busywork, say so. I'd
  rather hear it from you than figure it out in 3 months."

MIT, runs on your machine, your API key.

github.com/[your-handle]/claude-automations-starter

Curious what other people are using Claude for in their own ops —
particularly any workflow #6 ideas you wish existed.
```

---

## r/SideProject

**Title:** I cancelled $200/mo of SaaS and replaced it with 5 Python scripts

**Body:**

```
Was paying ~$200/mo for Zapier + a couple of niche AI automation tools.
They broke twice a month on average. Claude API got cheap and capable
enough that I rebuilt the whole thing.

Five scripts: inbox triage, invoice follow-up, meeting notes, lead
enrichment, weekly review. Total runtime cost ~$4/mo.

Open-sourced today. MIT-licensed. Free.

github.com/[your-handle]/claude-automations-starter

Not a sales pitch — I have a paid version with more workflows but the
free 5 do most of the work for solo operators. Linked in the README if
anyone wants more.

Happy to answer questions about how the prompts work — the prompts are
where 90% of the leverage is.
```

---

## r/Entrepreneur or r/SmallBusiness

**Title:** I built 5 AI scripts that handle the admin work in my one-person business

**Body:**

```
Solo consultant here. The admin work was eating ~10 hours/week. Tried
Zapier, tried VAs, tried just powering through — none worked.

What did work: 5 small Python scripts using the Claude API.

1. Inbox triage — scores emails by revenue impact, drafts replies for
   the ones that matter
2. Invoice follow-up — tiered nudges for overdue invoices (recovered
   ~$12k in 90 days from invoices I'd been "meaning to chase")
3. Meeting notes — decisions and action items, not transcripts
4. Lead enrichment — one-page brief before any sales call
5. Weekly review — Sunday night chief-of-staff synthesis

Cost: about $4/mo in API fees. Versus $200/mo of SaaS this replaced.

Just open-sourced all five. MIT licensed.
github.com/[your-handle]/claude-automations-starter

The setup is `git clone` → drop in your Anthropic API key → run with
`--dry-run`. Maybe 30 minutes if you've used Python before.

Caveats: requires basic Python literacy. When the API changes, you
patch it. If those are dealbreakers, just stay on Zapier.

Otherwise — fork it, run it, tell me what to build next.
```

---

## Rules for Reddit (different from X / LinkedIn)

- **Don't title-bait.** Reddit hates "I made $5k", "this changed my
  life", emojis in titles. Be specific and dry.
- **Don't link to the paid product in the post body.** Link to the
  repo only. The repo README does the upsell.
- **Reply to every comment for 24 hours.** Reply karma matters more
  than post karma here.
- **If a mod removes your post, message them — don't repost.**
  Often it's a flair issue, fixable in 2 minutes.
- **Don't crosspost the same body.** Each subreddit gets its own
  angle. The version above already does that.

## What success looks like on Reddit

- 50+ upvotes on r/ClaudeAI = strong (small sub)
- 200+ upvotes on r/SideProject = strong
- 500+ on r/Entrepreneur = strong but rare
- A pinned comment with the repo link gets 3–5x the clicks of a body link
- ~5–10% of upvoters will visit the repo. ~5% of those will star.

Reddit is a long tail — the post will keep driving traffic for months
through search. Worth the 20 minutes.
