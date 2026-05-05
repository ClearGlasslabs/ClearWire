"""Inbox triage: score each unread email and draft replies for high-revenue ones.

Run:
    python 01_inbox_triage/triage.py --dry-run --input examples/sample_inbox.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.claude_client import call_json

PROMPT_PATH = Path(__file__).parent / "prompt.md"
VOICE_PATH = Path(__file__).parent / "voice_samples.txt"
THRESHOLD = int(os.getenv("TRIAGE_REVENUE_THRESHOLD", "7"))


@dataclass
class Email:
    id: str
    sender: str
    subject: str
    body: str


def load_emails(path: Path) -> list[Email]:
    data = json.loads(path.read_text())
    return [Email(**e) for e in data]


def load_voice_samples() -> str:
    if not VOICE_PATH.exists():
        return "(no voice samples provided)"
    return VOICE_PATH.read_text().strip()


def triage(email: Email, voice_samples: str) -> dict:
    prompt = PROMPT_PATH.read_text().format(
        voice_samples=voice_samples,
        sender=email.sender,
        subject=email.subject,
        body=email.body,
    )
    return call_json(prompt, max_tokens=1500)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    emails = load_emails(args.input)
    voice = load_voice_samples()

    print(f"Triaging {len(emails)} email(s). Threshold: revenue >= {THRESHOLD}")
    print("-" * 60)

    for email in emails:
        result = triage(email, voice)
        print(f"\n[{email.id}] {email.sender} :: {email.subject}")
        print(
            f"  urgency={result['urgency']}  revenue={result['revenue']}  "
            f"replyability={result['replyability']}"
        )
        if result["revenue"] >= THRESHOLD:
            draft = result.get("draft", "").strip()
            if args.dry_run:
                print("  DRAFT (dry-run, not saved):")
                for line in draft.splitlines():
                    print(f"    {line}")
            else:
                save_draft(email, draft)
                print(f"  ✓ Draft saved to drafts/{email.id}.txt")
        else:
            print("  (skipped: below threshold)")

    return 0


def save_draft(email: Email, draft: str) -> None:
    out = Path(__file__).parent / "drafts"
    out.mkdir(exist_ok=True)
    (out / f"{email.id}.txt").write_text(
        f"To: {email.sender}\nSubject: Re: {email.subject}\n\n{draft}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
