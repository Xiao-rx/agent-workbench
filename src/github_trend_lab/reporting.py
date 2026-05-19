from __future__ import annotations

import re
from urllib.parse import urlparse

from .agents import BacklogItem, GitObservation, HotnessAnalysis, ReviewFinding, target_feedback_backlog_item
from .models import StarSample, TrendSnapshot


def render_report(
    *,
    snapshot: TrendSnapshot,
    analysis: HotnessAnalysis,
    backlog: tuple[BacklogItem, ...],
    findings: tuple[ReviewFinding, ...],
    git_observation: GitObservation | None = None,
    star_sample: StarSample | None = None,
) -> str:
    lines: list[str] = [
        "# GitHub Trend Lab Daily Brief",
        "",
        f"Generated: {_escape_text(snapshot.generated_at)}",
        f"Search window: repositories created since {_escape_text(snapshot.since)}",
        f"Query: `{_escape_code(snapshot.query)}`",
        "",
        "## Hotness Analyst",
        "",
        _escape_text(analysis.headline),
        "",
        "Observed top repositories:",
    ]
    for repo in snapshot.repos[:10]:
        repo_name = _escape_text(repo.full_name)
        description = _escape_text(repo.description or "No description", max_length=320)
        repo_link = _safe_markdown_link(repo_name, repo.html_url)
        lines.append(f"- {repo_link} - {repo.stars} stars - {description}")

    lines.extend(["", "Learning candidate leaders:"])
    if analysis.leading_repositories:
        for full_name in analysis.leading_repositories:
            lines.append(f"- {_escape_text(full_name)}")
    else:
        lines.append("- No clean learning candidates in this snapshot.")

    lines.extend(["", "Pattern reasons:"])
    for reason in analysis.reasons:
        lines.append(f"- {_escape_text(reason)}")

    if analysis.excluded_repositories:
        lines.extend(["", "Risky repositories excluded from learning:"])
        for full_name, flags in analysis.excluded_repositories:
            lines.append(f"- {_escape_text(full_name)}: {_escape_text(', '.join(flags))}")

    if analysis.watched_repositories:
        lines.extend(["", "Weak risk signals kept under watch:"])
        for full_name, flags in analysis.watched_repositories:
            lines.append(f"- {_escape_text(full_name)}: {_escape_text(', '.join(flags))}")

    if analysis.repo_lessons:
        lines.extend(["", "Per-repository lessons:"])
        for lesson in analysis.repo_lessons:
            lines.extend(
                [
                    f"- {_escape_text(lesson.full_name)}",
                    f"  - Trust: {_escape_text(lesson.trust_level)} ({lesson.trust_score}/100)",
                    f"  - Why popular: {_escape_text(lesson.adoption_hypothesis)}",
                    f"  - Evidence: {_escape_text('; '.join(lesson.evidence))}",
                    f"  - Emulate: {_escape_text('; '.join(lesson.emulate))}",
                    f"  - Avoid: {_escape_text('; '.join(lesson.avoid))}",
                ]
            )

    lines.extend(["", "Top languages:"])
    lines.extend(_counter_lines(analysis.languages))
    lines.extend(["", "Top topics:"])
    lines.extend(_counter_lines(analysis.topics))
    lines.extend(["", "Description terms:"])
    lines.extend(_counter_lines(analysis.description_terms))

    lines.extend(["", "## Builder Strategist", ""])
    rendered_backlog = _backlog_with_target_feedback(backlog, git_observation)
    for item in rendered_backlog:
        lines.extend(
            [
                f"### {_escape_text(item.title)}",
                "",
                f"- Rationale: {_escape_text(item.rationale)}",
                f"- Impact: {_escape_text(item.impact)}",
                f"- Effort: {_escape_text(item.effort)}",
                f"- Signal: {_escape_text(item.signal)}",
                f"- Verification: {_escape_text(item.verification)}",
                "",
            ]
        )

    lines.extend(["## Review Guardian", ""])
    for finding in findings:
        lines.append(f"- {_escape_text(finding.severity.upper())}: {_escape_text(finding.title)} - {_escape_text(finding.detail)}")

    if star_sample:
        lines.extend(
            [
                "",
                "## Target Repository Signal",
                "",
                f"- Repository: {_safe_markdown_link(_escape_text(star_sample.full_name), star_sample.html_url)}",
                f"- Stars: {star_sample.stars}",
                f"- Forks: {star_sample.forks}",
                f"- Open issues: {star_sample.open_issues}",
                f"- Sampled at: {_escape_text(star_sample.timestamp)}",
            ]
        )

    if git_observation:
        lines.extend(
            [
                "",
                "## Feedback Loop Evidence",
                "",
                f"- Recent product change: {_escape_text(git_observation.recent_change or 'unknown')}",
                f"- Next sample gate: {_escape_text(git_observation.next_sample_gate or 'Capture the next target repository star sample.')}",
                "",
                "## Git Steward",
                "",
                f"- Repository: {_escape_text(git_observation.repo)}",
                f"- Current stars: {_optional_number(git_observation.current_stars)}",
                f"- Star delta in local history: {_optional_number(git_observation.star_delta)}",
                f"- Samples seen: {git_observation.samples_seen}",
                f"- Recommendation: {_escape_text(git_observation.recommendation)}",
                "",
                "Git status:",
                "",
                "```text",
                _escape_fenced_text(git_observation.git_status or "No git status available."),
                "```",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _counter_lines(values: tuple[tuple[str, int], ...]) -> list[str]:
    if not values:
        return ["- No data yet."]
    return [f"- {_escape_text(name)}: {count}" for name, count in values]


def _optional_number(value: int | None) -> str:
    return "unknown" if value is None else str(value)


def _escape_text(value: str, max_length: int | None = None) -> str:
    cleaned = " ".join(str(value).replace("\r", " ").replace("\n", " ").split())
    if max_length is not None and len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 1].rstrip() + "..."
    cleaned = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    escaped = cleaned.replace("\\", "\\\\")
    for char in ("`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "-", ".", "!", "|"):
        escaped = escaped.replace(char, f"\\{char}")
    return escaped


def _escape_code(value: str) -> str:
    return str(value).replace("`", "'").replace("\r", " ").replace("\n", " ")


def _escape_fenced_text(value: str) -> str:
    return str(value).replace("```", "'''")


def _safe_markdown_link(label: str, url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        return label
    if parsed.params or parsed.query or parsed.fragment:
        return label
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) != 2:
        return label
    owner, repo = path_parts
    if not _is_github_owner(owner) or not _is_github_repo(repo):
        return label
    safe_url = f"https://github.com/{owner}/{repo}"
    return f"[{label}]({safe_url})"


def _is_github_owner(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", value))


def _is_github_repo(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", value))


def _backlog_with_target_feedback(
    backlog: tuple[BacklogItem, ...],
    git_observation: GitObservation | None,
) -> tuple[BacklogItem, ...]:
    if not git_observation:
        return backlog
    if any(item.signal.startswith("target-feedback:") for item in backlog):
        return backlog
    return (*backlog, target_feedback_backlog_item(git_observation))
