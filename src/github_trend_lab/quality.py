from __future__ import annotations

import re

from .models import RepoSignal


STRONG_RISK_TERMS = (
    "keygen",
    "crack",
    "cracked",
    "activator",
    "activation",
    "unlocker",
    "serial",
    "torrent",
    "license key",
    "pre-activated",
    "preactivated",
    "bypass",
    "free download",
)

WEAK_RISK_TERMS = (
    "full version",
    "loader",
    "mod",
    "steam workshop downloader",
    "download install",
)


def repo_risk_flags(repo: RepoSignal) -> tuple[str, ...]:
    text = normalize_risk_text(
        " ".join(
            [
                repo.full_name,
                repo.description,
                " ".join(repo.topics),
            ]
        )
    )
    flags = [term for term in STRONG_RISK_TERMS if _matches_risk_term(text, term)]
    flags.extend(term for term in WEAK_RISK_TERMS if _matches_risk_term(text, term))
    return tuple(dict.fromkeys(flags))


def repo_risk_score(repo: RepoSignal) -> int:
    flags = repo_risk_flags(repo)
    strong = sum(1 for flag in flags if flag in STRONG_RISK_TERMS)
    weak = sum(1 for flag in flags if flag in WEAK_RISK_TERMS)
    return strong * 3 + weak


def normalize_risk_text(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def blocking_risk_flags(repo: RepoSignal) -> tuple[str, ...]:
    flags = repo_risk_flags(repo)
    strong_flags = tuple(flag for flag in flags if flag in STRONG_RISK_TERMS)
    weak_flags = tuple(flag for flag in flags if flag in WEAK_RISK_TERMS)
    if strong_flags:
        return strong_flags
    if len(weak_flags) >= 2:
        return weak_flags
    return ()


def risk_summary(repo: RepoSignal) -> str:
    flags = repo_risk_flags(repo)
    if not flags:
        return "trusted"
    blocking = blocking_risk_flags(repo)
    if blocking:
        return f"blocked: {', '.join(blocking)}"
    return f"watch: {', '.join(flags)}"


def is_learning_candidate(repo: RepoSignal) -> bool:
    return not blocking_risk_flags(repo)


def _matches_risk_term(text: str, term: str) -> bool:
    normalized_term = normalize_risk_text(term)
    if " " in normalized_term:
        return f" {normalized_term} " in f" {text} "
    pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
    return re.search(pattern, text) is not None
