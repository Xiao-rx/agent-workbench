import unittest

from github_trend_lab.agents import BuilderStrategist, GitObservation, HotnessAnalyst, ReviewGuardian
from github_trend_lab.demo_data import sample_snapshot
from github_trend_lab.models import RepoSignal, TrendSnapshot
from github_trend_lab.reporting import render_report


class ReportingTests(unittest.TestCase):
    def test_report_contains_all_agent_sections(self):
        snapshot = sample_snapshot()
        analysis = HotnessAnalyst().analyze(snapshot)
        backlog = BuilderStrategist().propose(analysis, "owner/repo")
        findings = ReviewGuardian().review(backlog, snapshot)

        report = render_report(snapshot=snapshot, analysis=analysis, backlog=backlog, findings=findings)

        self.assertIn("# GitHub Trend Lab Daily Brief", report)
        self.assertIn("## Hotness Analyst", report)
        self.assertIn("## Builder Strategist", report)
        self.assertIn("## Review Guardian", report)
        self.assertIn("example/agent\\-workbench", report)
        self.assertIn("- Signal: topic:automation \\(2\\)", report)
        self.assertIn("Per-repository lessons", report)
        self.assertIn("Why popular:", report)

    def test_report_adds_target_feedback_recommendation(self):
        snapshot = sample_snapshot()
        analysis = HotnessAnalyst().analyze(snapshot)
        backlog = BuilderStrategist().propose(analysis, "owner/repo")
        findings = ReviewGuardian().review(backlog, snapshot)
        feedback = GitObservation(
            repo="owner/repo",
            current_stars=43,
            star_delta=3,
            samples_seen=2,
            git_status="nothing to commit, working tree clean",
            recommendation="Working tree is clean; prefer collecting another data point before changing code.",
            recent_change="Print proof summary in text output",
            next_sample_gate="After publishing Print proof summary in text output, compare the next star sample with 43 stars and local delta 3.",
        )

        report = render_report(
            snapshot=snapshot,
            analysis=analysis,
            backlog=backlog,
            findings=findings,
            git_observation=feedback,
        )

        self.assertIn("Amplify the trend\\-backed momentum for owner/repo", report)
        self.assertIn("- Signal: target\\-feedback:growing", report)
        self.assertIn("Target repo feedback is positive \\(\\+3\\)", report)
        self.assertIn("## Feedback Loop Evidence", report)
        self.assertIn("Recent product change: Print proof summary in text output", report)
        self.assertIn("Next sample gate:", report)

    def test_report_escapes_untrusted_markdown(self):
        repo = RepoSignal(
            full_name="owner/[bad](https://evil.test)",
            html_url="https://evil.test/repo",
            description="hello\n![x](https://evil.test/pixel) <img src=x> `tick`",
            stars=5,
            forks=0,
            open_issues=0,
            language="Python",
        )
        snapshot = TrendSnapshot(
            generated_at="2026-01-01T00:00:00Z",
            since="2026-01-01",
            query="created:>=2026-01-01 `bad`",
            repos=(repo,),
        )
        analysis = HotnessAnalyst().analyze(snapshot)
        backlog = BuilderStrategist().propose(analysis)
        findings = ReviewGuardian().review(backlog, snapshot)

        report = render_report(snapshot=snapshot, analysis=analysis, backlog=backlog, findings=findings)

        self.assertNotIn("https://evil.test", report)
        self.assertIn("\\[bad\\]", report)
        self.assertIn("\\!\\[x\\]", report)
        self.assertIn("&lt;img src=x&gt;", report)

    def test_report_only_links_to_github_repo_homepage(self):
        repo = RepoSignal(
            full_name="owner/repo",
            html_url="https://github.com/owner/repo/issues/1?template=bug",
            description="Legitimate repo with a non-canonical link",
            stars=5,
            forks=0,
            open_issues=0,
            language="Python",
        )
        snapshot = TrendSnapshot(
            generated_at="2026-01-01T00:00:00Z",
            since="2026-01-01",
            query="created:>=2026-01-01",
            repos=(repo,),
        )
        analysis = HotnessAnalyst().analyze(snapshot)
        backlog = BuilderStrategist().propose(analysis)
        findings = ReviewGuardian().review(backlog, snapshot)

        report = render_report(snapshot=snapshot, analysis=analysis, backlog=backlog, findings=findings)

        self.assertIn("owner/repo", report)
        self.assertNotIn("](https://github.com/owner/repo/issues", report)


if __name__ == "__main__":
    unittest.main()
