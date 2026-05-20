# Agent Workbench Launch Kit

## One-line pitch

Turn any repository into an AI-agent-ready workspace with one command.

## Short pitch

Agent Workbench is a provider-neutral Python CLI that scans a repository and generates the two Markdown files a coding agent needs before it starts work: `AGENTS.md` and `agent-task-pack.md`.

It works with Codex, Claude Code, Cursor, OpenCode, and other agent harnesses because the output is plain Markdown: repository map, safe commands, high-signal files, kickoff prompt, acceptance gates, and guardrails.

## GitHub metadata

Description:

```text
Turn any repository into an AI-agent-ready workspace with AGENTS.md, task packs, adapters, and scan JSON.
```

Topics:

```text
agent-workbench, ai-agents, claude-code, cli, codex, cursor, devtools, developer-tools, llm, productivity
```

License:

```text
MIT
```

## Demo command

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter all --strict --print-kickoff
```

## Share Post Draft

After publishing v0.8.0:

```text
I shipped Agent Workbench v0.8.0: a tiny provider-neutral CLI that turns any repo into an AI-agent-ready workspace.

One command generates:

- `AGENTS.md`
- `agent-task-pack.md`
- optional Claude Code, Codex, Cursor, and OpenCode adapters with `--adapter all`
- `agent-workbench check` for a quick readiness gate before handing the repo to an agent
- `--strict` on `demo` and `init` when warnings should fail the proof; it automatically runs the readiness check
- `demo --proof [PATH]` for a one-option strict all-adapter JSON proof command that also prints copyable `Proof:` and `Proof command:` lines and defaults the proof path inside the generated workbench
- `demo --report [PATH]` for a shareable no-secret Markdown report with generated files, readiness status, existing agent assets, the kickoff prompt, and a sanitized feedback link
- `init --proof [PATH]` for the same proof shape on the real repository bootstrap path
- `init --report [PATH]` for the same shareable Markdown report shape on a real repository, including the same feedback link
- `--print-kickoff` to copy the generated first prompt straight from the terminal
- the no-secret demo includes a safe `.github/copilot-instructions.md`, so the generated workbench visibly reports existing agent assets
- Agent Workbench does not need credentials; `.env.example` is a placeholder-only template for optional trend/monitor runs, while `.env.local` stays ignored
- GitHub issue form and embedded report feedback link for sanitized `demo --report` and `init --report` feedback, so report samples can feed the growth loop without exposing secrets
- text output prints a copyable `Proof:` line with adapter and existing agent asset counts, readiness counts when checks run, plus the exact readiness gate command for screenshots, issues, and release notes
- scan JSON reports `kind`, `schema_version`, and existing agent assets such as `AGENTS.md`, `CLAUDE.md`, Codex, Cursor, Copilot, Gemini, and OpenCode instruction files
- `demo --format json` and `init --format json` for machine-readable proofs with `kind`, `schema_version`, written files, artifact summary, a handoff object with `AGENTS.md`, `agent-task-pack.md`, and `next_action`, pre-write existing agent assets, copyable proof summary, proof command for the shortcut path, verification command, readiness summary, readiness counts, readiness command, structured readiness args, feedback URL and safety note, kickoff prompt, and readiness
- JSON artifacts with `--output-json` for CI and downstream agent harnesses; the option implies JSON output, so the proof command stays shorter
- CI validates the installed CLI with the strict all-adapter JSON demo proof and Markdown demo report, so the launch command is continuously exercised from a fresh checkout
- MIT license, so reuse rights are explicit before adoption

The output gives Codex, Claude Code, Cursor, OpenCode, and other coding agents a repo map, safe commands, high-signal files, a kickoff prompt, and guardrails before they touch code.

Examples include generated workbench output for both Python and TypeScript CLI repositories.

Repo: https://github.com/Xiao-rx/agent-workbench
Release: https://github.com/Xiao-rx/agent-workbench/releases/tag/v0.8.0
```

## Show HN draft

Title:

```text
Show HN: Agent Workbench - Generate AGENTS.md and task packs for coding agents
```

Body:

```text
I built Agent Workbench, a small Python CLI that turns a repository into an AI-agent-ready workspace.

It scans the repo and writes:

- AGENTS.md: repo map, safe commands, high-signal files, guardrails
- agent-task-pack.md: kickoff prompt, first jobs, acceptance gates
- Codex adapter: .codex/AGENTS.md handoff that points to the generated workbench
- OpenCode adapter: opencode.json instructions that point to the generated workbench
- readiness check: a pass/fail command for existing workbench files
- Proof line: a copyable summary in normal terminal output with adapter counts, existing agent asset counts, and readiness status when checks run
- Demo report: a shareable Markdown artifact with generated files, readiness status, existing agent assets, the kickoff prompt, and a Share Feedback link
- scan JSON: machine-readable repo map with schema metadata, file signals, package managers, safe commands, and existing agent assets
- output JSON files: reusable artifacts for CI and agent harnesses, including schema metadata, artifact summaries, structured handoff paths, pre-write existing agent assets, copyable proof summaries, verification commands, readiness summaries, readiness counts, structured readiness args, and report feedback metadata

It is provider-neutral and outputs plain Markdown, so it can be used with Codex, Claude Code, Cursor, OpenCode, or any coding agent workflow.
It is MIT licensed.

The repo includes generated examples for Python and TypeScript CLIs, so you can inspect the exact files before installing anything.

Install:
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git

Demo:
agent-workbench demo --adapter all --strict --print-kickoff

JSON demo proof:
agent-workbench demo --proof

Markdown demo report:
agent-workbench demo --report

JSON init proof:
agent-workbench init . --output .agent-workbench --proof

Markdown init report:
agent-workbench init . --output .agent-workbench --report

Check:
agent-workbench check . --format json
agent-workbench demo --adapter all --strict

Artifacts:
agent-workbench scan . --output-json .agent-workbench/repo-map.json
agent-workbench check . --output-json .agent-workbench/readiness.json

I am using a daily GitHub trend/feedback loop to decide what to improve next.
The local `trend-lab insight --decisions reports/daily-decisions.json` command summarizes the latest decision JSON before each product change.
```

## Social preview

Use [`assets/social-preview.svg`](../assets/social-preview.svg) as the GitHub Social preview image if the repository settings UI allows upload.
