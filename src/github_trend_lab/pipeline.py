from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .agents import BuilderStrategist, GitSteward, HotnessAnalyst, ReviewGuardian
from .demo_data import sample_snapshot
from .github_api import GitHubApiError, GitHubClient
from .git_ops import git_status, latest_commit_subject
from .models import StarSample, TrendSnapshot
from .reporting import render_report
from .storage import append_jsonl, read_star_history, star_history_path, write_json, write_snapshot


@dataclass(frozen=True)
class PipelineResult:
    snapshot_path: Path
    report_path: Path
    star_history_path: Path | None
    report: str


def run_analysis(snapshot: TrendSnapshot, target_repo: str | None = None, history: tuple[StarSample, ...] = ()) -> tuple[str, dict[str, object]]:
    analyst = HotnessAnalyst()
    builder = BuilderStrategist()
    reviewer = ReviewGuardian()

    analysis = analyst.analyze(snapshot)
    backlog = builder.propose(analysis, target_repo)
    findings = reviewer.review(backlog, snapshot)

    git_observation = None
    if target_repo:
        git_observation = GitSteward().observe(target_repo, history, git_status(), latest_commit_subject())

    report = render_report(
        snapshot=snapshot,
        analysis=analysis,
        backlog=backlog,
        findings=findings,
        git_observation=git_observation,
        star_sample=history[-1] if history else None,
    )
    decision_payload = {
        "analysis": analysis,
        "backlog": backlog,
        "review_findings": findings,
        "git_observation": git_observation,
    }
    return report, decision_payload


def run_live_cycle(
    *,
    client: GitHubClient,
    target_repo: str | None,
    since: str,
    top: int,
    min_stars: int,
    output: Path,
    snapshot_output: Path | None = None,
    decisions_output: Path | None = None,
) -> PipelineResult:
    snapshot = client.search_repositories(since=since, top=top, min_stars=min_stars)
    snapshot_path = write_snapshot(snapshot, snapshot_output)

    history_path = None
    history: tuple[StarSample, ...] = ()
    if target_repo:
        try:
            repo = client.get_repository(target_repo)
            sample = StarSample.from_repo(repo)
            history_path = star_history_path(target_repo)
            append_jsonl(history_path, sample.to_dict())
            history = tuple(read_star_history(history_path))
        except GitHubApiError:
            history_path = star_history_path(target_repo)
            history = tuple(read_star_history(history_path))

    report, decisions = run_analysis(snapshot, target_repo, history)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    if decisions_output:
        write_json(decisions_output, decisions)

    return PipelineResult(snapshot_path=snapshot_path, report_path=output, star_history_path=history_path, report=report)


def run_demo_cycle(output: Path, since: str = "2026-01-01") -> PipelineResult:
    snapshot = sample_snapshot(since=since)
    snapshot_path = write_snapshot(snapshot, Path("data/snapshots/demo-latest.json"))
    report, decisions = run_analysis(snapshot)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    write_json(Path("reports/demo-decisions.json"), decisions)
    return PipelineResult(snapshot_path=snapshot_path, report_path=output, star_history_path=None, report=report)
