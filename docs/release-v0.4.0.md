# Agent Workbench v0.4.0

Agent Workbench v0.4.0 adds a readiness gate for repositories that already generated a workbench.

## Install

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter claude --adapter cursor
```

## What ships

- `agent-workbench check`: verify that `.agent-workbench/AGENTS.md` and `agent-task-pack.md` exist and contain the required sections.
- `agent-workbench check --format json`: emit the same readiness result as machine-readable JSON for scripts and downstream agent harnesses.
- Warning-only reporting for local risk notes such as `.env.local` and `.env.bak`, so maintainers see the guardrails without blocking a ready workspace.
- English and Chinese README coverage for the new check command.

## Readiness check example

```powershell
agent-workbench check . --format json
```

The command exits with `0` when the workbench is ready and `1` when required files or sections are missing.

## Why it matters

The first-run path now has both creation and verification:

1. `agent-workbench init` generates the handoff.
2. `agent-workbench check` proves the handoff is present before a coding agent starts.

That keeps the product focused on one short maintainer workflow instead of only generating files once.

## Verification

```powershell
python -m unittest discover -s tests
python -m github_trend_lab verify
```
