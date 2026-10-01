"""Privacy-preserving JSONL run logging."""

from __future__ import annotations

import json
from pathlib import Path

from accountlens.schemas import UsageSummary


def append_usage_log(path: Path, summary: UsageSummary) -> None:
    """Append metadata only; never write account content or API keys."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(summary.model_dump(mode="json"), sort_keys=True) + "\n")

