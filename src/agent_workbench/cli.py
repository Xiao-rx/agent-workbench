from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

from .generator import SUPPORTED_ADAPTERS, write_workbench
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
    init.add_argument(
        "--adapter",
        action="append",
        choices=SUPPORTED_ADAPTERS,
        default=[],
        help="Also generate a thin adapter for a specific agent tool. Repeat for multiple adapters.",
    )

    demo = subparsers.add_parser("demo", help="Generate a no-secret demo workspace in a temporary repository.")
    demo.add_argument("--output", type=Path, help="Optional output directory. Defaults to a temporary directory.")

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
        paths = write_workbench(args.root, args.output, args.project_name, tuple(args.adapter))
        for path in paths:
            print(f"Wrote {path}")
        return 0

    if args.command == "demo":
        root, output = _prepare_demo_workspace(args.output)
        paths = write_workbench(root, output, "agent-workbench-demo")
        print(f"Demo repository: {root}")
        for path in paths:
            print(f"Wrote {path}")
        print("Next: open AGENTS.md and hand the task pack to your coding agent.")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


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
