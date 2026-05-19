from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .storage import read_json


def build_insight(decisions_path: Path) -> dict[str, object]:
    payload = read_json(decisions_path)
    analysis = _dict(payload.get("analysis"))
    backlog = _list(payload.get("backlog"))
    findings = _list(payload.get("review_findings"))
    feedback = _dict(payload.get("git_observation"))

    next_item = _dict(backlog[0]) if backlog else {}
    return {
        "source": str(decisions_path),
        "headline": str(analysis.get("headline") or "No analysis headline."),
        "top_signal": _top_signal(analysis),
        "next_product_move": {
            "title": str(next_item.get("title") or "No backlog item."),
            "impact": str(next_item.get("impact") or "unknown"),
            "effort": str(next_item.get("effort") or "unknown"),
            "verification": str(next_item.get("verification") or "No verification gate."),
        },
        "target_feedback": {
            "repo": str(feedback.get("repo") or "unknown"),
            "current_stars": feedback.get("current_stars"),
            "star_delta": feedback.get("star_delta"),
            "samples_seen": feedback.get("samples_seen") or 0,
            "recent_change": feedback.get("recent_change") or "unknown",
            "next_sample_gate": feedback.get("next_sample_gate") or "Capture the next target repository star sample.",
        },
        "risk_summary": _risk_summary(findings),
    }


def render_insight_text(insight: dict[str, object]) -> str:
    move = _dict(insight.get("next_product_move"))
    feedback = _dict(insight.get("target_feedback"))
    risk = _dict(insight.get("risk_summary"))
    lines = [
        "Trend Insight",
        f"source={insight['source']}",
        f"headline={insight['headline']}",
        f"top_signal={insight['top_signal']}",
        "",
        f"next={move['title']}",
        f"impact={move['impact']}",
        f"effort={move['effort']}",
        f"verify={move['verification']}",
        "",
        f"repo={feedback['repo']}",
        f"stars={feedback['current_stars']}",
        f"star_delta={feedback['star_delta']}",
        f"samples_seen={feedback['samples_seen']}",
        f"recent_change={feedback['recent_change']}",
        f"next_sample_gate={feedback['next_sample_gate']}",
        "",
        f"risks={risk['count']}",
    ]
    if risk["highest_severity"] != "none":
        lines.append(f"highest_risk={risk['highest_severity']}: {risk['first_title']}")
    return "\n".join(lines) + "\n"


def render_insight_json(insight: dict[str, object]) -> str:
    return json.dumps(insight, ensure_ascii=False, indent=2) + "\n"


def _top_signal(analysis: dict[str, Any]) -> str:
    topics = _list(analysis.get("topics"))
    if topics:
        topic = _list(topics[0])
        if len(topic) >= 2:
            return f"topic:{topic[0]} ({topic[1]})"
    terms = _list(analysis.get("description_terms"))
    if terms:
        term = _list(terms[0])
        if len(term) >= 2:
            return f"term:{term[0]} ({term[1]})"
    languages = _list(analysis.get("languages"))
    if languages:
        language = _list(languages[0])
        if len(language) >= 2:
            return f"language:{language[0]} ({language[1]})"
    return "insufficient data"


def _risk_summary(findings: list[Any]) -> dict[str, object]:
    severities = {"high": 3, "medium": 2, "low": 1}
    highest = "none"
    first_title = ""
    for item in findings:
        finding = _dict(item)
        severity = str(finding.get("severity") or "low").lower()
        if severities.get(severity, 0) > severities.get(highest, 0):
            highest = severity
            first_title = str(finding.get("title") or "")
    return {
        "count": len(findings),
        "highest_severity": highest,
        "first_title": first_title,
    }


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
