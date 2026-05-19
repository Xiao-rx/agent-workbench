from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from .github_api import GitHubClient
from .models import TrendSnapshot
from .storage import daily_snapshot_path, read_json, write_snapshot


def iter_days(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def collect_daily_rankings(
    *,
    client: GitHubClient,
    start: date,
    end: date,
    top: int,
    min_stars: int,
    output_dir: Path = Path("data/snapshots"),
    resume: bool = True,
) -> tuple[Path, ...]:
    paths: list[Path] = []
    for day in iter_days(start, end):
        path = output_dir / daily_snapshot_path(day.isoformat()).name
        if resume and path.exists():
            paths.append(path)
            continue
        snapshot = client.search_repositories_between(day=day, top=top, min_stars=min_stars)
        write_snapshot(snapshot, path)
        paths.append(path)
    return tuple(paths)


def load_many_snapshots(paths: tuple[Path, ...]) -> TrendSnapshot:
    repos = []
    first_since = ""
    generated_at = ""
    queries = []
    for path in paths:
        payload = read_json(path)
        snapshot = TrendSnapshot.from_dict(payload)
        if not first_since:
            first_since = snapshot.since
        generated_at = snapshot.generated_at
        queries.append(snapshot.query)
        repos.extend(snapshot.repos)
    return TrendSnapshot(
        generated_at=generated_at,
        since=first_since,
        query=f"{len(paths)} daily ranking snapshots",
        repos=tuple(repos),
    )
