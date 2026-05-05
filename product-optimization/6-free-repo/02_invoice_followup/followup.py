"""Invoice follow-up: tier messages by days overdue, draft in your voice.

Reads invoices from a CSV (id, client, amount, due_date, last_message).
Run:
    python 02_invoice_followup/followup.py --dry-run --csv invoices.example.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.claude_client import call

PROMPT_PATH = Path(__file__).parent / "prompt.md"

TIERS = {
    7: "warm nudge — assume it slipped someone's mind",
    14: "direct — ask for a confirmed payment date",
    30: "firm — mention pausing work or adding a late fee",
}


@dataclass
class Invoice:
    id: str
    client: str
    amount: str
    due_date: date
    last_message: str

    @property
    def days_overdue(self) -> int:
        return (date.today() - self.due_date).days


def load_invoices(path: Path) -> list[Invoice]:
    rows = list(csv.DictReader(path.open()))
    out = []
    for r in rows:
        out.append(
            Invoice(
                id=r["id"],
                client=r["client"],
                amount=r["amount"],
                due_date=datetime.strptime(r["due_date"], "%Y-%m-%d").date(),
                last_message=r.get("last_message", ""),
            )
        )
    return out


def pick_tier(days: int) -> tuple[int, str] | None:
    eligible = [t for t in TIERS if days >= t]
    if not eligible:
        return None
    t = max(eligible)
    return t, TIERS[t]


def draft(invoice: Invoice, tier_label: str) -> str:
    prompt = PROMPT_PATH.read_text().format(
        client=invoice.client,
        amount=invoice.amount,
        days=invoice.days_overdue,
        invoice_id=invoice.id,
        tier=tier_label,
        last_message=invoice.last_message or "(no prior message on file)",
    )
    return call(prompt, max_tokens=400).text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    invoices = load_invoices(args.csv)
    print(f"Reviewing {len(invoices)} invoice(s)")
    print("-" * 60)

    for inv in invoices:
        tier = pick_tier(inv.days_overdue)
        if not tier:
            print(f"\n[{inv.id}] {inv.client} :: {inv.days_overdue}d — no action")
            continue

        days_threshold, label = tier
        message = draft(inv, label)
        print(f"\n[{inv.id}] {inv.client} :: {inv.days_overdue}d overdue — tier {days_threshold}")
        for line in message.splitlines():
            print(f"  {line}")

        if not args.dry_run:
            out = Path(__file__).parent / "drafts"
            out.mkdir(exist_ok=True)
            (out / f"{inv.id}.txt").write_text(message + "\n")
            print(f"  ✓ Saved to drafts/{inv.id}.txt")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
