from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


SECRET_SCAN_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".uv-cache",
    ".uv-python",
    ".venv",
    "__pycache__",
    "htmlcov",
    "venv",
}

SECRET_SCAN_EXCLUDED_FILES = {
    ".env",
    ".env.local",
    ".env.bak",
}

SECRET_PATTERNS = (
    re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)

SENSITIVE_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(?:password|secret|api[_-]?key|token)\b\s*[:=]\s*(['\"])(?P<value>[^'\"]{12,})\1"
)


def run_local_checks(root: Path = Path(".")) -> tuple[CheckResult, ...]:
    checks = [
        _check_path(root / "src" / "github_trend_lab" / "cli.py", "CLI module exists"),
        _check_path(root / ".github" / "workflows" / "ci.yml", "CI workflow exists"),
        _check_path(root / ".github" / "workflows" / "daily-trend.yml", "Daily workflow exists"),
        _check_path(root / "scripts" / "publish.ps1", "Publish script exists"),
        _check_path(root / "reports" / "daily-brief.md", "Daily brief exists"),
        _check_git_ignored(root, ".env.local"),
        _check_git_ignored(root, ".env.bak"),
        run_secret_scan(root),
    ]
    return tuple(checks)


def render_check_report(checks: tuple[CheckResult, ...]) -> str:
    lines = ["# Local Verification", ""]
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        lines.append(f"- {status}: {check.name} - {check.detail}")
    return "\n".join(lines) + "\n"


def has_failures(checks: tuple[CheckResult, ...]) -> bool:
    return any(not check.ok for check in checks)


def _check_path(path: Path, name: str) -> CheckResult:
    return CheckResult(name=name, ok=path.exists(), detail=str(path))


def _check_git_ignored(root: Path, relative: str) -> CheckResult:
    path = root / relative
    if not path.exists():
        return CheckResult(name=f"{relative} ignored", ok=True, detail="file does not exist")
    result = subprocess.run(
        ["git", "check-ignore", "-q", relative],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return CheckResult(
        name=f"{relative} ignored",
        ok=result.returncode == 0,
        detail="ignored by git" if result.returncode == 0 else "not ignored by git",
    )


def run_secret_scan(root: Path = Path(".")) -> CheckResult:
    findings: list[str] = []
    for path in _iter_scannable_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _line_has_secret(line):
                findings.append(f"{path.relative_to(root)}:{line_number}")

    if findings:
        sample = ", ".join(findings[:8])
        extra = "" if len(findings) <= 8 else f", +{len(findings) - 8} more"
        return CheckResult(
            name="Secret scan",
            ok=False,
            detail=f"Potential secret material found at {sample}{extra}. Values are intentionally omitted.",
        )

    return CheckResult(
        name="Secret scan",
        ok=True,
        detail="No high-confidence secrets found outside ignored local env files.",
    )


def _iter_scannable_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in SECRET_SCAN_EXCLUDED_DIRS for part in relative_parts):
            continue
        if path.name in SECRET_SCAN_EXCLUDED_FILES:
            continue
        yield path


def _line_has_secret(line: str) -> bool:
    if any(pattern.search(line) for pattern in SECRET_PATTERNS):
        return True
    assignment = SENSITIVE_ASSIGNMENT_PATTERN.search(line)
    if not assignment:
        return False
    return _looks_like_hardcoded_secret(assignment.group("value"))


def _looks_like_hardcoded_secret(value: str) -> bool:
    normalized = value.strip()
    lowered = normalized.lower()
    if lowered.startswith(("<", "your-", "example", "placeholder", "xxxx", "token", "$")):
        return False
    if lowered in {"none", "null", "changeme", "change-me", "dummy-value"}:
        return False
    if any(char.isspace() for char in normalized):
        return False
    classes = sum(
        (
            any(char.islower() for char in normalized),
            any(char.isupper() for char in normalized),
            any(char.isdigit() for char in normalized),
            any(not char.isalnum() for char in normalized),
        )
    )
    return len(normalized) >= 16 and classes >= 2
