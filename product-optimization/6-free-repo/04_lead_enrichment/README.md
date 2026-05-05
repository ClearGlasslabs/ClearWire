# 04 · Lead enrichment

One-page brief on a person and their company before a sales call.

## Run

```bash
python 04_lead_enrichment/enrich.py --name "Jane Doe" --company "Acme Inc" \
  --out briefs/jane.md
```

## Configure

Set `BRAVE_SEARCH_API_KEY` in `.env` for live web search. Without it
the script runs on Claude's prior knowledge alone (worse output, but
still useful for well-known companies).

Swap Brave for Tavily, SerpAPI, or your own scraper by editing
`search()`.

## The "don't guess" instruction

Without it, Claude invents plausible-sounding details. With it, you
get a brief you can trust to walk into a call with.
