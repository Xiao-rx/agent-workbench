from __future__ import annotations

import argparse
from pathlib import Path

from .generator import write_workbench
from .scanner import scan_repo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-workbench", description="Turn a repository into an AI-agent-ready workspace.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Print a compact repository map.")
    scan.add_argument("root", nargs="?", type=Path, default=Path("."))

    init = subparsers.add_parser("init", help="Generate AGENTS.md and an agent task pack.")
    init.add_argument("root", nargs="?", type=Path, default=Path("."))
    init.add_argument("--output", type=Path, default=Path(".agent-workbench"))
    init.add_argument("--project-name")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        repo = scan_repo(args.root)
        print(f"root={repo.root}")
        print(f"files={repo.total_files}")
        print(f"lines={repo.total_lines}")
        print(f"package_managers={','.join(repo.package_managers) if repo.package_managers else 'none'}")
        print(f"test_commands={','.join(repo.test_commands) if repo.test_commands else 'none'}")
        return 0

    if args.command == "init":
        agents_path, tasks_path = write_workbench(args.root, args.output, args.project_name)
        print(f"Wrote {agents_path}")
        print(f"Wrote {tasks_path}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2
