# Video 1 Script — "I replaced my $200/month Zapier stack with 80 lines of Claude code"

**Target length:** 8–9 minutes
**Format:** Talking head + screen recording, 50/50
**Goal:** Drive viewers to the free PDF (lead magnet)
**Single CTA:** "Free guide in description — 5 Claude Automations That Saved Me 10 Hours a Week"

---

## Title options (test in YouTube Studio A/B)

1. I Replaced My $200/Month Zapier Stack With 80 Lines of Claude Code
2. Why I Deleted Zapier (And What I Built Instead)
3. The Claude API Killed My Zapier Subscription. Here's the Code.

**Pick #1 first.** Specificity ($200, 80 lines) outperforms cleverness.

## Thumbnail concept

- Left side: blurred Zapier dashboard, red X over it
- Right side: terminal window with green text, code visible
- Overlay text (large, sans-serif): **"$200/mo → $0"**
- Your face in bottom right, mild "can-you-believe-it" expression
- High contrast: black background, white code, one red accent

## Description (paste into YouTube)

```
I was paying $200/month for a Zapier stack that broke every time an API
changed. I replaced the whole thing with 80 lines of Python and the
Claude API. Here's exactly how, with code.

→ Free PDF: 5 Claude API Automations That Saved Me 10+ Hours a Week
   [link to landing page]

→ The full 12-automation system (paid):
   [link to Gumroad page]

→ Companion repo (free, MIT):
   github.com/[your-handle]/claude-automations-starter

Chapters:
0:00 The $200/mo problem
0:45 What I'm replacing (and what I'm keeping)
1:40 Build 1: inbox triage
3:30 Build 2: invoice follow-up
5:00 The architecture decision that matters
6:30 What this costs to run
7:30 The catch (be honest)
8:10 Free guide + repo
```

---

## Full script

> **Stage directions in italics.**
> Code/screen content in `code blocks`.

---

### 0:00–0:15 — HOOK (no greeting, no intro)

*Cut: terminal running. Show real output. Then cut to your face.*

> Last month I was paying two hundred dollars a month for a Zapier stack
> that broke every other week. I replaced the whole thing with eighty
> lines of Python and the Claude API. It's faster, it's cheaper, and I
> own the code. I'm going to show you exactly how.

*Cut to a Stripe screenshot showing the canceled $200 charge. Hold for 1 second.*

---

### 0:15–0:45 — PROMISE + CREDENTIALS

> By the end of this video you'll have two working automations: one that
> triages your inbox, one that chases your overdue invoices. Both
> running locally, both costing less than five dollars a month in API
> fees, both written in code you can read and change.
>
> I'm [name]. I run a one-person consulting business. I've been
> automating my own ops for the last three years, and the Claude API
> changed how I do it. Let's build.

*B-roll: quick montage of your terminal, your dashboard, your editor.*

---

### 0:45–1:40 — WHAT I'M REPLACING (and what I'm keeping)

> First, let me be honest about what I cut and what I kept. I didn't
> delete every SaaS tool I have. Notion stayed. Stripe stayed. Gmail
> obviously stayed. What I cut was the *glue layer* — Zapier, Make, and
> three little SaaS automation tools that each did one thing for fifteen
> dollars a month.
>
> Here's what they were doing.

*Show a simple diagram on screen.*

```
BEFORE:
  Gmail ──▶ Zapier ──▶ "AI inbox sorter" ──▶ back to Gmail
  Stripe ──▶ Zapier ──▶ "Invoice nudger" ──▶ Email
  Notion ──▶ Zapier ──▶ "Meeting notes formatter" ──▶ Notion
  Total: $200/mo. Breaks every 2-3 weeks.
```

> Each of these was doing something a smart intern could do in fifteen
> minutes. The reason I was paying for them was the glue. Zapier
> connecting things together.
>
> Once Claude got good at structured output and tool use, the glue
> stopped being the hard part. So I deleted it.

*Cut. New diagram.*

```
AFTER:
  cron ──▶ python script ──▶ Claude API ──▶ Gmail / Stripe / Notion
  Total: ~$3/mo in API fees.
```

---

### 1:40–3:30 — BUILD 1: INBOX TRIAGE

*Switch to screen recording. Talk over it.*

> Build one. Inbox triage. The job: pull the last twenty-four hours of
> unread email, score each one, and draft a reply for the ones that
> matter. Here's the whole thing.

*Show `triage.py`. Highlight in sections as you talk.*

```python
import anthropic
from gmail_api import fetch_unread, draft_reply

client = anthropic.Anthropic()

PROMPT = """
You are triaging the inbox of a solo consultant who bills $250/hr.
Score this email 1-10 on: urgency, revenue, replyability.
Return JSON. If revenue >= 7, draft a reply in the user's voice.

User's voice samples:
{voice_samples}

Email:
{email_body}
"""

def triage(email, voice_samples):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": PROMPT.format(
            voice_samples=voice_samples, email_body=email.body
        )}]
    )
    return parse_json(response.content[0].text)

for email in fetch_unread(hours=24):
    result = triage(email, load_voice_samples())
    if result["revenue"] >= 7:
        draft_reply(email, result["draft"])
```

> Three things I want you to notice.
>
> One: I'm passing voice samples. Three of my own recent sent emails.
> Without that, replies sound like a chatbot. With it, they sound like
> me. That's the difference between "I'll review the drafts" and "I'll
> just hit send."

