from __future__ import annotations

import subprocess
from pathlib import Path


def git_status(cwd: Path = Path(".")) -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return f"git unavailable: {exc}"

    if result.returncode != 0:
        return result.stderr.strip() or result.stdout.strip() or "git status failed"
    return result.stdout.strip()
