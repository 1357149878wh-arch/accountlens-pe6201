"""Small JSON/JSONL helpers and dataset loading."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def load_dataset(data_dir: Path) -> dict[str, Any]:
    return {
        "accounts": read_jsonl(data_dir / "accounts.jsonl"),
        "contacts": read_jsonl(data_dir / "contacts.jsonl"),
        "interactions": read_jsonl(data_dir / "interactions.jsonl"),
        "role_truth": read_jsonl(data_dir / "role_ground_truth.jsonl"),
        "critical_truth": read_jsonl(data_dir / "critical_event_ground_truth.jsonl"),
        "splits": read_json(data_dir / "splits.json"),
    }

