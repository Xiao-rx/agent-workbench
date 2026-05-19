from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from . import __version__
from .checks import check_workbench, readiness_payload, render_readiness_text
from .generator import SUPPORTED_ADAPTERS, write_workbench
from .models import RepoMap
from .scanner import scan_repo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-workbench", description="Turn a repository into an AI-agent-ready workspace.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Print a compact repository map.")
    scan.add_argument("root", nargs="?", type=Path, default=Path("."))
    scan.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    scan.add_argument("--output-json", type=Path, help="Write the JSON repository map to a file.")

    check = subparsers.add_parser("check", help="Check whether a repository has an agent-ready workbench.")
    check.add_argument("root", nargs="?", type=Path, default=Path("."))
    check.add_argument("--workbench", type=Path, help="Workbench directory. Defaults to ROOT/.agent-workbench.")
    check.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    check.add_argument("--output-json", type=Path, help="Write the JSON readiness report to a file.")
    check.add_argument("--strict", action="store_true", help="Treat warnings as not ready.")
    check.add_argument(
        "--adapter",
        action="append",
        choices=SUPPORTED_ADAPTERS,
        default=[],
        help="Require a generated adapter handoff. Use all for Claude Code, Codex, and Cursor.",
    )

    init = subparsers.add_parser("init", help="Generate AGENTS.md and an agent task pack.")
    init.add_argument("root", nargs="?", type=Path, default=Path("."))
    init.add_argument("--output", type=Path, default=Path(".agent-workbench"))
    init.add_argument("--project-name")
    init.add_argument("--check", action="store_true", help="Run a readiness check after writing the workbench.")
    init.add_argument("--print-kickoff", action="store_true", help="Print the generated kickoff prompt after writing files.")
    init.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    init.add_argument("--output-json", type=Path, help="Write the JSON init proof to a file.")
    init.add_argument(
        "--adapter",
        action="append",
        choices=SUPPORTED_ADAPTERS,
        default=[],
        help="Also generate thin adapter files. Use all for Claude Code, Codex, and Cursor.",
    )

    demo = subparsers.add_parser("demo", help="Generate a no-secret demo workspace in a temporary repository.")
    demo.add_argument("--output", type=Path, help="Optional output directory. Defaults to a temporary directory.")
    demo.add_argument("--check", action="store_true", help="Run a readiness check after writing the demo workbench.")
    demo.add_argument("--print-kickoff", action="store_true", help="Print the generated kickoff prompt after writing files.")
    demo.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    demo.add_argument("--output-json", type=Path, help="Write the JSON demo proof to a file.")
    demo.add_argument(
        "--adapter",
        action="append",
        choices=SUPPORTED_ADAPTERS,
        default=[],
        help="Also generate thin adapter files. Use all for Claude Code, Codex, and Cursor.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        if args.output_json and args.format != "json":
            parser.error("--output-json requires --format json")
        repo = scan_repo(args.root)
        if args.format == "json":
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
        return 0

    if args.command == "init":
        if args.output_json and args.format != "json":
            parser.error("--output-json requires --format json")
        paths = write_workbench(args.root, args.output, args.project_name, tuple(args.adapter))
        if args.format == "json":
            payload = _workbench_payload(args.root.resolve(), args.output, paths)
            if args.check:
                report = check_workbench(args.root, args.output)
                payload["readiness"] = readiness_payload(report)
                _write_or_print_json(args.output_json, payload)
                return 0 if report.ready else 1
            _write_or_print_json(args.output_json, payload)
            return 0
        for path in paths:
            print(f"Wrote {path}")
        print(f"Proof: {_workbench_payload(args.root.resolve(), args.output, paths)['proof_summary']}")
        if args.print_kickoff:
            _print_kickoff(args.output)
        if args.check:
            return _print_readiness(args.root, args.output, "text")
        return 0

    if args.command == "check":
        if args.output_json and args.format != "json":
            parser.error("--output-json requires --format json")
        return _print_readiness(args.root, args.workbench, args.format, args.output_json, tuple(args.adapter), args.strict)

    if args.command == "demo":
        if args.output_json and args.format != "json":
            parser.error("--output-json requires --format json")
        root, output = _prepare_demo_workspace(args.output)
        paths = write_workbench(root, output, "agent-workbench-demo", tuple(args.adapter))
        if args.format == "json":
            payload = _workbench_payload(root, output, paths, demo_repository=root)
            if args.check:
                report = check_workbench(root, output)
                payload["readiness"] = readiness_payload(report)
                _write_or_print_json(args.output_json, payload)
                return 0 if report.ready else 1
            _write_or_print_json(args.output_json, payload)
            return 0
        print(f"Demo repository: {root}")
        for path in paths:
            print(f"Wrote {path}")
        print(f"Proof: {_workbench_payload(root, output, paths, demo_repository=root)['proof_summary']}")
        if args.print_kickoff:
            _print_kickoff(output)
        if args.check:
            return _print_readiness(root, output, "text")
        print("Next: open AGENTS.md and hand the task pack to your coding agent.")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


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
) -> dict[str, object]:
    task_pack = workbench / "agent-task-pack.md"
    repo = scan_repo(root)
    artifact_summary = _artifact_summary(workbench, paths)
    verification_command = repo.test_commands[0] if repo.test_commands else _verification_command(root, workbench)
    payload = {
        "root": str(root),
        "workbench": str(workbench),
        "written": [str(path) for path in paths],
        "artifact_summary": artifact_summary,
        "verification_command": verification_command,
        "proof_summary": _proof_summary(artifact_summary, verification_command),
        "kickoff_prompt": _extract_kickoff_prompt(task_pack.read_text(encoding="utf-8")),
    }
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


def _verification_command(root: Path, workbench: Path) -> str:
    return f'agent-workbench check "{root}" --workbench "{workbench}" --format json'


def _proof_summary(artifact_summary: dict[str, object], verification_command: str) -> str:
    core_files = artifact_summary["core_files"]
    adapter_files = artifact_summary["adapter_files"]
    core_text = ", ".join(str(item) for item in core_files)
    adapter_count = len(adapter_files) if isinstance(adapter_files, list) else 0
    adapter_text = f", {adapter_count} adapter handoff{'s' if adapter_count != 1 else ''}" if adapter_count else ""
    return f"wrote {artifact_summary['written_total']} files: {core_text}{adapter_text}; verify with `{verification_command}`."


def _write_json_file(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_or_print_json(path: Path | None, payload: dict[str, object]) -> None:
    if path:
        _write_json_file(path, payload)
        print(f"Wrote {path}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def _repo_map_payload(repo: RepoMap) -> dict[str, object]:
    return {
        "root": str(repo.root),
        "total_files": repo.total_files,
        "total_lines": repo.total_lines,
        "package_managers": list(repo.package_managers),
        "test_commands": list(repo.test_commands),
        "risk_notes": list(repo.risk_notes),
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


def _prepare_demo_workspace(output: Path | None) -> tuple[Path, Path]:
    if output:
        base = output.resolve()
        base.mkdir(parents=True, exist_ok=True)
    else:
        base = Path(tempfile.mkdtemp(prefix="agent-workbench-demo-"))

    root = base / "sample-repo"
    workbench = base / ".agent-workbench"
    root.mkdir(parents=True, exist_ok=True)
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
    return root, workbench
