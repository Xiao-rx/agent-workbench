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
        )

        backlog = BuilderStrategist().propose(analysis, "owner/repo", feedback)

        feedback_item = backlog[-1]
        self.assertEqual(feedback_item.signal, "target-feedback:flat")
        self.assertIn("flat or negative (-1)", feedback_item.rationale)
        self.assertIn("owner/repo", feedback_item.title)

    def test_git_steward_handles_missing_history(self):
        from github_trend_lab.agents import GitSteward

        observation = GitSteward().observe("owner/repo", (), "## main\n?? README.md")

        self.assertIsNone(observation.current_stars)
        self.assertIn("publish the repo", observation.recommendation)

    def test_review_guardian_flags_empty_snapshot(self):
        snapshot = sample_snapshot()
        empty_snapshot = type(snapshot)(generated_at=snapshot.generated_at, since=snapshot.since, query=snapshot.query, repos=())
        analysis = HotnessAnalyst().analyze(empty_snapshot)
        backlog = BuilderStrategist().propose(analysis)

        findings = ReviewGuardian().review(backlog, empty_snapshot)

        self.assertEqual(findings[0].severity, "high")


if __name__ == "__main__":
    unittest.main()
