from datetime import date
import unittest

from github_trend_lab.github_api import GitHubClient


class RecordingClient(GitHubClient):
    def __init__(self):
        super().__init__(token=None)
        self.last_params = {}

    def _get_json(self, path, params=None):
        self.last_params = params or {}
        return {"items": []}


class GitHubApiTests(unittest.TestCase):
    def test_daily_search_uses_half_open_date_window(self):
        client = RecordingClient()

        client.search_repositories_between(day=date(2026, 1, 1), top=5, min_stars=0)

        query = client.last_params["q"]
        self.assertIn("created:>=2026-01-01", query)
        self.assertIn("created:<2026-01-02", query)
        self.assertEqual(client.last_params["sort"], "stars")
        self.assertEqual(client.last_params["order"], "desc")
        self.assertEqual(client.last_params["per_page"], 5)


if __name__ == "__main__":
    unittest.main()