*Pattern interrupt: cut to your face.*

> Two: the threshold. I only draft replies for emails scoring seven or
> higher on revenue. Otherwise I'd have a hundred drafts a day. The
> threshold is the product.

*Back to code.*

> Three: this runs as a cron job. Not a webhook, not a serverless
> function, not a Vercel deploy. A cron job on the same Mac mini I use
> for everything else. That's the architecture decision I want to come
> back to.

---

### 3:30–5:00 — BUILD 2: INVOICE FOLLOW-UP

> Build two. Invoice follow-up. The painful one.
>
> Most overdue invoices aren't refusals. They're forgotten. But the
> awkwardness of asking a third time is enough that solo operators just
> don't. Then six weeks later you realize you're owed eight thousand
> dollars and you've been doing nothing about it.
>
> So: tier the messages by how late the invoice is, write each one in
> your voice, and let Claude pick the right escalation.

*Show `followup.py`.*

```python
TIERS = {
    7:  "warm nudge — assume it slipped",
    14: "direct — ask for confirmation of payment date",
    30: "firm — mention pause / late fee",
}

def followup_message(invoice, history):
    days = (today() - invoice.due_date).days
    tier = max(t for t in TIERS if days >= t)

    prompt = f"""
    Write a follow-up message in the sender's voice.
    Tone: {TIERS[tier]}.
    Days overdue: {days}.
    Last 3 messages with this client: {history}

    Constraint: 4 sentences max. No "I hope this finds you well."
    """
    return claude(prompt)
```

> The thing that makes this work is the history. Without the last three
> messages with the client, you get a generic dunning bot. With it, you
> get a message that sounds like the actual relationship.
>
> I run this Friday morning. Takes thirty seconds. Recovered roughly
> twelve thousand dollars in the first ninety days.

*On-screen text: "+$12k in 90 days"*

---

### 5:00–6:30 — THE ARCHITECTURE DECISION THAT MATTERS

*Cut to your face. Slow down.*

> Now the part most people get wrong.
>
> When you watch tutorials on AI automation, almost all of them tell you
> to host things in the cloud. Vercel. AWS Lambda. Some serverless
> setup. For a solo operator, that's the wrong call.
>
> Here's why.

*Diagram on screen.*

```
Cloud-hosted automation:
  + scales to a million users
  - costs $20-50/mo minimum
  - OAuth re-auth flows are painful
  - your secrets live somewhere you don't control
  - one bad deploy and your inbox is broken at 2 a.m.

Local automation (cron + script):
  + costs ~$0
  + secrets stay on your machine
  + when it breaks you fix it by reading the log
  + you own everything
  - doesn't scale (you don't need it to)
```

> If you're a solo operator, your scale is one. Don't pay the cloud tax
> for scale you don't need. Run it on your laptop or a five-dollar VPS.
>
> When you're ready to sell this as a product to other people, *then*
> migrate. Not before.

---

### 6:30–7:30 — WHAT THIS COSTS TO RUN

> Real numbers. I pulled my Anthropic console for the last thirty days.

*Show actual screenshot of API usage. Black out anything sensitive.*

> Inbox triage: about a hundred emails a day, costs me roughly two
> dollars and forty cents a month.
>
> Invoice follow-up: runs once a week, maybe ten cents a month.
>
> Meeting notes, lead briefs, weekly review — the other three
> automations from the free guide — call it another two dollars.
>
> Total: under five dollars a month, replacing a two-hundred-dollar
> stack. The math is not subtle.

---

### 7:30–8:10 — THE CATCH (be honest, this is the trust move)

> Two things I'm not going to pretend.
>
> One: this isn't no-code. If you can't read Python, you'll struggle.
> The free guide has the full scripts and they're short, but you have
> to be willing to look at them.
>
> Two: when an API changes, you fix it. Gmail rotated an OAuth scope on
> me in March and my inbox triage broke for two days. With Zapier, I'd
> have just gotten an email. With my own code, I had to actually go in
> and read the error.
>
> If those two things are dealbreakers, stay on Zapier. It's a fine
> tool. If they're not — keep watching.

---

### 8:10–8:40 — CTA

*Cut to face. Direct.*

> I put the prompts and the full code for all five automations — inbox
> triage, invoice follow-up, meeting notes, lead enrichment, and a
> weekly review — into a free PDF. Link in the description. The repo
> is also linked, MIT licensed, take what you want.
>
> If you want the full system — twelve automations, the prompt library,
> a setup walkthrough, and a private Discord — that's on Gumroad, also
> in the description.
>
> If this saved you time, the only thing I'll ask is that you star the
> repo. Helps other solo operators find it. That's it. See you next
> Wednesday.

*End card: thumbnail of next planned video + free PDF graphic.*

---

## Production checklist

- [ ] Record voice-over in one take per section
- [ ] Screen record each code section separately, then trim
- [ ] Pattern interrupts: face cut every 25–35 seconds
- [ ] Add captions (45% of YouTube viewers watch muted)
- [ ] Verify all three links in description before publishing
- [ ] Pin a comment with the PDF link
- [ ] First 24h: respond to every comment within an hour

## Shorts repurposing

Cut three Shorts from this:
1. **0:00–0:15 hook** + the "$12k recovered" beat from build 2 (~50s)
2. **The architecture decision** segment, condensed to 60s
3. **The cost breakdown** with the real screenshot (~40s)

Each Short ends with: *"Full breakdown on the channel, free guide in bio."*
