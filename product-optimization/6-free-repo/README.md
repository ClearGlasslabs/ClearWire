# claude-automations-starter

Five Claude API automations I run every day. Standalone Python scripts,
MIT-licensed, runs on your machine with your API key.

If you're a solo founder, consultant, or indie dev drowning in admin
work, start here. Pick the one script that solves your single biggest
time leak. Run it for a week. Then come back for the next.

## What's in here

| # | Automation | What it does |
|---|---|---|
| 01 | Inbox triage | Scores incoming email, drafts replies for high-revenue threads |
| 02 | Invoice follow-up | Tiered nudges by days overdue (7 / 14 / 30) |
| 03 | Meeting notes | Decisions and action items from a transcript, not a summary |
| 04 | Lead enrichment | One-page brief before any sales call |
| 05 | Weekly review | Chief-of-staff weekly synthesis from your calendar + email + commits |

## Quickstart

```bash
git clone https://github.com/<your-handle>/claude-automations-starter
cd claude-automations-starter
cp .env.example .env          # add your ANTHROPIC_API_KEY
pip install -r requirements.txt
python 01_inbox_triage/triage.py --dry-run --input examples/sample_inbox.json
```

`--dry-run` prints what would happen without sending anything. Always
run it first.

## What you'll need

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com)
- About 30 minutes for first setup
- Roughly $1–5/month in API costs at solo-operator volume

## License

MIT for the code. Prompts and docs CC0. Use them however you want.

## Want the full system?

This repo has 5 standalone scripts. The paid ClearGlass AI Automation
Assistant has 12 integrated workflows + 40+ tested prompts + a 22-min
setup walkthrough + a private Discord + lifetime updates.

→ <https://clearglassinc.gumroad.com/l/ai>

If 5 scripts is enough for you, that's genuinely fine. They do most of
the work.

## Contributing / questions

Open an issue. PRs welcome — especially new prompt variants for the
existing workflows.

If this saved you time, star the repo. Helps other solo operators find it.
