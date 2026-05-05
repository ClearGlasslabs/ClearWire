# 03 · Meeting notes

Turns a transcript into decisions, action items, and open questions —
not a summary.

## Run

```bash
python 03_meeting_notes/notes.py --transcript meeting.txt --out notes.md
```

Pipes any plain-text transcript (Otter, Granola, Zoom, Fathom). Output
is markdown you can paste into Notion or send to the client.

## The trick

The prompt forces `AMBIGUOUS — needs clarification` whenever the
transcript is unclear. Default LLM summarizers smooth over confusion
and you discover the miscommunication two weeks later. This surfaces
it immediately.
