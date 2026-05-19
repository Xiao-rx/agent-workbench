from __future__ import annotations

from collections import Counter
from pathlib import Path

from .models import RepoMap

CONCRETE_ADAPTERS = ("claude", "codex", "cursor", "opencode")
SUPPORTED_ADAPTERS = (*CONCRETE_ADAPTERS, "all")
ADAPTER_HANDOFFS = {
    "claude": ("Claude Code", "CLAUDE.md"),
    "codex": ("Codex", ".codex/AGENTS.md"),
    "cursor": ("Cursor", ".cursor/rules/agent-workbench.md"),
    "opencode": ("OpenCode", "opencode.json"),
}


def render_agents_md(repo: RepoMap, project_name: str | None = None, adapters: tuple[str, ...] = ()) -> str:
    name = project_name or repo.root.name
    kinds = Counter(file.kind for file in repo.files)
    lines = [
        f"# AGENTS.md for {name}",
        "",
        "## Mission",
        "",
        "Help AI coding agents make small, verifiable changes in this repository without losing context or leaking secrets.",
        "",
        "## Repository Map",
        "",
        f"- Files scanned: {repo.total_files}",
        f"- Lines scanned: {repo.total_lines}",
        f"- Main file kinds: {_counter_text(kinds)}",
        f"- Package managers: {', '.join(repo.package_managers) if repo.package_managers else 'not detected'}",
        "",
    ]
    handoffs = _adapter_handoff_lines(adapters)
    if handoffs:
        lines.extend(["## Agent Tool Handoffs", "", *handoffs, ""])

    if repo.agent_assets:
        lines.extend(["## Existing Agent Assets", "", *_agent_asset_lines(repo), ""])

    lines.extend(["## Safe Commands", ""])
    if repo.test_commands:
        lines.extend(f"- `{command}`" for command in repo.test_commands)
    else:
        lines.append("- Add a test command before accepting risky automated edits.")

    lines.extend(["", "## High-Signal Files", ""])
    for file in sorted(repo.files, key=lambda item: item.lines, reverse=True)[:12]:
        lines.append(f"- `{file.path}` ({file.kind}, {file.lines} lines)")

    lines.extend(["", "## Guardrails", ""])
    guardrails = repo.risk_notes or ("Keep changes small and run the listed verification commands before committing.",)
    lines.extend(f"- {note}" for note in guardrails)
    lines.append("")
    return "\n".join(lines)


def render_task_pack(repo: RepoMap, project_name: str | None = None, adapters: tuple[str, ...] = ()) -> str:
    name = project_name or repo.root.name
    safe_commands = repo.test_commands or ("Add and document a safe verification command before making risky edits.",)
    high_signal_files = _task_pack_files(repo)
    first_file = high_signal_files[0].path if high_signal_files else "README.md"
    guardrails = repo.risk_notes or ("Keep changes small and run verification before committing.",)
    handoffs = _adapter_handoff_lines(adapters)
    return "\n".join(
        [
            f"# Agent Task Pack: {name}",
            "",
            "## Kickoff Prompt",
            "",
            "```text",
            f"You are working in {name}. Read AGENTS.md first, inspect `{first_file}`, make one small improvement, and verify it before summarizing the change.",
            "```",
            "",
            *(["## Agent Tool Handoffs", "", *handoffs, ""] if handoffs else []),
            *(["## Existing Agent Assets", "", *_agent_asset_lines(repo), ""] if repo.agent_assets else []),
            "## Verification Commands",
            "",
            *[f"- `{command}`" for command in safe_commands],
            "",
            "## High-Signal Files",
            "",
            *[
                f"- `{file.path}` ({file.kind}, {file.lines} lines)"
                for file in high_signal_files
            ],
            *(["- Add a README or primary source file before assigning agent work."] if not high_signal_files else []),
            "",
            "## First Jobs",
            "",
            "1. Run the verification commands and capture any existing failures.",
            f"2. Inspect `{first_file}` and one adjacent test or documentation file.",
            "3. Make the smallest useful change that improves the first-run path or reduces agent confusion.",
            "4. Re-run verification and summarize the changed files, result, and any follow-up risk.",
            "",
            "## Acceptance Gate",
            "",
            "- Every change explains the problem, the touched files, and the verification command.",
            "- No secrets, generated caches, or local environment files are committed.",
            "- Large rewrites must be split into reviewable commits.",
            "",
            "## Guardrails",
            "",
            *[f"- {note}" for note in guardrails],
            "",
        ]
    )


