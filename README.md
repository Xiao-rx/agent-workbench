# Agent Workbench

Turn any repository into an AI-agent-ready workspace with one command.

Agent Workbench scans a codebase and writes the two files a coding agent needs before it can work safely:

- `AGENTS.md`: repository map, safe commands, high-signal files, and guardrails.
- `agent-task-pack.md`: first jobs and acceptance gates for agent-driven edits.

The product direction is chosen by a local trend engine that studies current GitHub daily winners. The latest clean signal points toward provider-neutral agent tooling: projects that are specific, measurable, easy to run, and useful across Codex, Claude Code, and other agent harnesses.

## Quick Start

```powershell
$env:UV_CACHE_DIR='.uv-cache'
$env:UV_PYTHON_INSTALL_DIR='.uv-python'
$env:PYTHONPATH='src'
uv run --python 3.12 python -m agent_workbench init . --output .agent-workbench --project-name agent-workbench
```

See the value without touching your current repository:

```powershell
uv run --python 3.12 python -m agent_workbench demo
```

Inspect a repository before generating files:

```powershell
uv run --python 3.12 python -m agent_workbench scan .
```

Run tests:

```powershell
$env:UV_CACHE_DIR='.uv-cache'; $env:UV_PYTHON_INSTALL_DIR='.uv-python'; $env:PYTHONPATH='src'; uv run --python 3.12 python -m unittest discover -s tests
```

## Why This Exists

AI coding agents fail less when the repository gives them a short, accurate operating manual. Most projects do not have one. Agent Workbench builds that first manual automatically from repository structure, package markers, test commands, and local risk signals.

The goal is not to be another agent. The goal is to make every repository easier for agents to enter, change, verify, and leave clean.

## Commands

```text
python -m agent_workbench scan [ROOT]
python -m agent_workbench init [ROOT] --output .agent-workbench --project-name NAME
python -m agent_workbench demo [--output PATH]
```

The internal trend engine remains available for growth experiments:

```text
python -m github_trend_lab collect
python -m github_trend_lab history --start 2026-01-01 --end 2026-05-19 --top 5
python -m github_trend_lab monitor --repo OWNER/REPO
python -m github_trend_lab orchestrate --repo OWNER/REPO
python -m github_trend_lab verify
```

## Feedback Loop

```mermaid
flowchart LR
    A["Daily GitHub winners"] --> B["Trend engine"]
    B --> C["Product direction"]
    C --> D["Agent Workbench changes"]
    D --> E["Git steward and tests"]
    E --> F["Star and feedback monitor"]
    F --> B
```

## Current Trend Bet

The current bet is provider-neutral agent enablement:

- Specific audience: developers using coding agents on real repositories.
- One-command value: generate agent handoff docs immediately.
- Measurable proof: files scanned, safe commands found, guardrails written.
- Portable surface: works before choosing Codex, Claude Code, Cursor, or another tool.

The trend engine is deliberately kept in this repository so the product can keep changing as GitHub daily winners shift.

## Credentials

Do not paste tokens into chat or commit them to git.

For local trend runs, put a fine-grained token in `.env.local`:

```env
GITHUB_TOKEN=<your-token>
GITHUB_OWNER=your-user
GITHUB_REPO=agent-workbench
TARGET_REPO=your-user/agent-workbench
```

`.env.local` is ignored by git.

## Publishing

After `.env.local` contains a scoped token, publish with the normal git path:

```powershell
.\scripts\publish.ps1 -Visibility public
```

Verify the remote after publishing:

```powershell
.\scripts\verify_remote.ps1
```
