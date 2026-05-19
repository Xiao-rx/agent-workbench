import unittest

from github_trend_lab.agents import BuilderStrategist, GitObservation, HotnessAnalyst, ReviewGuardian
from github_trend_lab.demo_data import sample_snapshot


class AgentTests(unittest.TestCase):
    def test_hotness_analysis_extracts_reusable_signals(self):
        analysis = HotnessAnalyst().analyze(sample_snapshot())

        self.assertIn("learning candidates analyzed", analysis.headline)
        self.assertEqual(analysis.leading_repositories[0], "example/agent-workbench")
        self.assertIn(("Python", 1), analysis.languages)
        self.assertTrue(any(topic == "automation" for topic, _count in analysis.topics))
        self.assertTrue(any("AI" in reason or "automation" in reason for reason in analysis.reasons))
        self.assertEqual(analysis.repo_lessons[0].full_name, "example/agent-workbench")
        self.assertGreaterEqual(analysis.repo_lessons[0].trust_score, 50)
        self.assertTrue(analysis.repo_lessons[0].emulate)

    def test_builder_produces_verifiable_backlog(self):
        analysis = HotnessAnalyst().analyze(sample_snapshot())
        backlog = BuilderStrategist().propose(analysis, "owner/repo")

        self.assertGreaterEqual(len(backlog), 4)
        self.assertTrue(all(item.verification for item in backlog))
        self.assertTrue(any("owner/repo" in item.title for item in backlog))
        self.assertEqual(backlog[0].signal, "topic:automation (2)")
        self.assertIn("topic:automation", backlog[0].rationale)
        self.assertTrue(any(item.signal == "topic:data-ui" for item in backlog))

    def test_builder_uses_target_feedback_when_available(self):
        analysis = HotnessAnalyst().analyze(sample_snapshot())
        feedback = GitObservation(
            repo="owner/repo",
            current_stars=42,
            star_delta=-1,
            samples_seen=2,
            git_status="M src/github_trend_lab/agents.py",
            recommendation="Commit small, explainable improvements and watch the next star sample for response.",
            recent_change="Print proof summary in text output",
            next_sample_gate="After publishing Print proof summary in text output, compare the next star sample with 42 stars and local delta -1.",
        )

        backlog = BuilderStrategist().propose(analysis, "owner/repo", feedback)

        feedback_item = backlog[-1]
        self.assertEqual(feedback_item.signal, "target-feedback:flat")
        self.assertIn("flat or negative (-1)", feedback_item.rationale)
        self.assertIn("owner/repo", feedback_item.title)
        self.assertIn("following target repo star sample", feedback_item.verification)

    def test_git_steward_handles_missing_history(self):
        from github_trend_lab.agents import GitSteward

        observation = GitSteward().observe("owner/repo", (), "## main\n?? README.md", "Add launch proof")

        self.assertIsNone(observation.current_stars)
        self.assertIn("publish the repo", observation.recommendation)
        self.assertEqual(observation.recent_change, "Add launch proof")
        self.assertIn("capture the first star sample", observation.next_sample_gate)

    def test_git_steward_links_recent_change_to_next_sample(self):
        from github_trend_lab.agents import GitSteward
        from github_trend_lab.models import StarSample

        history = (
            StarSample(
                timestamp="2026-01-01T00:00:00Z",
                full_name="owner/repo",
                stars=2,
                forks=0,
                open_issues=0,
                html_url="https://github.com/owner/repo",
            ),
            StarSample(
                timestamp="2026-01-02T00:00:00Z",
                full_name="owner/repo",
                stars=3,
                forks=0,
                open_issues=0,
                html_url="https://github.com/owner/repo",
            ),
        )

        observation = GitSteward().observe("owner/repo", history, "## main", "Print proof summary in text output")

        self.assertEqual(observation.star_delta, 1)
        self.assertIn("Print proof summary in text output", observation.next_sample_gate)
        self.assertIn("3 stars", observation.next_sample_gate)

    def test_review_guardian_flags_empty_snapshot(self):
        snapshot = sample_snapshot()
        empty_snapshot = type(snapshot)(generated_at=snapshot.generated_at, since=snapshot.since, query=snapshot.query, repos=())
        analysis = HotnessAnalyst().analyze(empty_snapshot)
        backlog = BuilderStrategist().propose(analysis)

        findings = ReviewGuardian().review(backlog, empty_snapshot)

        self.assertEqual(findings[0].severity, "high")


if __name__ == "__main__":
    unittest.main()
