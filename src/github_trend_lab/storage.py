from __future__ import annotations

import json
import re
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from .models import StarSample, TrendSnapshot, utc_now_iso


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return cleaned or "untitled"


def default_snapshot_path(prefix: str = "trend") -> Path:
    stamp = utc_now_iso().replace(":", "").replace("-", "")
    return Path("data/snapshots") / f"{prefix}-{stamp}.json"


def daily_snapshot_path(day: str) -> Path:
    return Path("data/snapshots") / f"daily-{slugify(day)}.json"


def star_history_path(full_name: str) -> Path:
    return Path("data/star_history") / f"{slugify(full_name.replace('/', '__'))}.jsonl"


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, tuple):
        return list(value)
    return value


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, default=to_jsonable, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_snapshot(snapshot: TrendSnapshot, path: Path | None = None) -> Path:
    output = path or default_snapshot_path()
    return write_json(output, snapshot.to_dict())


def read_snapshot(path: Path) -> TrendSnapshot:
    return TrendSnapshot.from_dict(read_json(path))


def append_jsonl(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, default=to_jsonable, ensure_ascii=False) + "\n")
    return path


def read_star_history(path: Path) -> list[StarSample]:
    if not path.exists():
        return []
    samples: list[StarSample] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            samples.append(StarSample(**json.loads(line)))
    return samples


def write_lines(path: Path, lines: Iterable[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path
