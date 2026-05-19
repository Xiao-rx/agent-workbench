from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .config import default_since, read_config
from .github_api import GitHubApiError, GitHubClient
from .growth_loop import run_growth_loop
from .history import collect_daily_rankings, load_many_snapshots
from .insight import build_insight, render_insight_json, render_insight_text
from .models import StarSample
from .pipeline import run_analysis, run_demo_cycle, run_live_cycle
from .storage import append_jsonl, read_snapshot, read_star_history, star_history_path, write_json, write_snapshot
from .verification import has_failures, render_check_report, run_local_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="github-trend-lab", description="Analyze GitHub trend signals and maintain a project feedback loop.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Collect popular repositories from the GitHub Search API.")
    collect.add_argument("--since", default=default_since())
    collect.add_argument("--top", type=int, default=12)
    collect.add_argument("--min-stars", type=int, default=10)
    collect.add_argument("--language")
    collect.add_argument("--topic")
    collect.add_argument("--query-extra")
    collect.add_argument("--output", type=Path)

    history = subparsers.add_parser("history", help="Collect day-by-day top repositories for a date range.")
    history.add_argument("--start", default=default_since())
    history.add_argument("--end", default=date.today().isoformat())
    history.add_argument("--top", type=int, default=5)
    history.add_argument("--min-stars", type=int, default=0)
    history.add_argument("--output-dir", type=Path, default=Path("data/snapshots"))
    history.add_argument("--no-resume", action="store_true")
    history.add_argument("--analyze-output", type=Path, help="Optionally write one aggregate analysis report.")

    monitor = subparsers.add_parser("monitor", help="Record a live star sample for a target repository.")
    monitor.add_argument("--repo", help="Repository in OWNER/REPO form. Defaults to TARGET_REPO.")
    monitor.add_argument("--output", type=Path)

    analyze = subparsers.add_parser("analyze", help="Analyze a saved trend snapshot.")
    analyze.add_argument("--snapshot", type=Path, required=True)
    analyze.add_argument("--repo", help="Optional target repository in OWNER/REPO form.")
    analyze.add_argument("--history", type=Path, help="Optional star history JSONL path.")
    analyze.add_argument("--output", type=Path, default=Path("reports/daily-brief.md"))
    analyze.add_argument("--decisions-output", type=Path)

    insight = subparsers.add_parser("insight", help="Summarize the latest decision JSON for local product iteration.")
    insight.add_argument("--decisions", type=Path, default=Path("reports/daily-decisions.json"))
    insight.add_argument("--format", choices=("text", "json"), default="text")
    insight.add_argument("--output-json", type=Path, help="Write the JSON insight payload to a file. Implies --format json.")

    orchestrate = subparsers.add_parser("orchestrate", help="Run collect, monitor, analyze, review, and git stewardship.")
    orchestrate.add_argument("--repo", help="Repository in OWNER/REPO form. Defaults to TARGET_REPO.")
    orchestrate.add_argument("--since", default=default_since())
    orchestrate.add_argument("--top", type=int, default=12)
    orchestrate.add_argument("--min-stars", type=int, default=10)
    orchestrate.add_argument("--output", type=Path, default=Path("reports/daily-brief.md"))
    orchestrate.add_argument("--snapshot-output", type=Path)
    orchestrate.add_argument("--decisions-output", type=Path, default=Path("reports/daily-decisions.json"))

    demo = subparsers.add_parser("demo", help="Run a no-network seeded demo cycle.")
    demo.add_argument("--since", default="2026-01-01")
    demo.add_argument("--output", type=Path, default=Path("reports/demo-brief.md"))

    verify = subparsers.add_parser("verify", help="Run local readiness checks that do not require publishing.")
    verify.add_argument("--output", type=Path, help="Optional Markdown report path.")

    growth = subparsers.add_parser("growth-loop", help="Run the background agent growth loop for the actual product.")
    growth.add_argument("--repo", default="Xiao-rx/agent-workbench", help="Product repository to monitor.")
    growth.add_argument("--since", default=default_since())
    growth.add_argument("--top", type=int, default=12)
    growth.add_argument("--min-stars", type=int, default=50)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = read_config()
    client = GitHubClient(token=config.github_token, api_version=config.api_version)

    try:
        if args.command == "collect":
            snapshot = client.search_repositories(
                since=args.since,
                top=args.top,
                min_stars=args.min_stars,
                language=args.language,
                topic=args.topic,
                query_extra=args.query_extra,
            )
            path = write_snapshot(snapshot, args.output)
            print(f"Wrote snapshot: {path}")
            return 0

        if args.command == "monitor":
            repo_name = args.repo or config.target_repo
            if not repo_name:
                parser.error("monitor requires --repo or TARGET_REPO")
            repo = client.get_repository(repo_name)
            sample = StarSample.from_repo(repo)
            path = args.output or star_history_path(repo_name)
            append_jsonl(path, sample.to_dict())
            print(f"Wrote star sample: {path}")
            print(f"{sample.full_name}: {sample.stars} stars")
            return 0

        if args.command == "history":
            paths = collect_daily_rankings(
                client=client,
                start=date.fromisoformat(args.start),
                end=date.fromisoformat(args.end),
                top=args.top,
                min_stars=args.min_stars,
                output_dir=args.output_dir,
                resume=not args.no_resume,
            )
            print(f"Wrote or reused {len(paths)} daily snapshots in {args.output_dir}")
            if args.analyze_output:
                snapshot = load_many_snapshots(paths)
                report, _decisions = run_analysis(snapshot)
                args.analyze_output.parent.mkdir(parents=True, exist_ok=True)
                args.analyze_output.write_text(report, encoding="utf-8")
                print(f"Wrote aggregate report: {args.analyze_output}")
            return 0

        if args.command == "analyze":
            snapshot = read_snapshot(args.snapshot)
            history = tuple(read_star_history(args.history)) if args.history else ()
            report, decisions = run_analysis(snapshot, args.repo, history)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
            if args.decisions_output:
                write_json(args.decisions_output, decisions)
            print(f"Wrote report: {args.output}")
            return 0

        if args.command == "insight":
            output_format = "json" if args.output_json else args.format
            insight_payload = build_insight(args.decisions)
            if output_format == "json":
                if args.output_json:
                    write_json(args.output_json, insight_payload)
                    print(f"Wrote insight: {args.output_json}")
                else:
                    print(render_insight_json(insight_payload), end="")
                return 0
            print(render_insight_text(insight_payload), end="")
            return 0

        if args.command == "orchestrate":
            repo_name = args.repo or config.target_repo
            result = run_live_cycle(
                client=client,
                target_repo=repo_name,
                since=args.since,
                top=args.top,
                min_stars=args.min_stars,
                output=args.output,
                snapshot_output=args.snapshot_output,
                decisions_output=args.decisions_output,
            )
            print(f"Wrote snapshot: {result.snapshot_path}")
            print(f"Wrote report: {result.report_path}")
            if result.star_history_path:
                print(f"Star history: {result.star_history_path}")
            return 0

        if args.command == "demo":
            result = run_demo_cycle(args.output, since=args.since)
            print(f"Wrote demo snapshot: {result.snapshot_path}")
            print(f"Wrote demo report: {result.report_path}")
            return 0

        if args.command == "verify":
            checks = run_local_checks()
            report = render_check_report(checks)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(report, encoding="utf-8")
                print(f"Wrote verification report: {args.output}")
            else:
                print(report, end="")
            return 1 if has_failures(checks) else 0

        if args.command == "growth-loop":
            result = run_growth_loop(product_repo=args.repo, since=args.since, top=args.top, min_stars=args.min_stars)
            print(f"Wrote growth report: {result.report_path}")
            print(f"Wrote verification report: {result.verification_path}")
            print(f"Wrote trend snapshot: {result.snapshot_path}")
            return 0 if result.ok else 1
    except GitHubApiError as exc:
        print(f"GitHub API error: {exc}")
        print("Tip: refresh gh auth or set GITHUB_TOKEN in .env.local for higher rate limits.")
        return 2

    parser.error(f"Unknown command: {args.command}")
    return 2
