"""Weekly review: synthesize the week from your data.

Reads a JSON blob with whatever week-summary data you can pull from
your stack (calendar, sent email, commits, revenue). Outputs an honest
chief-of-staff style review.

Run:
    python 05_weekly_review/review.py --week examples/week.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.claude_client import call

PROMPT_PATH = Path(__file__).parent / "prompt.md"


def review(week_data: dict) -> str:
    prompt = PROMPT_PATH.read_text().format(
        data=json.dumps(week_data, indent=2)
    )
    return call(prompt, max_tokens=2048).text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    week_data = json.loads(args.week.read_text())
    output = review(week_data)
    print(output)

    if args.out:
        args.out.write_text(output + "\n")
        print(f"\n✓ Saved to {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
