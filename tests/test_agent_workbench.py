import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from agent_workbench.cli import main
from agent_workbench.generator import render_agents_md, write_workbench
from agent_workbench.scanner import scan_repo


class AgentWorkbenchTests(unittest.TestCase):
    def test_scan_repo_detects_python_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "app.py").write_text("print('hello')\n", encoding="utf-8")
            (root / ".env.local").write_text("TOKEN=secret\n", encoding="utf-8")

            repo = scan_repo(root)

        self.assertIn("python/pyproject", repo.package_managers)
        self.assertIn("python -m unittest discover -s tests", repo.test_commands)
        self.assertTrue(any(".env.local exists" in note for note in repo.risk_notes))

    def test_render_agents_md_contains_safe_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "main.py").write_text("x = 1\n", encoding="utf-8")
            repo = scan_repo(root)

        output = render_agents_md(repo, "demo")

        self.assertIn("# AGENTS.md for demo", output)
        self.assertIn("python -m unittest discover -s tests", output)
        self.assertIn("High-Signal Files", output)

    def test_write_workbench_outputs_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "out"
            root.mkdir()
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            agents_path, tasks_path = write_workbench(root, out, "demo")

            self.assertTrue(agents_path.exists())
            self.assertTrue(tasks_path.exists())

    def test_scan_repo_skips_local_agent_workbench_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            for dirname in (".agent-workbench", ".agents", ".omx"):
                artifact_dir = root / dirname
                artifact_dir.mkdir()
                (artifact_dir / "notes.md").write_text("local agent artifact\n", encoding="utf-8")

            repo = scan_repo(root)

        scanned_paths = {file.path for file in repo.files}
        self.assertIn("pyproject.toml", scanned_paths)
        self.assertNotIn(".agent-workbench/notes.md", scanned_paths)
        self.assertNotIn(".agents/notes.md", scanned_paths)
        self.assertNotIn(".omx/notes.md", scanned_paths)

    def test_scan_repo_respects_simple_gitignore_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gitignore").write_text("handoff.md\nreports/demo-*.json\n.env.*\n!.env.example\n", encoding="utf-8")
            (root / "handoff.md").write_text("local context\n", encoding="utf-8")
            (root / ".env.local").write_text("TOKEN=secret\n", encoding="utf-8")
            (root / ".env.example").write_text("TOKEN=<your-token>\n", encoding="utf-8")
            reports = root / "reports"
            reports.mkdir()
            (reports / "demo-decisions.json").write_text("{}\n", encoding="utf-8")
            (reports / "daily-brief.md").write_text("# Brief\n", encoding="utf-8")

            repo = scan_repo(root)

        scanned_paths = {file.path for file in repo.files}
        self.assertNotIn("handoff.md", scanned_paths)
        self.assertNotIn(".env.local", scanned_paths)
        self.assertNotIn("reports/demo-decisions.json", scanned_paths)
        self.assertIn(".env.example", scanned_paths)
        self.assertIn("reports/daily-brief.md", scanned_paths)

    def test_demo_command_writes_visible_workbench(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "demo"

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["demo", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((output / "sample-repo" / "pyproject.toml").exists())
            agents = (output / ".agent-workbench" / "AGENTS.md").read_text(encoding="utf-8")
            tasks = (output / ".agent-workbench" / "agent-task-pack.md").read_text(encoding="utf-8")
            self.assertIn("Demo repository:", stdout.getvalue())
            self.assertIn("agent-workbench-demo", agents)
            self.assertIn("python -m unittest discover -s tests", agents)
            self.assertIn("Agent Task Pack", tasks)


if __name__ == "__main__":
    unittest.main()
