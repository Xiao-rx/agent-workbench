import unittest
from pathlib import Path


class ExampleArtifactTests(unittest.TestCase):
    def test_python_cli_example_contains_generated_workbench(self):
        root = Path("examples/python-cli")
        agents = (root / "agent-workbench" / "AGENTS.md").read_text(encoding="utf-8")
        task_pack = (root / "agent-workbench" / "agent-task-pack.md").read_text(encoding="utf-8")

        self.assertTrue((root / "source" / "pyproject.toml").exists())
        self.assertIn("# AGENTS.md for tiny-python-cli", agents)
        self.assertIn("tiny_cli/cli.py", agents)
        self.assertIn("python -m unittest discover -s tests", agents)
        self.assertIn("# Agent Task Pack: tiny-python-cli", task_pack)
        self.assertIn("## Kickoff Prompt", task_pack)


if __name__ == "__main__":
    unittest.main()
