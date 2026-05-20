import unittest
from pathlib import Path


class IssueTemplateTests(unittest.TestCase):
    def test_agent_workbench_report_issue_form_collects_sanitized_feedback(self):
        text = Path(".github/ISSUE_TEMPLATE/agent-workbench-report.yml").read_text(encoding="utf-8")

        self.assertIn("Agent Workbench report", text)
        self.assertIn("agent-workbench demo --report", text)
        self.assertIn("agent-workbench init --report", text)
        self.assertIn("Paste only sanitized output", text)
        self.assertIn("Do not include tokens", text)
        self.assertIn("`.env.local`", text)
        self.assertIn("`.env.bak`", text)
        self.assertIn("Status: ready", text)
        self.assertIn("What worked, what was confusing", text)
        self.assertIn("I removed tokens", text)


if __name__ == "__main__":
    unittest.main()
