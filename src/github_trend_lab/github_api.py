from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import RepoSignal, TrendSnapshot, utc_now_iso


class GitHubApiError(RuntimeError):
    """Raised when GitHub returns an error or cannot be reached."""


@dataclass(frozen=True)
class GitHubClient:
    token: str | None = None
    api_version: str = "2026-03-10"
    base_url: str = "https://api.github.com"
    timeout_seconds: int = 30

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-trend-lab",
            "X-GitHub-Api-Version": self.api_version,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        request = Request(url, headers=self._headers())

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubApiError(f"GitHub API returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise GitHubApiError(f"Could not reach GitHub API: {exc.reason}") from exc

    def search_repositories(
        self,
        *,
        since: str,
        top: int,
        min_stars: int = 10,
        language: str | None = None,
        topic: str | None = None,
        query_extra: str | None = None,
    ) -> TrendSnapshot:
        query_parts = [
            f"created:>={since}",
            f"stars:>={min_stars}",
            "archived:false",
            "fork:false",
        ]
        if language:
            query_parts.append(f"language:{language}")
        if topic:
            query_parts.append(f"topic:{topic}")
        if query_extra:
            query_parts.append(query_extra)

        query = " ".join(query_parts)
        payload = self._get_json(
            "/search/repositories",
            {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": max(1, min(top, 100)),
            },
        )
        repos = tuple(RepoSignal.from_github(item) for item in payload.get("items", []))
        return TrendSnapshot(generated_at=utc_now_iso(), since=since, query=query, repos=repos)

    def search_repositories_between(
        self,
        *,
        day: date,
        top: int,
        min_stars: int = 0,
        language: str | None = None,
        topic: str | None = None,
    ) -> TrendSnapshot:
        next_day = day + timedelta(days=1)
        query_parts = [
            f"created:>={day.isoformat()}",
            f"created:<{next_day.isoformat()}",
            f"stars:>={min_stars}",
            "archived:false",
            "fork:false",
        ]
        if language:
            query_parts.append(f"language:{language}")
        if topic:
            query_parts.append(f"topic:{topic}")

        query = " ".join(query_parts)
        payload = self._get_json(
            "/search/repositories",
            {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": max(1, min(top, 100)),
            },
        )
        repos = tuple(RepoSignal.from_github(item) for item in payload.get("items", []))
        return TrendSnapshot(generated_at=utc_now_iso(), since=day.isoformat(), query=query, repos=repos)

    def get_repository(self, full_name: str) -> RepoSignal:
        if "/" not in full_name:
            raise ValueError("Repository must be in OWNER/REPO form.")
        owner, repo = full_name.split("/", 1)
        payload = self._get_json(f"/repos/{owner}/{repo}")
        return RepoSignal.from_github(payload)
