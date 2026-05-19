import unittest

from github_trend_lab.growth_loop import GrowthLoopResult


class GrowthLoopTests(unittest.TestCase):
    def test_growth_loop_result_shape(self):
        result = GrowthLoopResult(
            report_path=__import__("pathlib").Path("reports/daily-brief.md"),
            verification_path=__import__("pathlib").Path("reports/local-verification.md"),
            snapshot_path=__import__("pathlib").Path("data/snapshots/trend-product-live.json"),
            ok=True,
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.report_path.name, "daily-brief.md")


if __name__ == "__main__":
    unittest.main()
