import unittest
from pathlib import Path


class CiWorkflowTests(unittest.TestCase):
    def test_ci_validates_strict_demo_proof(self):
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

        self.assertIn(
            "agent-workbench demo --output /tmp/agent-workbench-demo --proof /tmp/agent-workbench-demo/proof.json",
            workflow,
        )
        self.assertIn(
            "agent-workbench demo --output /tmp/agent-workbench-demo-report --report /tmp/agent-workbench-demo-report/demo-report.md",
            workflow,
        )
        self.assertIn("test -f /tmp/agent-workbench-demo-report/demo-report.md", workflow)
        self.assertIn("grep -q \"Agent Workbench Demo Report\" /tmp/agent-workbench-demo-report/demo-report.md", workflow)
        self.assertIn("grep -q \"Status: ready (10 pass, 0 warn, 0 fail)\" /tmp/agent-workbench-demo-report/demo-report.md", workflow)
        self.assertIn('proof["kind"] != "agent_workbench.proof" or proof["schema_version"] != 1', workflow)
        self.assertIn('proof["readiness"]["status"] != "ready"', workflow)
        self.assertIn('proof["readiness"]["counts"] != {"pass": 10, "warn": 0, "fail": 0}', workflow)
        self.assertIn('proof["handoff"]["next_action"] != proof["next_action"]', workflow)
        self.assertIn('not proof["handoff"]["agents_md"].endswith("AGENTS.md")', workflow)
        self.assertIn('not proof["handoff"]["task_pack"].endswith("agent-task-pack.md")', workflow)
        self.assertIn('len(proof["artifact_summary"]["adapter_files"]) != 4', workflow)
        self.assertIn('"--adapter all --strict --format json" not in proof["readiness_command"]', workflow)
        self.assertIn('proof["readiness_args"][:2] != ["agent-workbench", "check"]', workflow)
        self.assertIn('proof["readiness_args"][-2:] != ["--format", "json"]', workflow)


if __name__ == "__main__":
    unittest.main()
