# Companion Repo Structure

Repo name: `claude-automations-starter`
License: MIT (free version) — encourages forks and stars, drives traffic.

## Directory layout

```
claude-automations-starter/
├── README.md
├── LICENSE
├── .env.example
├── requirements.txt
├── pyproject.toml
├── 01_inbox_triage/
│   ├── README.md
│   ├── triage.py
│   ├── prompts/
│   │   └── triage_prompt.md
│   └── voice_samples.example.txt
├── 02_invoice_followup/
│   ├── README.md
│   ├── followup.py
│   └── prompts/
│       ├── tier_1_warm.md
│       ├── tier_2_direct.md
│       └── tier_3_firm.md
├── 03_meeting_notes/
│   ├── README.md
│   ├── notes.py
│   └── prompts/
│       └── extraction_prompt.md
├── 04_lead_enrichment/
│   ├── README.md
│   ├── enrich.py
│   └── prompts/
│       └── brief_prompt.md
├── 05_weekly_review/
│   ├── README.md
│   ├── review.py
│   └── prompts/
│       └── chief_of_staff.md
└── shared/
    ├── claude_client.py
    └── config.py
```

## Top-level README must include

1. **One-line pitch** at top
2. **30-second demo GIF** (record a terminal run of `01_inbox_triage`)
3. **Quickstart** in 4 commands
4. **What's in here** (table of the 5 automations)
5. **Upgrade path** — clear link to the paid AI Automation Assistant on Gumroad
6. **Star CTA** at the end ("If this saved you time, star the repo so other
   solo operators find it")

## Quickstart block (paste into README)

````markdown
## Quickstart

```bash
git clone https://github.com/[your-handle]/claude-automations-starter
cd claude-automations-starter
cp .env.example .env  # add your ANTHROPIC_API_KEY
pip install -r requirements.txt
python 01_inbox_triage/triage.py --dry-run
```

`--dry-run` prints what would happen without sending anything. Run it first.
````

## What goes in the paid version (NOT in this repo)

This is the split that makes the funnel work — keep it clear:

| Free repo (this) | Paid product ($280) |
|---|---|
| 5 core automations | 12 automations |
| Basic prompts | 40+ tested prompts in a library |
| Single config style | Per-workflow config + secrets management |
| Self-serve docs | 22-min video walkthrough |
| GitHub issues for support | Private buyer Discord |
| You patch it yourself | Lifetime updates |
| Standalone scripts | Orchestration layer + scheduler |

If someone is happy with 5 scripts, they shouldn't feel cheated. If they want
the production system, the upgrade is obvious.

## Distribution

On publish:
1. Push to GitHub
2. Show HN: "5 Claude API automations I run every day (Python)"
3. Post on r/ClaudeAI, r/Python, r/SideProject
4. X/Threads launch: 5-post thread, one automation per post, screenshot of
   real terminal output for each
5. LinkedIn long-form post: "Why I deleted my Zapier subscription"

The repo is the artifact. Every video, post, and email links here.
