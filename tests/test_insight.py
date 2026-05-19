import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from github_trend_lab.cli import main
from github_trend_lab.insight import build_insight, render_insight_text


class InsightTests(unittest.TestCase):
    def test_build_insight_summarizes_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "daily-decisions.json"
            decisions.write_text(json.dumps(_decisions_payload()), encoding="utf-8")

            insight = build_insight(decisions)

        self.assertEqual(insight["top_signal"], "topic:agent-skill (2)")
        self.assertEqual(insight["next_product_move"]["title"], "Ship proof path")
        self.assertEqual(insight["target_feedback"]["star_delta"], 0)
        self.assertEqual(insight["risk_summary"]["highest_severity"], "medium")

    def test_render_insight_text_is_compact(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "daily-decisions.json"
            decisions.write_text(json.dumps(_decisions_payload()), encoding="utf-8")

            text = render_insight_text(build_insight(decisions))

        self.assertIn("Trend Insight", text)
        self.assertIn("top_signal=topic:agent-skill (2)", text)
        self.assertIn("next=Ship proof path", text)
        self.assertIn("stars=0", text)
        self.assertIn("highest_risk=medium: Risky repositories", text)

    def test_cli_insight_outputs_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "daily-decisions.json"
            decisions.write_text(json.dumps(_decisions_payload()), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["insight", "--decisions", str(decisions)])

        self.assertEqual(exit_code, 0)
        self.assertIn("recent_change=Add proof line", stdout.getvalue())

    def test_cli_insight_can_emit_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "daily-decisions.json"
            output = Path(tmp) / "insight.json"
            decisions.write_text(json.dumps(_decisions_payload()), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["insight", "--decisions", str(decisions), "--format", "json", "--output-json", str(output)])

            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["next_product_move"]["verification"], "Run the demo.")
        self.assertIn("Wrote insight", stdout.getvalue())

    def test_cli_insight_output_json_requires_json_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "daily-decisions.json"
            decisions.write_text(json.dumps(_decisions_payload()), encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                main(["insight", "--decisions", str(decisions), "--output-json", str(Path(tmp) / "insight.json")])

        self.assertEqual(raised.exception.code, 2)

    def test_insight_accepts_utf8_bom_decision_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "daily-decisions.json"
            decisions.write_text(json.dumps(_decisions_payload()), encoding="utf-8-sig")

            insight = build_insight(decisions)

        self.assertEqual(insight["top_signal"], "topic:agent-skill (2)")


def _decisions_payload():
    return {
        "analysis": {
            "headline": "Two learning candidates; top signal is topic:agent-skill.",
            "topics": [["agent-skill", 2]],
            "description_terms": [["agent", 3]],
            "languages": [["Python", 1]],
        },
        "backlog": [
            {
                "title": "Ship proof path",
                "impact": "high",
                "effort": "low",
                "verification": "Run the demo.",
            }
        ],
        "review_findings": [
            {
                "severity": "medium",
                "title": "Risky repositories",
            }
        ],
        "git_observation": {
            "repo": "owner/repo",
            "current_stars": 0,
            "star_delta": 0,
            "samples_seen": 2,
            "recent_change": "Add proof line",
            "next_sample_gate": "Capture the next sample.",
        },
    }


if __name__ == "__main__":
    unittest.main()
