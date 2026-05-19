from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path

from .models import AgentAsset, FileSignal, RepoMap


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".agent-workbench",
    ".agents",
    ".codex",
    ".omx",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".uv-cache",
    ".uv-python",
    "dist",
    "build",
}

KIND_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".md": "docs",
    ".yml": "config",
    ".yaml": "config",
    ".toml": "config",
    ".json": "config",
    ".ps1": "script",
    ".sh": "script",
}

AGENT_ASSET_PATTERNS = (
    ("AGENTS.md", "Agent instructions"),
    ("CLAUDE.md", "Claude Code instructions"),
    ("GEMINI.md", "Gemini instructions"),
    ("opencode.json", "OpenCode config"),
    (".codex/AGENTS.md", "Codex instructions"),
    (".cursor/rules/*.md", "Cursor rule"),
    (".github/copilot-instructions.md", "GitHub Copilot instructions"),
    (".github/instructions/*.instructions.md", "GitHub Copilot instructions"),
    (".github/prompts/*.prompt.md", "GitHub Copilot prompt"),
)


def scan_repo(root: Path, *, max_files: int = 300) -> RepoMap:
    root = root.resolve()
    ignore_rules = _load_gitignore(root)
    files: list[FileSignal] = []
    for path in sorted(root.rglob("*")):
        if len(files) >= max_files:
            break
        if path.is_dir() or _is_ignored(path, root, ignore_rules):
            continue
        if path.stat().st_size > 512_000:
            continue
        files.append(_file_signal(path, root))

    return RepoMap(
        root=root,
        files=tuple(files),
        package_managers=_package_managers(root),
        test_commands=_test_commands(root),
        risk_notes=_risk_notes(root),
        agent_assets=_agent_assets(root),
    )


@dataclass(frozen=True)
class _IgnoreRule:
    pattern: str
    negated: bool
    directory: bool
    anchored: bool


def _load_gitignore(root: Path) -> tuple[_IgnoreRule, ...]:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return ()

    rules: list[_IgnoreRule] = []
    for raw_line in gitignore.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        negated = line.startswith("!")
        if negated:
            line = line[1:]
        anchored = line.startswith("/")
        line = line.lstrip("/")
        directory = line.endswith("/")
        line = line.rstrip("/")
        if line:
            rules.append(_IgnoreRule(pattern=line, negated=negated, directory=directory, anchored=anchored))
    return tuple(rules)


def _is_ignored(path: Path, root: Path, ignore_rules: tuple[_IgnoreRule, ...] = ()) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    if any(part in IGNORE_DIRS for part in relative.parts):
        return True

    ignored = False
    for rule in ignore_rules:
        if _matches_ignore_rule(relative, rule):
            ignored = not rule.negated
    return ignored


def _matches_ignore_rule(relative: Path, rule: _IgnoreRule) -> bool:
    rel = relative.as_posix()
    parts = relative.parts
    if rule.directory:
        parent_paths = [Path(*parts[:index]).as_posix() for index in range(1, len(parts))]
        if not parent_paths:
            return False
        return any(_matches_pattern(parent, rule) for parent in parent_paths)
    return _matches_pattern(rel, rule) or ("/" not in rule.pattern and fnmatch.fnmatchcase(relative.name, rule.pattern))


def _matches_pattern(value: str, rule: _IgnoreRule) -> bool:
    if rule.anchored:
        return fnmatch.fnmatchcase(value, rule.pattern)
    if fnmatch.fnmatchcase(value, rule.pattern):
        return True
    if "/" not in rule.pattern:
        return any(fnmatch.fnmatchcase(part, rule.pattern) for part in value.split("/"))
    return fnmatch.fnmatchcase(value, f"*/{rule.pattern}")


def _file_signal(path: Path, root: Path) -> FileSignal:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.count("\n") + (1 if text else 0)
    except OSError:
        lines = 0
    relative = path.relative_to(root).as_posix()
    return FileSignal(path=relative, kind=KIND_BY_SUFFIX.get(path.suffix.lower(), "other"), lines=lines, bytes=path.stat().st_size)


def _package_managers(root: Path) -> tuple[str, ...]:
    managers = []
    markers = {
        "pyproject.toml": "python/pyproject",
        "package.json": "node/npm",
        "pnpm-lock.yaml": "node/pnpm",
        "yarn.lock": "node/yarn",
        "Cargo.toml": "rust/cargo",
        "go.mod": "go/modules",
    }
    for marker, label in markers.items():
        if (root / marker).exists():
            managers.append(label)
    return tuple(managers)


def _test_commands(root: Path) -> tuple[str, ...]:
    commands = []
    if (root / "pyproject.toml").exists():
        commands.append("python -m unittest discover -s tests")
    if (root / "package.json").exists():
        commands.append("npm test")
    if (root / "Cargo.toml").exists():
        commands.append("cargo test")
    if (root / "go.mod").exists():
        commands.append("go test ./...")
    return tuple(commands)


def _risk_notes(root: Path) -> tuple[str, ...]:
    notes = []
    for candidate in (".env", ".env.local", ".env.bak"):
        if (root / candidate).exists():
            notes.append(f"{candidate} exists; keep it ignored and never paste secrets into issues.")
    if not (root / ".gitignore").exists():
        notes.append("No .gitignore found; create one before agent-driven edits.")
    return tuple(notes)


def _agent_assets(root: Path) -> tuple[AgentAsset, ...]:
    assets: list[AgentAsset] = []
    for pattern, label in AGENT_ASSET_PATTERNS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                assets.append(AgentAsset(path=path.relative_to(root).as_posix(), label=label))
    return tuple(dict.fromkeys(assets))
