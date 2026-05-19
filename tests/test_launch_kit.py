import unittest
from pathlib import Path


class LaunchKitTests(unittest.TestCase):
    def test_launch_kit_contains_shareable_assets(self):
        launch = Path("docs/launch-kit.md").read_text(encoding="utf-8")
        preview = Path("assets/social-preview.svg").read_text(encoding="utf-8")

        self.assertIn("Turn any repository into an AI-agent-ready workspace", launch)
        self.assertIn("Show HN", launch)
        self.assertIn("--adapter claude --adapter cursor", launch)
        self.assertIn("uv tool install git+https://github.com/Xiao-rx/agent-workbench.git", launch)
        self.assertIn("https://github.com/Xiao-rx/agent-workbench/releases/tag/v0.2.0", launch)
        self.assertIn("<svg", preview)
        self.assertIn("Agent Workbench", preview)


if __name__ == "__main__":
    unittest.main()
