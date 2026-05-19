import tempfile
import unittest
from pathlib import Path

from github_trend_lab.models import RepoSignal, StarSample, TrendSnapshot
from github_trend_lab.storage import append_jsonl, read_snapshot, read_star_history, slugify, write_snapshot


class ModelAndStorageTests(unittest.TestCase):
    def test_repo_signal_from_github_payload(self):
        payload = {
            "full_name": "owner/repo",
            "html_url": "https://github.com/owner/repo",
            "description": "A fast local tool",
            "stargazers_count": 42,
            "forks_count": 5,
            "open_issues_count": 2,
            "language": "Python",
            "topics": ["cli", "automation"],
            "owner": {"type": "User"},
            "license": {"spdx_id": "MIT"},
        }

        signal = RepoSignal.from_github(payload)

        self.assertEqual(signal.full_name, "owner/repo")
        self.assertEqual(signal.stars, 42)
        self.assertEqual(signal.topics, ("cli", "automation"))
        self.assertEqual(signal.license_name, "MIT")

    def test_snapshot_round_trip(self):
        signal = RepoSignal(
            full_name="owner/repo",
            html_url="https://github.com/owner/repo",
            description="Tool",
            stars=1,
            forks=0,
            open_issues=0,
            language="Python",
        )
        snapshot = TrendSnapshot(generated_at="2026-01-01T00:00:00Z", since="2026-01-01", query="stars:>=1", repos=(signal,))

        with tempfile.TemporaryDirectory() as tmp:
            path = write_snapshot(snapshot, Path(tmp) / "snapshot.json")
            loaded = read_snapshot(path)

        self.assertEqual(loaded.repos[0].full_name, "owner/repo")
        self.assertEqual(loaded.repos[0].topics, ())

    def test_star_history_round_trip(self):
        sample = StarSample(
            timestamp="2026-01-01T00:00:00Z",
            full_name="owner/repo",
            stars=10,
            forks=1,
            open_issues=0,
            html_url="https://github.com/owner/repo",
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            append_jsonl(path, sample.to_dict())
            history = read_star_history(path)

        self.assertEqual(history[0].stars, 10)

    def test_slugify_keeps_safe_names(self):
        self.assertEqual(slugify("owner/repo name"), "owner-repo-name")


if __name__ == "__main__":
    unittest.main()
