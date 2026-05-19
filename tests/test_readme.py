import unittest
from pathlib import Path


class ReadmeTests(unittest.TestCase):
    def test_readme_shows_demo_and_output_preview(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("python -m agent_workbench demo", readme)
        self.assertIn("$ agent-workbench demo", readme)
        self.assertIn("$ tree .agent-workbench", readme)
        self.assertIn("--adapter claude --adapter cursor", readme)
        self.assertIn(".agent-workbench/", readme)
        self.assertIn("AGENTS.md", readme)
        self.assertIn("agent-task-pack.md", readme)
        self.assertIn("## Kickoff Prompt", readme)
        self.assertIn("## Verification Commands", readme)
        self.assertIn("examples/python-cli/source", readme)
        self.assertIn("examples/python-cli/agent-workbench/AGENTS.md", readme)
        self.assertIn("uv tool install git+https://github.com/Xiao-rx/agent-workbench.git", readme)
        self.assertIn("docs/release-v0.1.0.md", readme)
        self.assertIn("docs/launch-kit.md", readme)
        self.assertIn("provider-neutral", readme.lower())


if __name__ == "__main__":
    unittest.main()
