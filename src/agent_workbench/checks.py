from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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

    @property
    def ready(self) -> bool:
        return all(check.status != "fail" for check in self.checks)

    @property
    def status(self) -> str:
        return "ready" if self.ready else "not_ready"


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


def check_workbench(root: Path, workbench: Path | None = None) -> ReadinessReport:
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

    return ReadinessReport(root=root, workbench=workbench_path, checks=tuple(checks))


def readiness_payload(report: ReadinessReport) -> dict[str, object]:
    return {
        "status": report.status,
        "ready": report.ready,
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
        "",
    ]
    lines.extend(f"{check.status.upper()} {check.name}: {check.detail}" for check in report.checks)
    if report.ready:
        lines.extend(["", "Next: open agent-task-pack.md and hand the kickoff prompt to your coding agent."])
    else:
        lines.extend(["", "Next: run `agent-workbench init` to generate or refresh the missing workbench files."])
    return "\n".join(lines)


def _resolve_workbench(root: Path, workbench: Path | None) -> Path:
    if workbench is None:
        return root / ".agent-workbench"
    if workbench.is_absolute():
        return workbench.resolve()
    return (root / workbench).resolve()
