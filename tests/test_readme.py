import unittest
from pathlib import Path


class ReadmeTests(unittest.TestCase):
    def test_readme_shows_demo_and_output_preview(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("python -m agent_workbench demo", readme)
        self.assertIn("[中文](README.zh-CN.md)", readme)
        self.assertIn("agent-workbench demo --adapter claude --adapter cursor", readme)
        self.assertIn("python -m agent_workbench scan . --format json", readme)
        self.assertIn("agent-workbench scan [ROOT] [--format text|json]", readme)
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
        self.assertIn("examples/typescript-cli/source", readme)
        self.assertIn("examples/typescript-cli/agent-workbench/AGENTS.md", readme)
        self.assertIn("uv tool install git+https://github.com/Xiao-rx/agent-workbench.git", readme)
        self.assertIn("docs/release-v0.3.0.md", readme)
        self.assertIn("docs/launch-kit.md", readme)
        self.assertIn("provider-neutral", readme.lower())
        self.assertIn("用一条命令把任意代码仓库变成 AI coding agent 可以安全接手的工作区", readme)
        self.assertIn("默认输出不绑定任何模型或工具", readme)

    def test_chinese_readme_covers_first_run_path(self):
        readme = Path("README.zh-CN.md").read_text(encoding="utf-8")

        self.assertIn("[English](README.md)", readme)
        self.assertIn("用一条命令把任意代码仓库变成 AI coding agent 可以安全接手的工作区", readme)
        self.assertIn("agent-workbench demo --adapter claude --adapter cursor", readme)
        self.assertIn("agent-workbench scan . --format json", readme)
        self.assertIn("examples/typescript-cli/source", readme)
        self.assertIn("趋势分析不是产品本体", readme)


if __name__ == "__main__":
    unittest.main()
