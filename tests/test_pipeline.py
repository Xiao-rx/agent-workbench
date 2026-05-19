import json
import os
import tempfile
import unittest
from pathlib import Path

from github_trend_lab.demo_data import sample_snapshot
from github_trend_lab.github_api import GitHubApiError
from github_trend_lab.models import StarSample
from github_trend_lab.pipeline import run_live_cycle
from github_trend_lab.storage import append_jsonl, star_history_path


class FailingTargetRepoClient:
    def search_repositories(self, *, since, top, min_stars):
        return sample_snapshot(since=since)

    def get_repository(self, full_name):
        raise GitHubApiError("target repo unavailable")


class PipelineTests(unittest.TestCase):
    def test_live_cycle_preserves_existing_star_history_when_target_sample_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_cwd = Path.cwd()
            os.chdir(tmp)
            try:
                history_path = star_history_path("owner/repo")
                append_jsonl(
                    history_path,
                    StarSample(
                        timestamp="2026-01-01T00:00:00Z",
                        full_name="owner/repo",
                        stars=7,
                        forks=1,
                        open_issues=0,
                        html_url="https://github.com/owner/repo",
                    ).to_dict(),
                )

                result = run_live_cycle(
                    client=FailingTargetRepoClient(),
                    target_repo="owner/repo",
                    since="2026-01-01",
                    top=5,
                    min_stars=10,
                    output=Path("reports/daily-brief.md"),
                    snapshot_output=Path("data/snapshots/live.json"),
                    decisions_output=Path("reports/daily-decisions.json"),
                )

                decisions = json.loads(Path("reports/daily-decisions.json").read_text(encoding="utf-8"))
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(result.star_history_path, Path("data/star_history/owner__repo.jsonl"))
        self.assertIn("Samples seen: 1", result.report)
        self.assertEqual(decisions["git_observation"]["current_stars"], 7)
        self.assertEqual(decisions["git_observation"]["samples_seen"], 1)


if __name__ == "__main__":
    unittest.main()
