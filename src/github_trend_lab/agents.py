from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone

from .models import StarSample, TrendSnapshot
from .quality import blocking_risk_flags, is_learning_candidate, repo_risk_flags, risk_summary


SIGNAL_WORDS = {
    "ai",
    "agent",
    "llm",
    "dev",
    "cli",
    "tool",
    "open",
    "local",
    "fast",
    "simple",
    "data",
    "ui",
    "app",
    "workflow",
    "automation",
}


@dataclass(frozen=True)
class HotnessAnalysis:
    headline: str
    leading_repositories: tuple[str, ...]
    excluded_repositories: tuple[tuple[str, tuple[str, ...]], ...]
    watched_repositories: tuple[tuple[str, tuple[str, ...]], ...]
    repo_lessons: tuple["RepoLesson", ...]
    languages: tuple[tuple[str, int], ...]
    topics: tuple[tuple[str, int], ...]
    description_terms: tuple[tuple[str, int], ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class BacklogItem:
    title: str
    rationale: str
    impact: str
    effort: str
    verification: str
    signal: str = "baseline"


@dataclass(frozen=True)
class RepoLesson:
    full_name: str
    trust_score: int
    trust_level: str
    adoption_hypothesis: str
    evidence: tuple[str, ...]
    emulate: tuple[str, ...]
    avoid: tuple[str, ...]


@dataclass(frozen=True)
class ReviewFinding:
    severity: str
    title: str
    detail: str


@dataclass(frozen=True)
class GitObservation:
    repo: str
    current_stars: int | None
    star_delta: int | None
    samples_seen: int
    git_status: str
    recommendation: str
    recent_change: str | None = None
    next_sample_gate: str = ""


class HotnessAnalyst:
    name = "hotness-analyst"

    def analyze(self, snapshot: TrendSnapshot) -> HotnessAnalysis:
        learning_repos = tuple(repo for repo in snapshot.repos if is_learning_candidate(repo))
        excluded = tuple((repo.full_name, blocking_risk_flags(repo)) for repo in snapshot.repos if blocking_risk_flags(repo))
        watched = tuple(
            (repo.full_name, repo_risk_flags(repo))
            for repo in learning_repos
            if repo_risk_flags(repo)
        )

        languages = Counter(repo.language or "Unknown" for repo in learning_repos)
        topics = Counter(topic for repo in learning_repos for topic in repo.topics)
        terms = Counter()
        for repo in learning_repos:
            terms.update(_description_terms(repo.description))

        leading = tuple(repo.full_name for repo in sorted(learning_repos, key=lambda item: item.stars, reverse=True)[:5])
        lessons = tuple(_repo_lesson(repo) for repo in sorted(learning_repos, key=lambda item: item.stars, reverse=True)[:5])
        reasons = _infer_reasons(languages, topics, terms)
        headline = (
            f"{len(learning_repos)} learning candidates analyzed since {snapshot.since}; "
            f"{len(excluded)} risky repositories excluded; top signal is {_top_label(topics, terms, languages)}."
        )

        return HotnessAnalysis(
            headline=headline,
            leading_repositories=leading,
            excluded_repositories=excluded,
            watched_repositories=watched,
            repo_lessons=lessons,
            languages=tuple(languages.most_common(8)),
            topics=tuple(topics.most_common(12)),
            description_terms=tuple(terms.most_common(12)),
            reasons=reasons,
        )


class BuilderStrategist:
    name = "builder-strategist"

    def propose(
        self,
        analysis: HotnessAnalysis,
        target_repo: str | None = None,
        target_feedback: GitObservation | None = None,
    ) -> tuple[BacklogItem, ...]:
        topic_names = {topic for topic, _count in analysis.topics}
        term_names = {term for term, _count in analysis.description_terms}
        dominant_signal = _dominant_signal(analysis)
        backlog: list[BacklogItem] = [
            BacklogItem(
                title="Ship a one-command demo loop",
                rationale=f"{dominant_signal} is the strongest analysis signal, so the first success path should make that value obvious.",
                impact="high",
                effort="medium",
                verification="A fresh clone can run the demo command and produce a report without secrets.",
                signal=dominant_signal,
            ),
            BacklogItem(
                title="Publish daily trend evidence",
                rationale=f"The roadmap should show how current {dominant_signal} evidence changes recommendations over time.",
                impact="high",
                effort="low",
                verification="A scheduled run updates a snapshot, star history, and daily brief.",
                signal=dominant_signal,
            ),
            BacklogItem(
                title="Keep credentials optional and documented",
                rationale="Public GitHub data can be read unauthenticated, but tokens raise rate limits and enable repo automation.",
                impact="medium",
                effort="low",
                verification=".env.local is ignored, `.env.example` is safe, and CI uses scoped tokens.",
                signal="operational-safety",
            ),
        ]

        if {"ai", "llm", "agent"} & topic_names or {"ai", "llm", "agent"} & term_names:
            backlog.append(
                BacklogItem(
                    title="Expose the agent decisions as machine-readable JSON",
                    rationale="Agent-oriented projects spread faster when downstream tools can reuse their decisions.",
                    impact="medium",
                    effort="medium",
                    verification="The daily run writes both Markdown and JSON decision artifacts.",
                    signal="topic:agent",
                )
            )

        if {"cli", "tool", "automation", "workflow"} & topic_names or {"cli", "tool", "automation", "workflow"} & term_names:
            backlog.append(
                BacklogItem(
                    title="Tighten the CLI around repeatable maintainer workflows",
                    rationale="Developer-tool projects win when routine jobs become short, memorable commands.",
                    impact="medium",
                    effort="medium",
                    verification="Collect, monitor, analyze, and orchestrate commands have examples and tests.",
                    signal="topic:automation",
                )
            )

        if {"data", "ui", "local", "app"} & topic_names or {"data", "ui", "local", "app"} & term_names:
            backlog.append(
                BacklogItem(
                    title="Add a local insight view for trend comparisons",
                    rationale="Data and UI signals point to users wanting inspectable local output, not only a generated brief.",
                    impact="medium",
                    effort="medium",
                    verification="The report data can be opened locally and compared across at least two snapshots.",
                    signal="topic:data-ui",
                )
            )

        if target_feedback:
            backlog.append(target_feedback_backlog_item(target_feedback))
        elif target_repo:
            backlog.append(
                BacklogItem(
                    title=f"Create a public progress loop for {target_repo}",
                    rationale="The target repository should show how trend data directly affects roadmap choices.",
                    impact="medium",
                    effort="low",
                    verification="The daily brief includes a target repo star sample and next action.",
                    signal="target-repo",
                )
            )

        return tuple(backlog)


class ReviewGuardian:
    name = "review-guardian"

    def review(self, backlog: tuple[BacklogItem, ...], snapshot: TrendSnapshot) -> tuple[ReviewFinding, ...]:
        findings: list[ReviewFinding] = []
        risky_count = sum(1 for repo in snapshot.repos if blocking_risk_flags(repo))
        watched_count = sum(1 for repo in snapshot.repos if repo_risk_flags(repo) and not blocking_risk_flags(repo))
        if not snapshot.repos:
            findings.append(
                ReviewFinding(
                    severity="high",
                    title="No trend data available",
                    detail="Recommendations are weak without a live or sample snapshot. Run collect with network access or demo for a seeded sample.",
                )
            )
        if not any("credentials" in item.title.lower() for item in backlog):
            findings.append(
                ReviewFinding(
                    severity="medium",
                    title="Credential safety missing from backlog",
                    detail="The project handles GitHub tokens, so every iteration should preserve secret hygiene.",
                )
            )
        if not any("demo" in item.title.lower() for item in backlog):
            findings.append(
                ReviewFinding(
                    severity="medium",
                    title="No onboarding proof",
                    detail="A trend-driven project needs a quick reproducible proof path to earn trust.",
                )
            )
        if risky_count:
            findings.append(
                ReviewFinding(
                    severity="medium",
                    title="Trend data contains risky repositories",
                    detail=f"{risky_count} repository entries look like piracy, credential abuse, or spam magnets and should not be used as product inspiration.",
                )
            )
        if watched_count:
            findings.append(
                ReviewFinding(
                    severity="low",
                    title="Trend data contains weak risk signals",
                    detail=f"{watched_count} repository entries have weak risk terms and remain learning candidates only with caution.",
                )
            )
        missing_gates = [item.title for item in backlog if not item.verification.strip()]
        if missing_gates:
            findings.append(
                ReviewFinding(
                    severity="medium",
                    title="Backlog item missing verification gate",
                    detail=f"Every recommendation needs a testable gate. Missing: {', '.join(missing_gates)}",
                )
            )
        if not findings:
            findings.append(
                ReviewFinding(
                    severity="low",
                    title="Backlog has testable gates",
                    detail="Every proposed item includes a verification statement and can be reviewed before release.",
                )
            )
        return tuple(findings)


class GitSteward:
    name = "git-steward"

    def observe(
        self,
        target_repo: str,
        history: tuple[StarSample, ...],
        git_status: str,
        recent_change: str | None = None,
    ) -> GitObservation:
        current = history[-1].stars if history else None
        delta = None
        if len(history) >= 2:
            delta = history[-1].stars - history[0].stars

        if "nothing to commit" in git_status.lower() or not git_status.strip():
            recommendation = "Working tree is clean; prefer collecting another data point before changing code."
        elif not history:
            recommendation = "Target repository has no star history yet; publish the repo, then capture the first sample."
        elif delta is not None and delta <= 0:
            recommendation = "Commit small, explainable improvements and watch the next star sample for response."
        else:
            recommendation = "Review the current diff, keep changes focused, and commit once tests pass."

        return GitObservation(
            repo=target_repo,
            current_stars=current,
            star_delta=delta,
            samples_seen=len(history),
            git_status=git_status.strip(),
            recommendation=recommendation,
            recent_change=recent_change,
            next_sample_gate=_next_sample_gate(target_repo, current, delta, recent_change),
        )


def _description_terms(description: str) -> list[str]:
    words = []
    for raw in description.lower().replace("/", " ").replace("-", " ").split():
        word = "".join(ch for ch in raw if ch.isalnum())
        if len(word) >= 2 and word in SIGNAL_WORDS:
            words.append(word)
    return words


def _repo_lesson(repo) -> RepoLesson:
    score, evidence = _trust_score(repo)
    level = "high" if score >= 75 else "medium" if score >= 50 else "low"
    hypothesis_parts = []
    if {"ai", "llm", "agent"} & set(repo.topics) or {"ai", "llm", "agent"} & set(_description_terms(repo.description)):
        hypothesis_parts.append("AI/agent positioning")
    if "benchmark" in repo.description.lower() or "%" in repo.description:
        hypothesis_parts.append("a measurable benchmark claim")
    if repo.language:
        hypothesis_parts.append(f"{repo.language} ecosystem fit")
    if repo.topics:
        hypothesis_parts.append("clear topic packaging")
    if not hypothesis_parts:
        hypothesis_parts.append("a specific audience and visible social proof")

    emulate = []
    if repo.description:
        emulate.append("Use a concrete one-sentence value proposition.")
    if "benchmark" in repo.description.lower() or "%" in repo.description:
        emulate.append("Back claims with a measurable benchmark or proof point.")
    if repo.license_name and repo.license_name != "NOASSERTION":
        emulate.append("Keep license and reuse rights explicit.")
    if repo.pushed_at:
        emulate.append("Show active maintenance through recent commits.")

    avoid = []
    flags = repo_risk_flags(repo)
    if flags:
        avoid.append(f"Treat weak risk terms cautiously: {', '.join(flags)}.")
    if repo.stars > 100 and repo.forks == 0:
        avoid.append("Do not trust star spikes without fork or usage corroboration.")
    if not repo.description:
        avoid.append("Avoid vague positioning with no clear first-use story.")
    if not avoid:
        avoid.append("Avoid copying surface topics without reproducing the proof path.")

    return RepoLesson(
        full_name=repo.full_name,
        trust_score=score,
        trust_level=level,
        adoption_hypothesis=f"{repo.full_name} is likely gaining attention because it combines {', '.join(hypothesis_parts)}.",
        evidence=tuple(evidence),
        emulate=tuple(emulate),
        avoid=tuple(avoid),
    )


def _trust_score(repo) -> tuple[int, list[str]]:
    score = 45
    evidence: list[str] = []
    if repo.stars:
        score += min(20, repo.stars // 50)
        evidence.append(f"{repo.stars} stars")
    if repo.forks:
        score += min(15, max(1, int((repo.forks / max(repo.stars, 1)) * 100)))
        evidence.append(f"{repo.forks} forks corroborate reuse")
    else:
        score -= 10
        evidence.append("0 forks weakens social proof")
    if repo.license_name and repo.license_name != "NOASSERTION":
        score += 10
        evidence.append(f"{repo.license_name} license")
    else:
        score -= 5
        evidence.append("unclear license")
    if repo.open_issues <= 10:
        score += 5
        evidence.append(f"{repo.open_issues} open issues")
    if _hours_since(repo.pushed_at) is not None and _hours_since(repo.pushed_at) <= 72:
        score += 10
        evidence.append("recent push activity")
    if repo_risk_flags(repo):
        score -= 15
        evidence.append(f"risk watch: {risk_summary(repo)}")
    return max(0, min(100, score)), evidence


def _hours_since(value: str) -> float | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - parsed).total_seconds() / 3600


def _infer_reasons(languages: Counter[str], topics: Counter[str], terms: Counter[str]) -> tuple[str, ...]:
    reasons: list[str] = []
    if topics:
        top_topics = ", ".join(topic for topic, _count in topics.most_common(3))
        reasons.append(f"Topic clustering is strong around {top_topics}, which makes the value proposition easy to search and share.")
    if languages:
        top_language, _count = languages.most_common(1)[0]
        reasons.append(f"{top_language} leads the language mix, so examples and packaging should respect that ecosystem.")
    if {"ai", "llm", "agent"} & set(topics) or {"ai", "llm", "agent"} & set(terms):
        reasons.append("AI and agent language is still a strong discovery hook when paired with a concrete workflow.")
    if {"cli", "automation", "workflow", "tool"} & set(topics) or {"cli", "automation", "workflow", "tool"} & set(terms):
        reasons.append("Developer automation projects benefit from short setup, visible output, and repeatable commands.")
    if not reasons:
        reasons.append("The strongest projects combine a specific audience, obvious first run, and visible maintenance activity.")
    return tuple(reasons)


def _dominant_signal(analysis: HotnessAnalysis) -> str:
    if analysis.topics:
        topic, count = analysis.topics[0]
        return f"topic:{topic} ({count})"
    if analysis.description_terms:
        term, count = analysis.description_terms[0]
        return f"term:{term} ({count})"
    if analysis.languages:
        language, count = analysis.languages[0]
        return f"language:{language} ({count})"
    return "insufficient data"


def target_feedback_backlog_item(feedback: GitObservation) -> BacklogItem:
    repo = feedback.repo
    if feedback.star_delta is None:
        return BacklogItem(
            title=f"Start a measured feedback loop for {repo}",
            rationale="The target repository has no star delta yet, so recommendations need a baseline before claiming movement.",
            impact="medium",
            effort="low",
            verification="Capture at least two target repo star samples before changing the target-specific roadmap.",
            signal="target-feedback:baseline",
        )
    if feedback.star_delta <= 0:
        return BacklogItem(
            title=f"Tighten the next public proof for {repo}",
            rationale=f"Target repo feedback is flat or negative ({feedback.star_delta}), so the next change should be small and measurable.",
            impact="high",
            effort="low",
            verification="The next brief links one shipped improvement to the following target repo star sample.",
            signal="target-feedback:flat",
        )
    return BacklogItem(
        title=f"Amplify the trend-backed momentum for {repo}",
        rationale=f"Target repo feedback is positive (+{feedback.star_delta}), so the next recommendation should package what is already working.",
        impact="high",
        effort="medium",
        verification="Publish the winning workflow, before/after evidence, and the next star sample in the daily brief.",
        signal="target-feedback:growing",
    )


def _next_sample_gate(repo: str, current_stars: int | None, star_delta: int | None, recent_change: str | None) -> str:
    change = recent_change or "the next small product change"
    if current_stars is None:
        return f"After publishing {change}, capture the first star sample for {repo}."
    if star_delta is None:
        return f"After publishing {change}, compare the next star sample with the current {current_stars} stars."
    return f"After publishing {change}, compare the next star sample with {current_stars} stars and local delta {star_delta}."


def _top_label(topics: Counter[str], terms: Counter[str], languages: Counter[str]) -> str:
    if topics:
        return f"topic:{topics.most_common(1)[0][0]}"
    if terms:
        return f"term:{terms.most_common(1)[0][0]}"
    if languages:
        return f"language:{languages.most_common(1)[0][0]}"
    return "insufficient data"
