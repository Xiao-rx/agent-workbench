from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    github_token: str | None
    target_repo: str | None
    api_version: str = "2026-03-10"


def load_dotenv(path: Path = Path(".env.local")) -> None:
    """Load a tiny subset of dotenv syntax without adding a dependency."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_config(dotenv_path: Path = Path(".env.local")) -> AppConfig:
    load_dotenv(dotenv_path)
    return AppConfig(
        github_token=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"),
        target_repo=os.environ.get("TARGET_REPO"),
        api_version=os.environ.get("GITHUB_API_VERSION", "2026-03-10"),
    )


def default_since() -> str:
    today = date.today()
    return date(today.year, 1, 1).isoformat()
