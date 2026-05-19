from __future__ import annotations

from pathlib import Path

from agent_workbench.generator import write_workbench


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    example = ROOT / "examples" / "python-cli"
    source = example / "source"
    output = example / "agent-workbench"
    write_workbench(source, output, "tiny-python-cli")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
