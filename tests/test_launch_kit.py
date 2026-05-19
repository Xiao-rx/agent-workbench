import unittest
from pathlib import Path


class LaunchKitTests(unittest.TestCase):
    def test_launch_kit_contains_shareable_assets(self):
        launch = Path("docs/launch-kit.md").read_text(encoding="utf-8")
        preview = Path("assets/social-preview.svg").read_text(encoding="utf-8")

        self.assertIn("Turn any repository into an AI-agent-ready workspace", launch)
        self.assertIn("Show HN", launch)
        self.assertIn("Share Post Draft", launch)
        self.assertIn("After publishing v0.8.0", launch)
        self.assertIn("--adapter all", launch)
        self.assertIn("agent-workbench demo --adapter all --check --print-kickoff", launch)
        self.assertIn("agent-workbench demo --adapter all --check --format json --output-json .agent-workbench/demo-proof.json", launch)
        self.assertIn("agent-workbench init . --output .agent-workbench --adapter all --check --format json --output-json .agent-workbench/init-proof.json", launch)
        self.assertIn("--print-kickoff", launch)
        self.assertIn("demo --format json", launch)
        self.assertIn("init --format json", launch)
        self.assertIn("Codex adapter", launch)
        self.assertIn("agent-workbench check . --format json", launch)
        self.assertIn("agent-workbench scan . --format json --output-json .agent-workbench/repo-map.json", launch)
        self.assertIn("agent-workbench check . --format json --output-json .agent-workbench/readiness.json", launch)
        self.assertIn("readiness check", launch)
        self.assertIn("scan JSON", launch)
        self.assertIn("Python and TypeScript", launch)
        self.assertIn("Turn any repository into an AI-agent-ready workspace with AGENTS.md, task packs, adapters, and scan JSON.", launch)
        self.assertIn("developer-tools, llm, productivity", launch)
        self.assertIn("uv tool install git+https://github.com/Xiao-rx/agent-workbench.git", launch)
        self.assertIn("https://github.com/Xiao-rx/agent-workbench/releases/tag/v0.8.0", launch)
        self.assertIn("<svg", preview)
        self.assertIn("Agent Workbench", preview)


if __name__ == "__main__":
    unittest.main()
