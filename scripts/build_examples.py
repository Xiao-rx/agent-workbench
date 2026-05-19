from __future__ import annotations

from pathlib import Path

from agent_workbench.generator import write_workbench


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    examples = (
        ("python-cli", "tiny-python-cli"),
        ("typescript-cli", "tiny-typescript-cli"),
    )
    for directory, project_name in examples:
        example = ROOT / "examples" / directory
        source = example / "source"
        output = example / "agent-workbench"
        write_workbench(source, output, project_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
