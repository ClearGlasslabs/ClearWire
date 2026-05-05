"""Lead enrichment: one-page brief before any sales call.

Run:
    python 04_lead_enrichment/enrich.py --name "Jane Doe" --company "Acme Inc"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.claude_client import call

PROMPT_PATH = Path(__file__).parent / "prompt.md"
BRAVE_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")


def search(query: str, count: int = 8) -> str:
    """Brave Search wrapper. Falls back to a stub if no key is set."""
    if not BRAVE_KEY:
        return f"(no BRAVE_SEARCH_API_KEY set; running on prior knowledge for: {query})"
    r = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": BRAVE_KEY, "Accept": "application/json"},
        params={"q": query, "count": count},
        timeout=15,
    )
    r.raise_for_status()
    results = r.json().get("web", {}).get("results", [])
    return "\n\n".join(
        f"{x.get('title', '')}\n{x.get('url', '')}\n{x.get('description', '')}"
        for x in results
    )


def brief(name: str, company: str) -> str:
    public_info = "\n\n".join([
        f"=== Company: {company} ===\n{search(f'{company} company')}",
        f"=== Recent: {company} ===\n{search(f'{company} 2026 news announcement')}",
        f"=== Person: {name} ===\n{search(f'{name} {company}')}",
    ])
    prompt = PROMPT_PATH.read_text().format(
        name=name, company=company, public_info=public_info
    )
    return call(prompt, max_tokens=1500).text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--company", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    output = brief(args.name, args.company)
    print(output)

    if args.out:
        args.out.write_text(output + "\n")
        print(f"\n✓ Saved to {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