def write_workbench(
    root: Path,
    output: Path,
    project_name: str | None = None,
    adapters: tuple[str, ...] = (),
) -> tuple[Path, ...]:
    from .scanner import scan_repo

    invalid = tuple(adapter for adapter in adapters if adapter not in SUPPORTED_ADAPTERS)
    if invalid:
        raise ValueError(f"Unsupported adapter(s): {', '.join(invalid)}")

    expanded_adapters = expand_adapters(adapters)
    repo = scan_repo(root)
    workbench_ref = workbench_reference(root, output)
    output.mkdir(parents=True, exist_ok=True)
    agents_path = output / "AGENTS.md"
    tasks_path = output / "agent-task-pack.md"
    agents_path.write_text(render_agents_md(repo, project_name, expanded_adapters), encoding="utf-8")
    tasks_path.write_text(render_task_pack(repo, project_name, expanded_adapters), encoding="utf-8")
    written = [agents_path, tasks_path]
    for adapter in expanded_adapters:
        written.append(_write_adapter(output, adapter, workbench_ref))
    return tuple(written)


def workbench_reference(root: Path, output: Path) -> str:
    root = root.resolve()
    output = output.resolve()
    try:
        return output.relative_to(root).as_posix()
    except ValueError:
        return output.as_posix()


def expand_adapters(adapters: tuple[str, ...]) -> tuple[str, ...]:
    expanded: list[str] = []
    for adapter in adapters:
        choices = CONCRETE_ADAPTERS if adapter == "all" else (adapter,)
        for choice in choices:
            if choice not in expanded:
                expanded.append(choice)
    return tuple(expanded)


def _adapter_handoff_lines(adapters: tuple[str, ...]) -> tuple[str, ...]:
    expanded = expand_adapters(adapters)
    return tuple(f"- {label}: `{path}`" for label, path in (ADAPTER_HANDOFFS[adapter] for adapter in expanded))


def _agent_asset_lines(repo: RepoMap) -> tuple[str, ...]:
    return tuple(f"- {asset.label}: `{asset.path}`" for asset in repo.agent_assets)


def _counter_text(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"{kind}={count}" for kind, count in counter.most_common(6))


def _task_pack_files(repo: RepoMap):
    def rank(file):
        priority = 2
        if file.path == "README.md":
            priority = 0
        elif file.path.startswith(("src/agent_workbench/", "tests/test_agent_workbench")):
            priority = 1
        return (priority, -file.lines, file.path)

    return tuple(sorted(repo.files, key=rank)[:6])


def _write_adapter(output: Path, adapter: str, workbench_ref: str) -> Path:
    if adapter == "claude":
        path = output / "CLAUDE.md"
        path.write_text(
            "\n".join(
                [
                    "# Claude Code Instructions",
                    "",
                    "Read `AGENTS.md` first for the repository map, safe commands, high-signal files, and guardrails.",
                    "",
                    "Use `agent-task-pack.md` for the kickoff prompt, first jobs, verification commands, and acceptance gate.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    if adapter == "cursor":
        rules_dir = output / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        path = rules_dir / "agent-workbench.md"
        path.write_text(
            "\n".join(
                [
                    "# Agent Workbench Cursor Rule",
                    "",
                    f"Read `{workbench_ref}/AGENTS.md` before editing.",
                    "",
                    f"Use `{workbench_ref}/agent-task-pack.md` for the current kickoff prompt, verification commands, and acceptance gate.",
                    "",
                    "Keep changes small and run the listed verification commands before summarizing work.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    if adapter == "codex":
        codex_dir = output / ".codex"
        codex_dir.mkdir(parents=True, exist_ok=True)
        path = codex_dir / "AGENTS.md"
        path.write_text(
            "\n".join(
                [
                    "# Codex Instructions",
                    "",
                    f"Read `{workbench_ref}/AGENTS.md` first for the repository map, safe commands, high-signal files, and guardrails.",
                    "",
                    f"Use `{workbench_ref}/agent-task-pack.md` for the kickoff prompt, first jobs, verification commands, and acceptance gate.",
                    "",
                    "Keep generated caches, local environment files, and secrets out of commits.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    if adapter == "opencode":
        path = output / "opencode.json"
        path.write_text(
            "\n".join(
                [
                    "{",
                    '  "$schema": "https://opencode.ai/config.json",',
                    '  "instructions": [',
                    '    "AGENTS.md",',
                    '    "agent-task-pack.md"',
                    "  ]",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    raise ValueError(f"Unsupported adapter: {adapter}")
