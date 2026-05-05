"""Thin wrapper around the Anthropic SDK with JSON parsing helpers."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


@dataclass
class ClaudeResponse:
    text: str
    usage: dict[str, int]


_client = Anthropic()


def call(
    prompt: str,
    *,
    model: str = _DEFAULT_MODEL,
    max_tokens: int = 1024,
    system: str | None = None,
) -> ClaudeResponse:
    msg = _client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system or "",
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in msg.content if block.type == "text")
    return ClaudeResponse(
        text=text,
        usage={
            "input_tokens": msg.usage.input_tokens,
            "output_tokens": msg.usage.output_tokens,
        },
    )


def call_json(prompt: str, **kwargs: Any) -> dict[str, Any]:
    """Call Claude and parse the first JSON object found in the response."""
    response = call(prompt, **kwargs)
    return _extract_json(response.text)


_JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL)
_BARE_JSON = re.compile(r"(\{.*\}|\[.*\])", re.DOTALL)


def _extract_json(text: str) -> dict[str, Any]:
    match = _JSON_BLOCK.search(text) or _BARE_JSON.search(text)
    if not match:
        raise ValueError(f"No JSON found in model response:\n{text}")
    return json.loads(match.group(1))
