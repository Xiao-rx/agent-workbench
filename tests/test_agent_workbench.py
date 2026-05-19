import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path

from agent_workbench import __version__
from agent_workbench.checks import check_workbench, readiness_payload
from agent_workbench.cli import main
from agent_workbench.generator import render_agents_md, render_task_pack, write_workbench
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

    def test_write_workbench_outputs_optional_adapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "out"
            root.mkdir()
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            paths = write_workbench(root, out, "demo", ("claude", "cursor"))

            self.assertEqual(len(paths), 4)
            self.assertTrue((out / "CLAUDE.md").exists())
            self.assertTrue((out / ".cursor" / "rules" / "agent-workbench.md").exists())
            self.assertIn("Read `AGENTS.md` first", (out / "CLAUDE.md").read_text(encoding="utf-8"))
            self.assertIn(".agent-workbench/AGENTS.md", (out / ".cursor" / "rules" / "agent-workbench.md").read_text(encoding="utf-8"))

    def test_check_workbench_reports_ready_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = root / ".agent-workbench"
            root.mkdir()
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            write_workbench(root, out, "demo")

            report = check_workbench(root)
            payload = readiness_payload(report)

        self.assertTrue(report.ready)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(any(check.name == "verification commands" and check.status == "pass" for check in report.checks))

    def test_check_workbench_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            report = check_workbench(root)

        self.assertFalse(report.ready)
        self.assertTrue(any(check.name == "AGENTS.md" and check.status == "fail" for check in report.checks))
        self.assertTrue(any(check.name == "agent-task-pack.md" and check.status == "fail" for check in report.checks))

    def test_render_task_pack_contains_repo_specific_kickoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("def test_demo():\n    assert True\n", encoding="utf-8")
            repo = scan_repo(root)

        output = render_task_pack(repo, "demo")

        self.assertIn("## Kickoff Prompt", output)
        self.assertIn("## Verification Commands", output)
        self.assertIn("python -m unittest discover -s tests", output)
        self.assertIn("## High-Signal Files", output)
        self.assertIn("tests/test_demo.py", output)
        self.assertIn("Acceptance Gate", output)

    def test_render_task_pack_prioritizes_product_entry_points(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            product = root / "src" / "agent_workbench"
            product.mkdir(parents=True)
            (product / "cli.py").write_text("print('agent workbench')\n", encoding="utf-8")
            internal = root / "src" / "github_trend_lab"
            internal.mkdir(parents=True)
            (internal / "agents.py").write_text("\n".join("x = 1" for _ in range(200)), encoding="utf-8")
            repo = scan_repo(root)

        output = render_task_pack(repo, "demo")

        self.assertIn("inspect `README.md`", output)
        self.assertLess(output.index("README.md"), output.index("src/github_trend_lab/agents.py"))

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

    def test_scan_command_can_emit_json_repo_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "app.py").write_text("print('hello')\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["scan", str(root), "--format", "json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["total_files"], 2)
        self.assertEqual(payload["package_managers"], ["python/pyproject"])
        self.assertIn("python -m unittest discover -s tests", payload["test_commands"])
        self.assertEqual(payload["files"][0]["path"], "app.py")

    def test_scan_command_can_write_json_repo_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "reports" / "repo-map.json"
            root.mkdir()
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "app.py").write_text("print('hello')\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["scan", str(root), "--format", "json", "--output-json", str(out)])

            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertTrue(out.exists())
            self.assertIn("Wrote", stdout.getvalue())
            self.assertEqual(payload["package_managers"], ["python/pyproject"])

    def test_check_command_can_emit_json_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            write_workbench(root, root / ".agent-workbench", "demo")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["check", str(root), "--format", "json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["ready"])
        self.assertTrue(any(check["name"] == "AGENTS.md" for check in payload["checks"]))

    def test_check_command_can_write_json_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "reports" / "readiness.json"
            root.mkdir()
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            write_workbench(root, root / ".agent-workbench", "demo")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["check", str(root), "--format", "json", "--output-json", str(out)])

            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertTrue(out.exists())
            self.assertIn("Wrote", stdout.getvalue())
            self.assertEqual(payload["status"], "ready")

    def test_output_json_requires_json_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                main(["scan", str(root), "--output-json", str(root / "repo-map.json")])

        self.assertEqual(raised.exception.code, 2)

    def test_check_command_returns_nonzero_for_missing_workbench(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["check", str(root)])

        self.assertEqual(exit_code, 1)
        self.assertIn("status=not_ready", stdout.getvalue())
        self.assertIn("Missing", stdout.getvalue())

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

    def test_demo_command_can_check_generated_workbench(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "demo"

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["demo", "--output", str(output), "--check"])

            self.assertEqual(exit_code, 0)
            self.assertIn("status=ready", stdout.getvalue())
            self.assertIn("PASS AGENTS.md", stdout.getvalue())

    def test_demo_command_writes_requested_adapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "demo"

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["demo", "--output", str(output), "--adapter", "claude", "--adapter", "cursor"])

            self.assertEqual(exit_code, 0)
            self.assertTrue((output / ".agent-workbench" / "CLAUDE.md").exists())
            self.assertTrue((output / ".agent-workbench" / ".cursor" / "rules" / "agent-workbench.md").exists())
            self.assertIn("CLAUDE.md", stdout.getvalue())
            self.assertIn("agent-workbench.md", stdout.getvalue())

    def test_init_command_writes_requested_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "out"
            root.mkdir()
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["init", str(root), "--output", str(out), "--adapter", "claude"])

            self.assertEqual(exit_code, 0)
            self.assertTrue((out / "CLAUDE.md").exists())
            self.assertIn("CLAUDE.md", stdout.getvalue())

    def test_init_command_can_check_generated_workbench(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "out"
            root.mkdir()
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["init", str(root), "--output", str(out), "--check"])

            self.assertEqual(exit_code, 0)
            self.assertTrue((out / "AGENTS.md").exists())
            self.assertIn("status=ready", stdout.getvalue())
            self.assertIn("PASS verification commands", stdout.getvalue())

    def test_version_flag_prints_package_version(self):
        stdout = StringIO()
        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn(f"agent-workbench {__version__}", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
