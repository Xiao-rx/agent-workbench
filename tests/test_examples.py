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

    def test_typescript_cli_example_contains_generated_workbench(self):
        root = Path("examples/typescript-cli")
        agents = (root / "agent-workbench" / "AGENTS.md").read_text(encoding="utf-8")
        task_pack = (root / "agent-workbench" / "agent-task-pack.md").read_text(encoding="utf-8")

        self.assertTrue((root / "source" / "package.json").exists())
        self.assertIn("# AGENTS.md for tiny-typescript-cli", agents)
        self.assertIn("typescript=1", agents)
        self.assertIn("Package managers: node/npm", agents)
        self.assertIn("npm test", agents)
        self.assertIn("src/index.ts", agents)
        self.assertIn("# Agent Task Pack: tiny-typescript-cli", task_pack)
        self.assertIn("tests/smoke.test.js", task_pack)


if __name__ == "__main__":
    unittest.main()
