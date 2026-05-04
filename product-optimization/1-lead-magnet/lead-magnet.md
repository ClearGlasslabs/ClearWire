# 5 Claude API Automations That Saved Me 10+ Hours a Week

**A free guide for solo founders, indie devs, and consultants who want to stop drowning in admin work.**

By [Your Name] · ClearGlass

---

## Who this is for

You run a one-person business — consulting, indie SaaS, content, agency-of-one.
You ship real work. You also lose an hour a day to inbox triage, follow-ups,
invoice nudges, meeting notes, and CRM updates.

You don't need another $200/mo SaaS subscription. You don't need a Zapier maze
that breaks every time an API changes. You need code you control, that runs on
your machine, that does exactly what you tell it.

This guide gives you five automations I run every day. Each one is a working
Python script using the Claude API. Total setup time: under an hour.

---

## What you'll need

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com)
- 30–60 minutes
- Roughly $1–5/month in API costs at solo-operator volume

All five scripts are in the companion repo:
**github.com/[your-handle]/claude-automations-starter**

---

## Automation 1 — Inbox triage that actually understands intent

**Time saved: ~3 hours/week**

The standard "AI inbox" tools sort by keyword. They're useless because the
problem isn't sorting — it's *deciding what to reply to first*. Claude is good
at this because it can read the actual content and rank by your priorities.

**What it does:**
- Pulls last 24h of unread emails (Gmail API)
- Asks Claude to score each one on: urgency, revenue impact, replyability
- Drafts a reply for every email scoring above a threshold
- Leaves drafts in Gmail for you to review and send

**The prompt that makes it work:**

```
You are triaging the inbox of a solo consultant who bills $250/hr.
Score this email 1–10 on three axes:
- urgency: does it need a response within 24h?
- revenue: is there money on the line, directly or indirectly?
- replyability: can a 3-sentence reply close the loop?

Return JSON only. If revenue >= 7, draft a reply in the user's voice
(short, direct, no pleasantries beyond "Hi [name]").

Email:
{email_body}

User's voice samples:
{three_recent_sent_emails}
```

**The trick most people miss:** feeding Claude three of your own recent sent
emails as voice samples. Without that, replies sound like a chatbot. With it,
they sound like you on a good day.

**File:** `01_inbox_triage.py` in the repo.

---

## Automation 2 — Invoice follow-up without being annoying

**Time saved: ~1 hour/week. Cash recovered: significant.**

Most overdue invoices aren't refusals. They're forgotten. But the awkwardness
of asking a third time is enough that solo operators just… don't. Claude
removes the awkwardness because it writes the message for you, in your voice,
calibrated to how late the invoice is and how the relationship is going.

**What it does:**
- Reads your invoice tracker (Stripe, Notion, or a CSV)
- Identifies invoices >7, >14, >30 days overdue
- Drafts a follow-up message escalating in firmness with each tier
- Optionally: sends via Gmail or saves as draft

**The escalation logic:**
- 7 days: warm nudge ("just bumping this in case it slipped")
- 14 days: direct ("can you confirm a payment date?")
- 30 days: firm ("I'll need to pause work / add a late fee Friday")

The script feeds Claude the tier *and* the last three messages with the
client. That context is what keeps it from sounding like a collections bot.

**File:** `02_invoice_followup.py`

---

## Automation 3 — Meeting notes that capture decisions, not transcripts

**Time saved: ~2 hours/week**

Every meeting tool gives you a transcript. Nobody wants a transcript. You want
*the decisions made* and *the actions assigned*, in a format you can paste into
Notion or send to the client in five seconds.

**What it does:**
- Takes a Zoom/Granola/Otter transcript as input
- Asks Claude to extract: decisions, action items (with owners), open questions, follow-up date
- Outputs a clean markdown summary
- Optionally writes to Notion via API

**The prompt:**

