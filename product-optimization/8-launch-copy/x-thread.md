# X / Twitter launch thread

**When to post:** Tuesday or Wednesday, 9am ET.
**Pin:** to your profile for 7 days.
**Reply with:** the GitHub link in post 8 (don't put it in post 1 — kills reach).

---

**1/**

I was paying $200/month for a Zapier stack that broke every other week.

Replaced the whole thing with 80 lines of Python and the Claude API.

5 scripts that run my entire one-person business now. Open-sourced all of them today.

🧵

---

**2/**

The 5 automations:

→ Inbox triage (scores email, drafts replies for high-revenue ones)
→ Invoice follow-up (tiered nudges by days overdue)
→ Meeting notes (decisions + actions, not transcripts)
→ Lead enrichment (1-page brief before any sales call)
→ Weekly review (chief-of-staff style, written for you)

Each one is <150 lines.

---

**3/**

The piece that made inbox triage actually usable wasn't the model.

It was passing 3 of my own recent sent emails as voice samples.

Without that: replies sound like a chatbot.

With it: they sound like me on a good day.

Difference between "I'll review the drafts" and "I'll just hit send."

---

**4/**

Invoice follow-up was the painful one to build because the awkwardness is real.

Tiered the messages by days overdue:
- 7d: warm nudge
- 14d: direct
- 30d: firm

Fed Claude the last 3 messages with the client. That context is what makes it sound like the actual relationship, not a dunning bot.

Recovered ~$12k in 90 days.

---

**5/**

Meeting notes prompt has one rule that fixes the whole thing:

> "If something is ambiguous, mark it AMBIGUOUS — needs clarification rather than guessing."

Default summarizers smooth over confusion. You discover the miscommunication 2 weeks later.

This surfaces it immediately. Game changer.

---

**6/**

Lead enrichment runs before every sales call. Brave Search → Claude → 1-page brief.

Hardest instruction to land in the prompt: "If you don't know something, write 'unknown'. Do not guess."

Without it Claude invents plausible details.
With it you get a brief you can walk into a call with.

---

**7/**

Weekly review is the one that changed how I run the business.

Prompt is calibrated for honesty:

> "If I spent the week on busywork, say so. I'd rather hear it from you than figure it out in 3 months."

Default LLM tone is encouraging-coach. You want a chief of staff.

---

**8/**

All 5 scripts, the prompts, voice samples, and example data — open-sourced under MIT.

Setup: clone, drop in your Anthropic API key, run with `--dry-run`.

→ github.com/[your-handle]/claude-automations-starter

If it saves you time, a star helps other solo operators find it.

---

**9/**

The full system I run — 12 workflows, 40+ prompts, orchestration layer, walkthrough video — is on Gumroad if you want it.

But honestly, the 5 in the repo do most of the work. Start there.

Will post the 6th, 7th, 8th automation next week. Let me know which one would help most.

---

## Quote-tweet bait (post separately, day 2)

> "Automate the thinking, not the deciding."
>
> The thing that separates AI tools you keep from AI tools you delete.
>
> Drafts > sends. Suggestions > actions. You stay in the loop.

---

## Reply-guy openers (have these ready for the comments)

If someone asks "what model?" → "Claude Sonnet 4.6, mostly. Haiku 4.5 for the cheap classification jobs."

If someone says "why not Zapier?" → "Use what works. For me it was the cost + the breakage. If your Zapier stack is stable and cheap, keep it."

If someone says "this is just a wrapper" → "Yes. The wrapper is the product. The prompt + the threshold + the voice samples are 90% of the value."

If someone DMs asking for free version → reply with the GitHub link, no caveats.
