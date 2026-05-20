import unittest
from pathlib import Path


class EnvExampleTests(unittest.TestCase):
    def test_env_example_is_placeholder_only_and_documents_optional_credentials(self):
        text = Path(".env.example").read_text(encoding="utf-8")

        self.assertIn("Agent Workbench itself does not need a token.", text)
        self.assertIn("Never commit .env.local", text)
        self.assertIn("GITHUB_TOKEN=", text)
        self.assertIn("GH_TOKEN=", text)
        self.assertIn("TARGET_REPO=OWNER/agent-workbench", text)
        self.assertIn("GITHUB_API_VERSION=2026-03-10", text)
        self.assertNotIn("github_pat_", text)
        self.assertNotIn("ghp_", text)

    def test_gitignore_keeps_local_env_files_ignored_but_tracks_example(self):
        text = Path(".gitignore").read_text(encoding="utf-8")

        self.assertIn(".env.*", text)
        self.assertIn("!.env.example", text)


if __name__ == "__main__":
    unittest.main()