```
Read this meeting transcript. Extract:

1. Decisions made (bullet list, one line each)
2. Action items, with owner and deadline if mentioned
3. Open questions left unresolved
4. Suggested follow-up date based on conversation

Ignore small talk. Ignore tangents. If something is ambiguous, mark it
"AMBIGUOUS — needs clarification" rather than guessing.

Output format: markdown.

Transcript:
{transcript}
```

**Why this is better than tool-built summaries:** the "AMBIGUOUS" instruction.
Default LLM summarizers smooth over confusion, so you discover the
miscommunication two weeks later. Forcing it to flag ambiguity surfaces
problems immediately.

**File:** `03_meeting_notes.py`

---

## Automation 4 — Lead enrichment before the first call

**Time saved: ~30 min per call. Conversion lift: real.**

Before any sales or discovery call, you should know: what their company does,
what they shipped recently, what their stack is, what they probably care about.
Most people skip this because it takes 20 minutes per lead. Claude does it in
30 seconds.

**What it does:**
- Takes a name + company (or LinkedIn URL)
- Pulls public info via Brave Search API or similar
- Asks Claude to synthesize a one-page brief: company, role, recent moves,
  likely pain points, suggested talking points

**The prompt:**

```
You're prepping a 30-min discovery call. Given the public info below,
write a one-page brief covering:

- 2-sentence company summary
- Their probable revenue stage (seed / growth / mature)
- 3 things they shipped or announced in the last 90 days
- 3 likely pain points based on stage and stack
- 2 questions I should ask in the first 5 minutes
- 1 thing I should NOT bring up

Be specific. If you don't know something, say so. Don't guess.

Public info:
{search_results}
```

The "don't guess" instruction matters. Without it, Claude will invent
plausible-sounding details. With it, you get a brief you can trust.

**File:** `04_lead_enrichment.py`

---

## Automation 5 — Weekly review that runs itself

**Time saved: ~1 hour/week. Strategic clarity: high.**

Every solo operator knows they should do a weekly review. Almost none do.
Reason: it's another 60 minutes of work at the end of an exhausting week.
Automate the data gathering and you only have to read.

**What it does:**
- Pulls your week from: calendar, Gmail sent folder, GitHub commits, Stripe
  revenue, time tracker
- Asks Claude to synthesize: what got done, what stalled, where time leaked,
  what to focus on next week
- Emails you the summary Sunday night

**The prompt:**

```
You're my chief of staff. Below is everything I did this week across
calendar, email, code, and revenue.

Write a weekly review covering:
1. Top 3 wins (specific outcomes, not activities)
2. Top 3 stalls (what didn't move, and the likely reason)
3. Time allocation (% on revenue work vs. admin vs. learning vs. other)
4. One pattern I should notice
5. The single most important thing to focus on next week, with reasoning

Be honest. If I spent the week on busywork, say so. I'd rather hear it
from you than figure it out in three months.

Data:
{aggregated_week_data}
```

The "be honest" instruction is doing real work here. Default LLM tone is
encouraging-coach. You want an honest chief of staff.

**File:** `05_weekly_review.py`

---

## What to do next

1. Clone the repo: `git clone github.com/[your-handle]/claude-automations-starter`
2. Copy `.env.example` to `.env` and add your Anthropic API key
3. Pick the automation that solves your biggest pain — set it up first
4. Run it daily for a week. Tweak the prompts to your voice.

If you want the full system — 12 production-ready workflows, the prompt
library, the setup walkthrough video, and a private Discord — that's the
**ClearGlass AI Automation Assistant**. One-time payment, runs on your machine,
your API key.

→ [Get the full system on Gumroad](https://clearglassinc.gumroad.com/l/ai)

---

## A note on tradeoffs

These automations work because they're small, focused, and you own the code.
That also means: if the Claude API changes, you're the one who fixes it. If
Gmail rotates an OAuth scope, you're the one who re-authorizes.

If you want a hosted, no-code version — this isn't that. Use Zapier.

If you want to actually understand how your automations work, save $200/mo on
SaaS subscriptions, and have a system you can extend yourself — start here.

---

*Questions? Reply to the email this came with. I read every one.*
