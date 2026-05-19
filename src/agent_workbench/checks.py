from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .generator import expand_adapters, workbench_reference
from .scanner import scan_repo


@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class ReadinessReport:
    root: Path
    workbench: Path
    checks: tuple[ReadinessCheck, ...]
    strict: bool = False

    @property
    def ready(self) -> bool:
        if self.strict:
            return all(check.status == "pass" for check in self.checks)
        return all(check.status != "fail" for check in self.checks)

    @property
    def status(self) -> str:
        return "ready" if self.ready else "not_ready"

    @property
    def has_failures(self) -> bool:
        return any(check.status == "fail" for check in self.checks)

    @property
    def next_action(self) -> str:
        if self.ready:
            return "open agent-task-pack.md and hand the kickoff prompt to your coding agent."
        if self.has_failures:
            return "run `agent-workbench init` to generate or refresh the missing workbench files."
        return "resolve the warning checks before using this readiness report as a strict gate."


REQUIRED_DOCUMENTS = {
    "AGENTS.md": (
        "## Repository Map",
        "## Safe Commands",
        "## Guardrails",
    ),
    "agent-task-pack.md": (
        "## Kickoff Prompt",
        "## Verification Commands",
        "## Acceptance Gate",
    ),
}

OPTIONAL_ADAPTERS = {
    "claude": (
        "Claude Code handoff",
        Path("CLAUDE.md"),
    ),
    "codex": (
        "Codex handoff",
        Path(".codex") / "AGENTS.md",
    ),
    "cursor": (
        "Cursor handoff",
        Path(".cursor") / "rules" / "agent-workbench.md",
    ),
    "opencode": (
        "OpenCode handoff",
        Path("opencode.json"),
    ),
}


def check_workbench(
    root: Path,
    workbench: Path | None = None,
    adapters: tuple[str, ...] = (),
    strict: bool = False,
) -> ReadinessReport:
    root = root.resolve()
    workbench_path = _resolve_workbench(root, workbench)
    checks: list[ReadinessCheck] = []

    for filename, required_sections in REQUIRED_DOCUMENTS.items():
        path = workbench_path / filename
        if not path.exists():
            checks.append(ReadinessCheck(filename, "fail", f"Missing {path}"))
            continue
        if not path.is_file():
            checks.append(ReadinessCheck(filename, "fail", f"{path} is not a file"))
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        checks.append(ReadinessCheck(filename, "pass", f"Found {path}"))
        missing_sections = tuple(section for section in required_sections if section not in text)
        if missing_sections:
            checks.append(
                ReadinessCheck(
                    f"{filename} sections",
                    "fail",
                    f"Missing required sections: {', '.join(missing_sections)}",
                )
            )
        else:
            checks.append(ReadinessCheck(f"{filename} sections", "pass", "Required sections are present"))

    checks.extend(_check_optional_adapters(root, workbench_path, adapters))

    repo = scan_repo(root)
    if repo.test_commands:
        checks.append(ReadinessCheck("verification commands", "pass", ", ".join(repo.test_commands)))
    else:
        checks.append(
            ReadinessCheck(
                "verification commands",
                "warn",
                "No test command detected; add one before accepting risky agent edits.",
            )
        )

    if repo.risk_notes:
        checks.extend(ReadinessCheck("risk note", "warn", note) for note in repo.risk_notes)
    else:
        checks.append(ReadinessCheck("risk notes", "pass", "No local risk notes detected"))

    return ReadinessReport(root=root, workbench=workbench_path, checks=tuple(checks), strict=strict)


def _check_optional_adapters(root: Path, workbench: Path, adapters: tuple[str, ...]) -> tuple[ReadinessCheck, ...]:
    checks: list[ReadinessCheck] = []
    required_adapters = set(expand_adapters(adapters))
    workbench_ref = workbench_reference(root, workbench)
    for adapter, (name, relative_path) in OPTIONAL_ADAPTERS.items():
        path = workbench / relative_path
        if not path.exists():
            if adapter in required_adapters:
                checks.append(ReadinessCheck(name, "fail", f"Missing {path}"))
            continue
        if not path.is_file():
            checks.append(ReadinessCheck(name, "fail", f"{path} is not a file"))
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        missing = tuple(item for item in _adapter_required_text(adapter, workbench_ref) if item not in text)
        if missing:
            checks.append(ReadinessCheck(name, "fail", f"Missing references: {', '.join(missing)}"))
        else:
            checks.append(ReadinessCheck(name, "pass", f"Found {path}"))
    return tuple(checks)


def _adapter_required_text(adapter: str, workbench_ref: str) -> tuple[str, ...]:
    if adapter in {"codex", "cursor"}:
        return (f"{workbench_ref}/AGENTS.md", f"{workbench_ref}/agent-task-pack.md")
    return ("AGENTS.md", "agent-task-pack.md")


def readiness_payload(report: ReadinessReport) -> dict[str, object]:
    counts = _check_status_counts(report)
    return {
        "kind": "agent_workbench.readiness",
        "schema_version": 1,
        "status": report.status,
        "ready": report.ready,
        "strict": report.strict,
        "counts": counts,
        "next_action": report.next_action,
        "root": str(report.root),
        "workbench": str(report.workbench),
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "detail": check.detail,
            }
            for check in report.checks
        ],
    }


def render_readiness_text(report: ReadinessReport) -> str:
    lines = [
        f"status={report.status}",
        f"root={report.root}",
        f"workbench={report.workbench}",
    ]
    if report.strict:
        lines.append("strict=true")
    lines.append(f"next_action={report.next_action}")
    lines.append("")
    lines.extend(f"{check.status.upper()} {check.name}: {check.detail}" for check in report.checks)
    lines.extend(["", f"Next: {report.next_action}"])
    return "\n".join(lines)


def _resolve_workbench(root: Path, workbench: Path | None) -> Path:
    if workbench is None:
        return root / ".agent-workbench"
    if workbench.is_absolute():
        return workbench.resolve()
    return (root / workbench).resolve()


def _check_status_counts(report: ReadinessReport) -> dict[str, int]:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for check in report.checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts
