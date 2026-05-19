# Agent Workbench v0.2.0

Agent Workbench v0.2.0 keeps the core output provider-neutral while adding optional handoff adapters for Claude Code and Cursor.

## Install

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter claude --adapter cursor
```

## What ships

- `agent-workbench scan`: print a compact repository map.
- `agent-workbench init`: generate `AGENTS.md` and `agent-task-pack.md`.
- `agent-workbench demo`: create a no-secret demo workspace without touching the current repository.
- `agent-workbench --version`: print the installed CLI version.
- `--adapter claude`: also write `CLAUDE.md` as a thin Claude Code handoff.
- `--adapter cursor`: also write `.cursor/rules/agent-workbench.md` as a thin Cursor rule.

## Adapter example

```powershell
agent-workbench init . --output .agent-workbench --adapter claude --adapter cursor
agent-workbench demo --adapter claude --adapter cursor
```

Without adapters, Agent Workbench still writes only the two plain Markdown files: `AGENTS.md` and `agent-task-pack.md`.

## Why it matters

The default path remains portable across Codex, Claude Code, Cursor, OpenCode, and other coding agents. Teams can stay provider-neutral, then opt into small tool-specific files only when those files help an existing workflow.

## Verification

```powershell
python -m unittest discover -s tests
python -m github_trend_lab verify
```
