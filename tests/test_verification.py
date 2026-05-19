import tempfile
import unittest
from pathlib import Path

from github_trend_lab.verification import CheckResult, has_failures, render_check_report, run_secret_scan


class VerificationTests(unittest.TestCase):
    def test_render_check_report(self):
        report = render_check_report((CheckResult("thing", True, "ok"), CheckResult("other", False, "bad")))

        self.assertIn("PASS: thing", report)
        self.assertIn("FAIL: other", report)

    def test_has_failures(self):
        self.assertFalse(has_failures((CheckResult("thing", True, "ok"),)))
        self.assertTrue(has_failures((CheckResult("thing", False, "bad"),)))

    def test_secret_scan_reports_location_without_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            leaked = "github_pat_" + ("A" * 30)
            (root / "notes.txt").write_text(f"token={leaked}\n", encoding="utf-8")

            check = run_secret_scan(root)

            self.assertFalse(check.ok)
            self.assertIn("notes.txt:1", check.detail)
            self.assertNotIn(leaked, check.detail)

    def test_secret_scan_ignores_local_env_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local_token = "ghp_" + ("a" * 30)
            (root / ".env.local").write_text(f"GITHUB_TOKEN={local_token}\n", encoding="utf-8")
            (root / ".env.example").write_text("GITHUB_TOKEN=<your-token>\n", encoding="utf-8")

            check = run_secret_scan(root)

            self.assertTrue(check.ok)

    def test_secret_scan_allows_token_variable_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "client.py").write_text("client = GitHubClient(token=config.github_token)\n", encoding="utf-8")

            check = run_secret_scan(root)

            self.assertTrue(check.ok)

    def test_secret_scan_flags_hardcoded_sensitive_assignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_secret = "".join(("Abcdef", "1234567890"))
            (root / "settings.py").write_text(f'api_key = "{fake_secret}"\n', encoding="utf-8")

            check = run_secret_scan(root)

            self.assertFalse(check.ok)
            self.assertIn("settings.py:1", check.detail)


if __name__ == "__main__":
    unittest.main()
