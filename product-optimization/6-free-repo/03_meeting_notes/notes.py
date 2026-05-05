"""Meeting notes: extract decisions and action items from a transcript.

Run:
    python 03_meeting_notes/notes.py --transcript path/to/transcript.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.claude_client import call

PROMPT_PATH = Path(__file__).parent / "prompt.md"


def summarize(transcript: str) -> str:
    prompt = PROMPT_PATH.read_text().format(transcript=transcript)
    return call(prompt, max_tokens=2048).text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    transcript = args.transcript.read_text()
    summary = summarize(transcript)

    print(summary)

    if args.out:
        args.out.write_text(summary + "\n")
        print(f"\n✓ Saved to {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
