from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import default_since, read_config
from .github_api import GitHubClient
from .pipeline import run_live_cycle
from .verification import has_failures, render_check_report, run_local_checks


@dataclass(frozen=True)
class GrowthLoopResult:
    report_path: Path
    verification_path: Path
    snapshot_path: Path
    ok: bool


def run_growth_loop(
    *,
    product_repo: str,
    since: str | None = None,
    top: int = 12,
    min_stars: int = 50,
    report_path: Path = Path("reports/daily-brief.md"),
    verification_path: Path = Path("reports/local-verification.md"),
    snapshot_path: Path = Path("data/snapshots/trend-product-live.json"),
) -> GrowthLoopResult:
    config = read_config()
    client = GitHubClient(token=config.github_token, api_version=config.api_version)
    result = run_live_cycle(
        client=client,
        target_repo=product_repo,
        since=since or default_since(),
        top=top,
        min_stars=min_stars,
        output=report_path,
        snapshot_output=snapshot_path,
        decisions_output=Path("reports/daily-decisions.json"),
    )
    checks = run_local_checks()
    verification_path.parent.mkdir(parents=True, exist_ok=True)
    verification_path.write_text(render_check_report(checks), encoding="utf-8")
    return GrowthLoopResult(
        report_path=result.report_path,
        verification_path=verification_path,
        snapshot_path=result.snapshot_path,
        ok=not has_failures(checks),
    )
