import unittest

from github_trend_lab.models import RepoSignal
from github_trend_lab.quality import is_learning_candidate, repo_risk_flags, risk_summary


class QualityTests(unittest.TestCase):
    def test_flags_keygen_style_repository(self):
        repo = RepoSignal(
            full_name="owner/product-keygen",
            html_url="https://github.com/owner/product-keygen",
            description="Patch activator license key pre-activated full version",
            stars=1000,
            forks=0,
            open_issues=0,
            language="C",
        )

        self.assertFalse(is_learning_candidate(repo))
        self.assertIn("keygen", repo_risk_flags(repo))
        self.assertIn("activator", repo_risk_flags(repo))

    def test_does_not_flag_model_substring_as_mod(self):
        repo = RepoSignal(
            full_name="owner/smallcode",
            html_url="https://github.com/owner/smallcode",
            description="AI coding agent optimized for small LLMs. 87% benchmark with 4B-active model.",
            stars=1000,
            forks=0,
            open_issues=0,
            language="JavaScript",
        )

        self.assertTrue(is_learning_candidate(repo))
        self.assertEqual(repo_risk_flags(repo), ())

    def test_single_weak_term_is_watch_not_block(self):
        repo = RepoSignal(
            full_name="owner/model-loader",
            html_url="https://github.com/owner/model-loader",
            description="A loader for local model weights",
            stars=1000,
            forks=100,
            open_issues=4,
            language="Python",
        )

        self.assertTrue(is_learning_candidate(repo))
        self.assertIn("loader", repo_risk_flags(repo))
        self.assertTrue(risk_summary(repo).startswith("watch:"))

    def test_hyphenated_license_key_variant_is_blocked(self):
        repo = RepoSignal(
            full_name="owner/free-product",
            html_url="https://github.com/owner/free-product",
            description="License-key activation unlocker and serial download",
            stars=1000,
            forks=0,
            open_issues=0,
            language="C",
        )

        self.assertFalse(is_learning_candidate(repo))
        self.assertIn("license key", repo_risk_flags(repo))
        self.assertIn("activation", repo_risk_flags(repo))


if __name__ == "__main__":
    unittest.main()
