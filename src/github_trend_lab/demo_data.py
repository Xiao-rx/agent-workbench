from __future__ import annotations

from .models import RepoSignal, TrendSnapshot, utc_now_iso


def sample_snapshot(since: str = "2026-01-01") -> TrendSnapshot:
    repos = (
        RepoSignal(
            full_name="example/agent-workbench",
            html_url="https://github.com/example/agent-workbench",
            description="Local AI agent workflow automation tool",
            stars=48200,
            forks=2100,
            open_issues=88,
            language="Python",
            topics=("ai", "agent", "automation", "workflow"),
            created_at=f"{since}T00:00:00Z",
            updated_at=utc_now_iso(),
            pushed_at=utc_now_iso(),
            owner_type="Organization",
            license_name="MIT",
        ),
        RepoSignal(
            full_name="example/fast-cli-kit",
            html_url="https://github.com/example/fast-cli-kit",
            description="Simple dev CLI for shipping internal tools fast",
            stars=31500,
            forks=870,
            open_issues=24,
            language="Go",
            topics=("cli", "devtools", "automation"),
            created_at=f"{since}T00:00:00Z",
            updated_at=utc_now_iso(),
            pushed_at=utc_now_iso(),
            owner_type="User",
            license_name="Apache-2.0",
        ),
        RepoSignal(
            full_name="example/local-data-ui",
            html_url="https://github.com/example/local-data-ui",
            description="Open local data app with fast UI and no cloud lock-in",
            stars=22800,
            forks=640,
            open_issues=31,
            language="TypeScript",
            topics=("data", "ui", "local-first", "app"),
            created_at=f"{since}T00:00:00Z",
            updated_at=utc_now_iso(),
            pushed_at=utc_now_iso(),
            owner_type="Organization",
            license_name="MIT",
        ),
    )
    return TrendSnapshot(
        generated_at=utc_now_iso(),
        since=since,
        query=f"created:>={since} stars:>=10 archived:false fork:false",
        repos=repos,
    )
