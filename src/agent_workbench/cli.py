from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from . import __version__
from .checks import ReadinessReport, check_workbench, readiness_payload, render_readiness_text
from .generator import CONCRETE_ADAPTERS, SUPPORTED_ADAPTERS, expand_adapters, write_workbench
from .models import RepoMap
from .scanner import scan_repo


_DEFAULT_PROOF = object()
_DEFAULT_REPORT = object()
_FEEDBACK_URL = "https://github.com/Xiao-rx/agent-workbench/issues/new?template=agent-workbench-report.yml"
_FEEDBACK_SAFETY_NOTE = (
    "Paste only sanitized output. Do not include tokens, `.env.local`, `.env.bak`, "
    "private repository names, or proprietary source snippets."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-workbench", description="Turn a repository into an AI-agent-ready workspace.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Print a compact repository map.")
    scan.add_argument("root", nargs="?", type=Path, default=Path("."))
    scan.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    scan.add_argument("--output-json", type=Path, help="Write the JSON repository map to a file. Implies --format json.")

    check = subparsers.add_parser("check", help="Check whether a repository has an agent-ready workbench.")
    check.add_argument("root", nargs="?", type=Path, default=Path("."))
    check.add_argument("--workbench", type=Path, help="Workbench directory. Defaults to ROOT/.agent-workbench.")
    check.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    check.add_argument("--output-json", type=Path, help="Write the JSON readiness report to a file. Implies --format json.")
    check.add_argument("--strict", action="store_true", help="Treat warnings as not ready.")
    check.add_argument(
        "--adapter",
        action="append",
        choices=SUPPORTED_ADAPTERS,
        default=[],
        help="Require a generated adapter handoff. Use all for Claude Code, Codex, Cursor, and OpenCode.",
    )

    init = subparsers.add_parser("init", help="Generate AGENTS.md and an agent task pack.")
    init.add_argument("root", nargs="?", type=Path, default=Path("."))
    init.add_argument("--output", type=Path, default=Path(".agent-workbench"))
    init.add_argument("--project-name")
    init.add_argument("--check", action="store_true", help="Run a readiness check after writing the workbench.")
    init.add_argument("--strict", action="store_true", help="Run a readiness check and treat warnings as not ready.")
    init.add_argument("--print-kickoff", action="store_true", help="Print the generated kickoff prompt after writing files.")
    init.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    init.add_argument("--output-json", type=Path, help="Write the JSON init proof to a file. Implies --format json.")
    init.add_argument(
        "--proof",
        nargs="?",
        const=_DEFAULT_PROOF,
        type=Path,
        metavar="PATH",
        help="Write a shareable JSON init proof. Optional PATH defaults to the generated workbench and implies --check and --format json.",
    )
    init.add_argument(
        "--report",
        nargs="?",
        const=_DEFAULT_REPORT,
        type=Path,
        metavar="PATH",
        help="Write a shareable Markdown init report. Optional PATH defaults to the generated workbench and implies --check.",
    )
    init.add_argument(
        "--adapter",
        action="append",
        choices=SUPPORTED_ADAPTERS,
        default=[],
        help="Also generate thin adapter files. Use all for Claude Code, Codex, Cursor, and OpenCode.",
    )

    demo = subparsers.add_parser("demo", help="Generate a no-secret demo workspace in a temporary repository.")
    demo.add_argument("--output", type=Path, help="Optional output directory. Defaults to a temporary directory.")
    demo.add_argument(
        "--template",
        choices=("python", "typescript"),
        default="python",
        help="Demo repository template. Use typescript to exercise the Node/npm proof path.",
    )
    demo.add_argument("--check", action="store_true", help="Run a readiness check after writing the demo workbench.")
    demo.add_argument("--strict", action="store_true", help="Run a readiness check and treat warnings as not ready.")
    demo.add_argument("--print-kickoff", action="store_true", help="Print the generated kickoff prompt after writing files.")
    demo.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    demo.add_argument("--output-json", type=Path, help="Write the JSON demo proof to a file. Implies --format json.")
    demo.add_argument(
        "--proof",
        nargs="?",
        const=_DEFAULT_PROOF,
        type=Path,
        metavar="PATH",
        help="Write a shareable strict all-adapter JSON demo proof. Optional PATH defaults to the generated workbench. Implies --adapter all, --strict, and --format json.",
    )
    demo.add_argument(
        "--report",
        nargs="?",
        const=_DEFAULT_REPORT,
        type=Path,
        metavar="PATH",
        help="Write a shareable Markdown demo report. Optional PATH defaults to the generated workbench. Implies --adapter all and --strict.",
    )
    demo.add_argument(
        "--adapter",
        action="append",
        choices=SUPPORTED_ADAPTERS,
        default=[],
        help="Also generate thin adapter files. Use all for Claude Code, Codex, Cursor, and OpenCode.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        output_format = _effective_format(args.format, args.output_json)
        repo = scan_repo(args.root)
        if output_format == "json":
            payload = _repo_map_payload(repo)
            if args.output_json:
                _write_json_file(args.output_json, payload)
                print(f"Wrote {args.output_json}")
            else:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        print(f"root={repo.root}")
        print(f"files={repo.total_files}")
        print(f"lines={repo.total_lines}")
        print(f"package_managers={','.join(repo.package_managers) if repo.package_managers else 'none'}")
        print(f"test_commands={','.join(repo.test_commands) if repo.test_commands else 'none'}")
        print(f"agent_assets={','.join(asset.path for asset in repo.agent_assets) if repo.agent_assets else 'none'}")
        return 0

    if args.command == "init":
        root = args.root.resolve()
        workbench = _resolve_init_output(root, args.output)
        output_json = _proof_output_json(parser, args.output_json, args.proof, workbench, "init-proof.json")
        report_path = _report_output_path(args.report, workbench, "init-report.md")
        if output_json and report_path and output_json == report_path:
            parser.error("--report and --proof/--output-json cannot write to the same path")
        output_format = _effective_format(args.format, output_json)
        proof_requested = args.proof is not None
        report_requested = args.report is not None
        check_requested = args.check or args.strict or proof_requested or report_requested
        announce_report = output_format != "json" or output_json is not None
        proof_command = _init_proof_command(args.root, args.output, args.proof)
        report_command = _init_report_command(args.root, args.output, args.report)
        repo = scan_repo(root)
        paths = write_workbench(root, workbench, args.project_name, tuple(args.adapter))
        if output_format == "json":
            report = check_workbench(root, workbench, tuple(args.adapter), args.strict) if check_requested else None
            payload = _workbench_payload(
                root,
                workbench,
                paths,
                repo=repo,
                adapters=tuple(args.adapter),
                strict=args.strict,
                show_readiness_command=check_requested or bool(args.adapter),
                readiness_report=report,
                proof_command=proof_command,
                report_path=report_path,
                report_command=report_command,
            )
            if check_requested:
                payload["readiness"] = readiness_payload(report)
                _write_workbench_report(report_path, payload, announce=announce_report)
                _write_or_print_json(output_json, payload, print_proof=proof_requested)
                return 0 if report.ready else 1
            _write_workbench_report(report_path, payload, announce=announce_report)
            _write_or_print_json(output_json, payload, print_proof=proof_requested)
            return 0
        for path in paths:
            print(f"Wrote {path}")
        report = check_workbench(root, workbench, tuple(args.adapter), args.strict) if check_requested else None
        proof_payload = _workbench_payload(
            root,
            workbench,
            paths,
            repo=repo,
            adapters=tuple(args.adapter),
            strict=args.strict,
            show_readiness_command=check_requested or bool(args.adapter),
            readiness_report=report,
            proof_command=proof_command,
            report_path=report_path,
            report_command=report_command,
        )
        _write_workbench_report(report_path, proof_payload)
        print(f"Proof: {proof_payload['proof_summary']}")
        if report_path:
            print(f"Report: {proof_payload['proof_summary']}")
        if args.print_kickoff:
            _print_kickoff(workbench)
        if check_requested:
            print(render_readiness_text(report))
            return 0 if report.ready else 1
        return 0

    if args.command == "check":
        output_format = _effective_format(args.format, args.output_json)
        return _print_readiness(args.root, args.workbench, output_format, args.output_json, tuple(args.adapter), args.strict)

    if args.command == "demo":
        proof_requested = args.proof is not None
        report_requested = args.report is not None
        shareable_demo_requested = proof_requested or report_requested
        demo_adapters = _demo_adapters(tuple(args.adapter), shareable_demo_requested)
        strict = args.strict or shareable_demo_requested
        check_requested = args.check or strict
        root, output = _prepare_demo_workspace(args.output, args.template)
        output_json = _proof_output_json(parser, args.output_json, args.proof, output, "demo-proof.json")
        report_path = _report_output_path(args.report, output, "demo-report.md")
        if output_json and report_path and output_json == report_path:
            parser.error("--report and --proof/--output-json cannot write to the same path")
        output_format = _effective_format(args.format, output_json)
        announce_report = output_format != "json" or output_json is not None
        proof_command = _demo_proof_command(args.output, args.proof)
        report_command = _demo_report_command(args.output, args.report)
        repo = scan_repo(root)
        paths = write_workbench(root, output, "agent-workbench-demo", demo_adapters)
        if output_format == "json":
            report = check_workbench(root, output, demo_adapters, strict) if check_requested else None
            payload = _workbench_payload(
                root,
                output,
                paths,
                demo_repository=root,
                repo=repo,
                adapters=demo_adapters,
                strict=strict,
                show_readiness_command=check_requested or bool(args.adapter),
                readiness_report=report,
                proof_command=proof_command,
                report_path=report_path,
                report_command=report_command,
            )
            if check_requested:
                payload["readiness"] = readiness_payload(report)
                _write_workbench_report(report_path, payload, announce=announce_report)
                _write_or_print_json(output_json, payload, print_proof=proof_requested)
                return 0 if report.ready else 1
            _write_workbench_report(report_path, payload, announce=announce_report)
            _write_or_print_json(output_json, payload, print_proof=proof_requested)
            return 0
        print(f"Demo repository: {root}")
        for path in paths:
            print(f"Wrote {path}")
        report = check_workbench(root, output, demo_adapters, strict) if check_requested else None
        proof_payload = _workbench_payload(
            root,
            output,
            paths,
            demo_repository=root,
            repo=repo,
            adapters=demo_adapters,
            strict=strict,
            show_readiness_command=check_requested or bool(args.adapter),
            readiness_report=report,
            proof_command=proof_command,
            report_path=report_path,
            report_command=report_command,
        )
        _write_workbench_report(report_path, proof_payload)
        print(f"Proof: {proof_payload['proof_summary']}")
        if report_path:
            print(f"Report: {proof_payload['proof_summary']}")
        if args.print_kickoff:
            _print_kickoff(output)
        if check_requested:
            print(render_readiness_text(report))
            return 0 if report.ready else 1
        print("Next: open AGENTS.md and hand the task pack to your coding agent.")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def _effective_format(output_format: str, output_json: Path | None) -> str:
    if output_json:
        return "json"
    return output_format


def _proof_output_json(
    parser: argparse.ArgumentParser,
    output_json: Path | None,
    proof: object | Path | None,
    workbench: Path,
    default_name: str,
) -> Path | None:
    if proof is _DEFAULT_PROOF:
        return output_json or (workbench / default_name)
    if output_json and proof and output_json != proof:
        parser.error("--proof and --output-json cannot write to different paths")
    if isinstance(proof, Path):
        return proof
    return output_json


def _report_output_path(report: object | Path | None, workbench: Path, default_name: str) -> Path | None:
    if report is _DEFAULT_REPORT:
        return workbench / default_name
    if isinstance(report, Path):
        return report
    return None


def _demo_adapters(adapters: tuple[str, ...], proof_requested: bool) -> tuple[str, ...]:
    if proof_requested and "all" not in adapters:
        return (*adapters, "all")
    return adapters


def _demo_proof_command(output: Path | None, proof: object | Path | None) -> str | None:
    if proof is None:
        return None
    parts = ["agent-workbench", "demo"]
    if output:
        parts.extend(("--output", str(output)))
    parts.append("--proof")
    if isinstance(proof, Path):
        parts.append(str(proof))
    return _command_text(parts)


def _demo_report_command(output: Path | None, report: object | Path | None) -> str | None:
    if report is None:
        return None
    parts = ["agent-workbench", "demo"]
    if output:
        parts.extend(("--output", str(output)))
    parts.append("--report")
    if isinstance(report, Path):
        parts.append(str(report))
    return _command_text(parts)


def _init_report_command(root: Path, output: Path, report: object | Path | None) -> str | None:
    if report is None:
        return None
    parts = ["agent-workbench", "init", str(root), "--output", str(output), "--report"]
    if isinstance(report, Path):
        parts.append(str(report))
    return _command_text(parts)


def _init_proof_command(root: Path, output: Path, proof: object | Path | None) -> str | None:
    if proof is None:
        return None
    parts = ["agent-workbench", "init", str(root), "--output", str(output), "--proof"]
    if isinstance(proof, Path):
        parts.append(str(proof))
    return _command_text(parts)


def _print_readiness(
    root: Path,
    workbench: Path | None,
    output_format: str,
    output_json: Path | None = None,
    adapters: tuple[str, ...] = (),
    strict: bool = False,
) -> int:
    report = check_workbench(root, workbench, adapters, strict)
    if output_format == "json":
        payload = readiness_payload(report)
        if output_json:
            _write_json_file(output_json, payload)
            print(f"Wrote {output_json}")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_readiness_text(report))
    return 0 if report.ready else 1


def _resolve_init_output(root: Path, output: Path) -> Path:
    if output.is_absolute():
        return output.resolve()
    return (root / output).resolve()


def _print_kickoff(workbench: Path) -> None:
    task_pack = workbench / "agent-task-pack.md"
    text = task_pack.read_text(encoding="utf-8")
    prompt = _extract_kickoff_prompt(text)
    print("")
    print("Kickoff prompt:")
    print(prompt)


def _extract_kickoff_prompt(text: str) -> str:
    marker = "## Kickoff Prompt"
    start = text.index(marker)
    fenced = text.index("```", start)
    line_start = text.index("\n", fenced) + 1
    end = text.index("```", line_start)
    return text[line_start:end].strip()


def _workbench_payload(
    root: Path,
    workbench: Path,
    paths: tuple[Path, ...],
    demo_repository: Path | None = None,
    repo: RepoMap | None = None,
    adapters: tuple[str, ...] = (),
    strict: bool = False,
    show_readiness_command: bool = False,
    readiness_report: ReadinessReport | None = None,
    proof_command: str | None = None,
    report_path: Path | None = None,
    report_command: str | None = None,
) -> dict[str, object]:
    task_pack = workbench / "agent-task-pack.md"
    repo = repo or scan_repo(root)
    artifact_summary = _artifact_summary(workbench, paths)
    agent_assets = _agent_asset_payload(repo)
    readiness_args = _readiness_args(root, workbench, adapters, strict)
    readiness_command = _command_text(readiness_args)
    verification_command = repo.test_commands[0] if repo.test_commands else readiness_command
    readiness_summary = _readiness_summary(readiness_report) if readiness_report else None
    readiness_counts = _readiness_counts(readiness_report) if readiness_report else None
    next_action = _proof_next_action(readiness_report)
    proof_summary = _proof_summary(
        artifact_summary,
        verification_command,
        agent_assets,
        readiness_command,
        show_readiness_command,
        readiness_summary,
    )
    share_snippet = _share_snippet(artifact_summary, agent_assets, verification_command, readiness_summary)
    payload = {
        "kind": "agent_workbench.proof",
        "schema_version": 1,
        "root": str(root),
        "workbench": str(workbench),
        "written": [str(path) for path in paths],
        "artifact_summary": artifact_summary,
        "handoff": {
            "agents_md": str(workbench / "AGENTS.md"),
            "task_pack": str(task_pack),
            "next_action": next_action,
        },
        "next_action": next_action,
        "agent_assets": agent_assets,
        "agent_assets_source": "pre_write_scan",
        "verification_command": verification_command,
        "readiness_command": readiness_command,
        "readiness_args": readiness_args,
        "proof_summary": proof_summary,
        "share_snippet": share_snippet,
        "feedback": {
            "url": _FEEDBACK_URL,
            "safety_note": _FEEDBACK_SAFETY_NOTE,
        },
        "kickoff_prompt": _extract_kickoff_prompt(task_pack.read_text(encoding="utf-8")),
    }
    if readiness_summary:
        payload["readiness_summary"] = readiness_summary
    if readiness_counts:
        payload["readiness_counts"] = readiness_counts
    if proof_command:
        payload["proof_command"] = proof_command
    if report_path:
        payload["report"] = str(report_path)
    if report_command:
        payload["report_command"] = report_command
    if demo_repository is not None:
        payload["demo_repository"] = str(demo_repository)
    return payload


def _artifact_summary(workbench: Path, paths: tuple[Path, ...]) -> dict[str, object]:
    core_files: list[str] = []
    adapter_files: list[str] = []
    for path in paths:
        try:
            relative = path.relative_to(workbench).as_posix()
        except ValueError:
            relative = path.as_posix()
        if relative in {"AGENTS.md", "agent-task-pack.md"}:
            core_files.append(relative)
        else:
            adapter_files.append(relative)
    return {
        "written_total": len(paths),
        "core_files": core_files,
        "adapter_files": adapter_files,
    }


def _readiness_args(root: Path, workbench: Path, adapters: tuple[str, ...] = (), strict: bool = False) -> list[str]:
    parts = ["agent-workbench", "check", str(root), "--workbench", str(workbench)]
    parts.extend(_adapter_check_args(adapters))
    if strict:
        parts.append("--strict")
    parts.extend(["--format", "json"])
    return parts


def _adapter_check_args(adapters: tuple[str, ...]) -> tuple[str, ...]:
    expanded = expand_adapters(adapters)
    if not expanded:
        return ()
    if expanded == CONCRETE_ADAPTERS:
        return ("--adapter", "all")
    parts: list[str] = []
    for adapter in expanded:
        parts.extend(("--adapter", adapter))
    return tuple(parts)


def _command_text(args: list[str]) -> str:
    return " ".join(_quote_arg(arg) for arg in args)


def _quote_arg(arg: str) -> str:
    if not arg or any(char.isspace() for char in arg):
        return '"' + arg.replace('"', '\\"') + '"'
    return arg


def _agent_asset_payload(repo: RepoMap) -> list[dict[str, str]]:
    return [
        {
            "path": asset.path,
            "label": asset.label,
        }
        for asset in repo.agent_assets
    ]


def _proof_summary(
    artifact_summary: dict[str, object],
    verification_command: str,
    agent_assets: list[dict[str, str]],
    readiness_command: str,
    show_readiness_command: bool = False,
    readiness_summary: str | None = None,
) -> str:
    core_files = artifact_summary["core_files"]
    adapter_files = artifact_summary["adapter_files"]
    core_text = ", ".join(str(item) for item in core_files)
    adapter_count = len(adapter_files) if isinstance(adapter_files, list) else 0
    adapter_text = f", {adapter_count} adapter handoff{'s' if adapter_count != 1 else ''}" if adapter_count else ""
    asset_count = len(agent_assets)
    asset_text = f", detected {asset_count} existing agent asset{'s' if asset_count != 1 else ''}" if asset_count else ""
    summary = f"wrote {artifact_summary['written_total']} files: {core_text}{adapter_text}{asset_text}; verify with `{verification_command}`."
    if readiness_summary:
        summary = f"{summary} Readiness: {readiness_summary}."
    if show_readiness_command and readiness_command != verification_command:
        summary = f"{summary} Readiness gate: `{readiness_command}`."
    return summary


def _share_snippet(
    artifact_summary: dict[str, object],
    agent_assets: list[dict[str, str]],
    verification_command: str,
    readiness_summary: str | None = None,
) -> str:
    adapter_files = artifact_summary.get("adapter_files")
    adapter_count = len(adapter_files) if isinstance(adapter_files, list) else 0
    asset_count = len(agent_assets)
    readiness_text = f" Readiness: {readiness_summary}." if readiness_summary else ""
    return (
        "Agent Workbench turned this repo into an AI-agent-ready workspace: "
        f"AGENTS.md + agent-task-pack.md, {adapter_count} adapter handoff"
        f"{'s' if adapter_count != 1 else ''}, {asset_count} existing agent asset"
        f"{'s' if asset_count != 1 else ''} detected. Verify with `{verification_command}`."
        f"{readiness_text}"
    )


def _readiness_summary(report: ReadinessReport) -> str:
    counts = _readiness_counts(report)
    return f"{report.status} ({counts['pass']} pass, {counts['warn']} warn, {counts['fail']} fail)"


def _readiness_counts(report: ReadinessReport) -> dict[str, int]:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for check in report.checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts


def _proof_next_action(report: ReadinessReport | None) -> str:
    if report:
        return report.next_action
    return "run the readiness_command before handing the task pack to your coding agent."


def _write_json_file(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_or_print_json(path: Path | None, payload: dict[str, object], print_proof: bool = False) -> None:
    if path:
        _write_json_file(path, payload)
        print(f"Wrote {path}")
        if print_proof and isinstance(payload.get("proof_summary"), str):
            print(f"Proof: {payload['proof_summary']}")
        if print_proof and isinstance(payload.get("proof_command"), str):
            print(f"Proof command: {payload['proof_command']}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def _write_workbench_report(path: Path | None, payload: dict[str, object], *, announce: bool = True) -> None:
    if not path:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_workbench_report(payload), encoding="utf-8")
    if announce:
        print(f"Wrote {path}")


def _render_workbench_report(payload: dict[str, object]) -> str:
    artifact_summary = payload.get("artifact_summary", {})
    core_files = _string_list_from_mapping(artifact_summary, "core_files")
    adapter_files = _string_list_from_mapping(artifact_summary, "adapter_files")
    agent_assets = payload.get("agent_assets")
    readiness_counts = payload.get("readiness_counts")
    is_demo = bool(payload.get("demo_repository"))
    display = _ReportDisplay(payload)

    lines = [
        "# Agent Workbench Demo Report" if is_demo else "# Agent Workbench Init Report",
        "",
        "A no-secret proof that Agent Workbench can turn a fresh repository into an AI-agent-ready workspace."
        if is_demo
        else "A shareable proof that Agent Workbench turned this repository into an AI-agent-ready workspace.",
        "",
        f"- Repository: `{display.value(payload.get('demo_repository', payload.get('root', '')))}`",
        f"- Workbench: `{display.value(payload.get('workbench', ''))}`",
        f"- Report command: `{display.value(payload.get('report_command', 'agent-workbench init . --report'))}`",
    ]
    if payload.get("proof_command"):
        lines.append(f"- Proof command: `{display.value(payload['proof_command'])}`")
    lines.extend(
        [
            f"- Proof: {display.value(payload.get('proof_summary', ''))}",
            f"- Next action: {payload.get('next_action', '')}",
            "",
            "## Files Written",
            "",
        ]
    )
    for item in core_files:
        lines.append(f"- `{item}`")
    for item in adapter_files:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Readiness", ""])
    if payload.get("readiness_summary"):
        lines.append(f"- Status: {payload['readiness_summary']}")
    if isinstance(readiness_counts, dict):
        lines.append(
            f"- Counts: {readiness_counts.get('pass', 0)} pass, {readiness_counts.get('warn', 0)} warn, {readiness_counts.get('fail', 0)} fail"
        )
    lines.append(f"- Gate: `{display.value(payload.get('readiness_command', ''))}`")
    lines.extend(["", "## Existing Agent Assets", ""])
    if isinstance(agent_assets, list) and agent_assets:
        for asset in agent_assets:
            if isinstance(asset, dict):
                lines.append(f"- `{asset.get('path', '')}` ({asset.get('label', 'agent asset')})")
    else:
        lines.append("- None detected before generation.")
    lines.extend(
        [
            "",
            "## Share Feedback",
            "",
            "Copy/paste summary:",
            "",
            "```text",
            display.value(payload.get("share_snippet", "")),
            "```",
            "",
            "Open an Agent Workbench report issue after removing local/private details:",
            "",
            f"- Feedback form: {_FEEDBACK_URL}",
            f"- Safety: {_FEEDBACK_SAFETY_NOTE}",
            "",
            "## Kickoff Prompt",
            "",
            "```text",
            str(payload.get("kickoff_prompt", "")),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


class _ReportDisplay:
    def __init__(self, payload: dict[str, object]):
        replacements: list[tuple[str, str]] = []
        replacements.extend(self._path_replacements(payload.get("report"), "<report>"))
        replacements.extend(self._path_replacements(payload.get("workbench"), "<workbench>"))
        replacements.extend(self._path_replacements(payload.get("demo_repository", payload.get("root")), "<repo>"))
        if payload.get("demo_repository"):
            try:
                demo_base = Path(str(payload["demo_repository"])).parent
                replacements.extend(self._path_replacements(demo_base, "<demo-workspace>"))
            except (OSError, ValueError):
                pass
        replacements.extend(self._home_replacements())
        replacements.sort(key=lambda item: len(item[0]), reverse=True)
        self._replacements = tuple(replacements)

    def value(self, value: object) -> str:
        text = str(value)
        for raw, label in self._replacements:
            text = text.replace(raw, label)
        return text

    @staticmethod
    def _path_replacements(value: object, label: str) -> list[tuple[str, str]]:
        if not value:
            return []
        try:
            path = Path(str(value))
        except (OSError, ValueError):
            return []
        variants = {str(path), path.as_posix()}
        try:
            resolved = path.resolve()
        except (OSError, ValueError):
            resolved = None
        if resolved:
            variants.update((str(resolved), resolved.as_posix()))
        return [(variant, label) for variant in variants if variant]

    @staticmethod
    def _home_replacements() -> list[tuple[str, str]]:
        replacements: list[tuple[str, str]] = []
        home = Path.home()
        home_label = "$HOME" if os.name != "nt" else "%USERPROFILE%"
        for variant in {str(home), home.as_posix()}:
            if variant:
                replacements.append((variant, home_label))
        return replacements


def _string_list_from_mapping(mapping: object, key: str) -> list[str]:
    if not isinstance(mapping, dict):
        return []
    value = mapping.get(key)
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _repo_map_payload(repo: RepoMap) -> dict[str, object]:
    return {
        "kind": "agent_workbench.repo_map",
        "schema_version": 1,
        "root": str(repo.root),
        "total_files": repo.total_files,
        "total_lines": repo.total_lines,
        "package_managers": list(repo.package_managers),
        "test_commands": list(repo.test_commands),
        "risk_notes": list(repo.risk_notes),
        "agent_assets": _agent_asset_payload(repo),
        "files": [
            {
                "path": file.path,
                "kind": file.kind,
                "lines": file.lines,
                "bytes": file.bytes,
            }
            for file in repo.files
        ],
    }


def _prepare_demo_workspace(output: Path | None, template: str = "python") -> tuple[Path, Path]:
    if output:
        base = output.resolve()
        base.mkdir(parents=True, exist_ok=True)
    else:
        base = Path(tempfile.mkdtemp(prefix="agent-workbench-demo-"))

    root = base / "sample-repo"
    workbench = base / ".agent-workbench"
    root.mkdir(parents=True, exist_ok=True)
    if template == "typescript":
        _write_typescript_demo(root)
    else:
        _write_python_demo(root)
    return root, workbench


def _write_python_demo(root: Path) -> None:
    (root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "agent-workbench-demo"',
                'version = "0.1.0"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Agent Workbench Demo\n\nA tiny repository for the demo command.\n", encoding="utf-8")
    (root / ".gitignore").write_text(".env\n.env.*\n!.env.example\n__pycache__/\n.pytest_cache/\n", encoding="utf-8")
    github = root / ".github"
    github.mkdir(exist_ok=True)
    (github / "copilot-instructions.md").write_text(
        "Keep changes small, run `python -m unittest discover -s tests`, and avoid committing secrets.\n",
        encoding="utf-8",
    )
    tests = root / "tests"
    tests.mkdir(exist_ok=True)
    (tests / "test_demo.py").write_text(
        "\n".join(
            [
                "import unittest",
                "",
                "",
                "class DemoTests(unittest.TestCase):",
                "    def test_demo(self):",
                "        self.assertTrue(True)",
                "",
                "",
                "if __name__ == \"__main__\":",
                "    unittest.main()",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_typescript_demo(root: Path) -> None:
    (root / "package.json").write_text(
        "\n".join(
            [
                "{",
                '  "name": "agent-workbench-demo-ts",',
                '  "version": "0.1.0",',
                '  "type": "module",',
                '  "private": true,',
                '  "scripts": {',
                '    "test": "node --test tests/smoke.test.js"',
                "  }",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "tsconfig.json").write_text(
        "\n".join(
            [
                "{",
                '  "compilerOptions": {',
                '    "target": "ES2022",',
                '    "module": "ES2022",',
                '    "moduleResolution": "Node"',
                "  }",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Agent Workbench TypeScript Demo\n\nA tiny TypeScript repository for the demo command.\n", encoding="utf-8")
    (root / ".gitignore").write_text("node_modules/\ndist/\n.env\n.env.*\n!.env.example\n", encoding="utf-8")
    github = root / ".github"
    github.mkdir(exist_ok=True)
    (github / "copilot-instructions.md").write_text(
        "Keep changes small, run `npm test`, and avoid committing secrets.\n",
        encoding="utf-8",
    )
    src = root / "src"
    src.mkdir(exist_ok=True)
    (src / "index.ts").write_text(
        "\n".join(
            [
                "export function greeting(name: string): string {",
                "  return `hello, ${name}`;",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    tests = root / "tests"
    tests.mkdir(exist_ok=True)
    (tests / "smoke.test.js").write_text(
        "\n".join(
            [
                "import test from 'node:test';",
                "import assert from 'node:assert/strict';",
                "",
                "test('demo repository is testable without dependencies', () => {",
                "  assert.equal('hello, agent', `hello, ${'agent'}`);",
                "});",
                "",
            ]
        ),
        encoding="utf-8",
    )
