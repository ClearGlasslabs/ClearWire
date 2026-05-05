"""Outreach drafter — get the first 10 testimonials in 7 days.

Reads a CSV of leads. For each one, generates a short, specific DM
offering a free copy of the AI Automation Assistant in exchange for an
honest review.

Run:
    python outreach.py --leads leads.example.csv --dry-run
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Re-uses the free repo's claude_client. Drop this file next to it or
# `pip install` your own minimal wrapper.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "6-free-repo"))

from shared.claude_client import call

PROMPT_PATH = Path(__file__).parent / "prompt.md"
PRODUCT_URL = os.getenv(
    "PRODUCT_URL", "https://clearglassinc.gumroad.com/l/ai"
)
SENDER_NAME = os.getenv("SENDER_NAME", "[Your name]")


@dataclass
class Lead:
    name: str
    handle: str
    platform: str        # x | linkedin | email | reddit
    why_them: str        # 1-line: why this person specifically
    public_signal: str   # something they posted/built/said publicly
    contact: str         # @handle, URL, or email


def load_leads(path: Path) -> list[Lead]:
    return [Lead(**row) for row in csv.DictReader(path.open())]


def draft(lead: Lead) -> str:
    prompt = PROMPT_PATH.read_text().format(
        sender_name=SENDER_NAME,
        product_url=PRODUCT_URL,
        name=lead.name,
        platform=lead.platform,
        why_them=lead.why_them,
        public_signal=lead.public_signal,
    )
    return call(prompt, max_tokens=500).text.strip()


def channel_limits(platform: str) -> str:
    return {
        "x": "DM, max 280 chars (use a thread of 2 if needed)",
        "linkedin": "InMail, ≤800 chars, no links in the first message",
        "email": "Email, 3-4 short paragraphs, ≤120 words total",
        "reddit": "DM, conversational, no marketing language",
    }.get(platform, "Short and specific")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--leads", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max", type=int, default=10,
                        help="Daily cap to avoid spam-flagging")
    args = parser.parse_args()

    leads = load_leads(args.leads)[: args.max]
    print(f"Drafting outreach for {len(leads)} lead(s) (cap: {args.max})")
    print("=" * 70)

    out_dir = Path(__file__).parent / "drafts"
    out_dir.mkdir(exist_ok=True)

    for lead in leads:
        message = draft(lead)
        print(f"\n→ {lead.name} ({lead.platform}) — {lead.contact}")
        print(f"  Limits: {channel_limits(lead.platform)}")
        print("-" * 60)
        for line in message.splitlines():
            print(f"  {line}")

        if not args.dry_run:
            slug = lead.handle.replace("/", "_")
            (out_dir / f"{lead.platform}_{slug}.txt").write_text(
                f"To: {lead.contact}\nPlatform: {lead.platform}\n\n{message}\n"
            )

    print("\n" + "=" * 70)
    print("Reminder: send each one MANUALLY. Personalize the first line if")
    print("anything looks off. Track replies in a spreadsheet, not a CRM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
