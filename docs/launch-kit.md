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

## Demo command

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter all --check --print-kickoff
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
- `--print-kickoff` to copy the generated first prompt straight from the terminal
- the no-secret demo includes a safe `.github/copilot-instructions.md`, so the generated workbench visibly reports existing agent assets
- text output prints a copyable `Proof:` line with adapter and existing agent asset counts for screenshots, issues, and release notes
- scan JSON reports existing agent assets such as `AGENTS.md`, `CLAUDE.md`, Codex, Cursor, Copilot, Gemini, and OpenCode instruction files
- `demo --format json` and `init --format json` for machine-readable proofs with written files, artifact summary, existing agent assets, copyable proof summary, verification command, kickoff prompt, and readiness
- JSON artifacts with `--output-json` for CI and downstream agent harnesses

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
- Proof line: a copyable summary in normal terminal output with adapter and existing agent asset counts
- scan JSON: machine-readable repo map with file signals, package managers, safe commands, and existing agent assets
- output JSON files: reusable artifacts for CI and agent harnesses, including artifact summaries, existing agent assets, copyable proof summaries, and verification commands

It is provider-neutral and outputs plain Markdown, so it can be used with Codex, Claude Code, Cursor, OpenCode, or any coding agent workflow.

The repo includes generated examples for Python and TypeScript CLIs, so you can inspect the exact files before installing anything.

Install:
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git

Demo:
agent-workbench demo --adapter all --check --print-kickoff

JSON demo proof:
agent-workbench demo --adapter all --check --format json --output-json .agent-workbench/demo-proof.json

JSON init proof:
agent-workbench init . --output .agent-workbench --adapter all --check --format json --output-json .agent-workbench/init-proof.json

Check:
agent-workbench check . --format json

Artifacts:
agent-workbench scan . --format json --output-json .agent-workbench/repo-map.json
agent-workbench check . --format json --output-json .agent-workbench/readiness.json

I am using a daily GitHub trend/feedback loop to decide what to improve next.
The local `trend-lab insight --decisions reports/daily-decisions.json` command summarizes the latest decision JSON before each product change.
```

## Social preview

Use [`assets/social-preview.svg`](../assets/social-preview.svg) as the GitHub Social preview image if the repository settings UI allows upload.
