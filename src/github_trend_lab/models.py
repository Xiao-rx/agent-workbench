from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RepoSignal:
    full_name: str
    html_url: str
    description: str
    stars: int
    forks: int
    open_issues: int
    language: str | None
    topics: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""
    updated_at: str = ""
    pushed_at: str = ""
    owner_type: str = ""
    license_name: str | None = None

    @classmethod
    def from_github(cls, payload: dict[str, Any]) -> "RepoSignal":
        owner = payload.get("owner") or {}
        license_payload = payload.get("license") or {}
        return cls(
            full_name=str(payload.get("full_name") or ""),
            html_url=str(payload.get("html_url") or ""),
            description=str(payload.get("description") or ""),
            stars=int(payload.get("stargazers_count") or 0),
            forks=int(payload.get("forks_count") or payload.get("forks") or 0),
            open_issues=int(payload.get("open_issues_count") or payload.get("open_issues") or 0),
            language=payload.get("language"),
            topics=tuple(str(topic) for topic in payload.get("topics") or ()),
            created_at=str(payload.get("created_at") or ""),
            updated_at=str(payload.get("updated_at") or ""),
            pushed_at=str(payload.get("pushed_at") or ""),
            owner_type=str(owner.get("type") or ""),
            license_name=license_payload.get("spdx_id") or license_payload.get("name"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "full_name": self.full_name,
            "html_url": self.html_url,
            "description": self.description,
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "language": self.language,
            "topics": list(self.topics),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "pushed_at": self.pushed_at,
            "owner_type": self.owner_type,
            "license_name": self.license_name,
        }


@dataclass(frozen=True)
class TrendSnapshot:
    generated_at: str
    since: str
    query: str
    repos: tuple[RepoSignal, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TrendSnapshot":
        return cls(
            generated_at=str(payload["generated_at"]),
            since=str(payload["since"]),
            query=str(payload["query"]),
            repos=tuple(_repo_from_stored(repo) for repo in payload["repos"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "since": self.since,
            "query": self.query,
            "repos": [repo.to_dict() for repo in self.repos],
        }


@dataclass(frozen=True)
class StarSample:
    timestamp: str
    full_name: str
    stars: int
    forks: int
    open_issues: int
    html_url: str

    @classmethod
    def from_repo(cls, repo: RepoSignal, timestamp: str | None = None) -> "StarSample":
        return cls(
            timestamp=timestamp or utc_now_iso(),
            full_name=repo.full_name,
            stars=repo.stars,
            forks=repo.forks,
            open_issues=repo.open_issues,
            html_url=repo.html_url,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "full_name": self.full_name,
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "html_url": self.html_url,
        }


def _repo_from_stored(payload: dict[str, Any]) -> RepoSignal:
    if "stargazers_count" in payload:
        return RepoSignal.from_github(payload)
    repo_payload = dict(payload)
    repo_payload["topics"] = tuple(repo_payload.get("topics") or ())
    return RepoSignal(**repo_payload)
