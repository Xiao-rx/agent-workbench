# Agent Workbench v0.1.0

Agent Workbench turns a repository into an AI-agent-ready workspace with one command.

## Install

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo
```

## What ships

- `agent-workbench scan`: print a compact repository map.
- `agent-workbench init`: generate `AGENTS.md` and `agent-task-pack.md`.
- `agent-workbench demo`: create a no-secret demo workspace without touching the current repository.
- A committed example under `examples/python-cli` showing source input and generated output.

## Why it matters

The generated files are plain Markdown, provider-neutral, and designed to help Codex, Claude Code, Cursor, OpenCode, and other coding agents start with local context, safe commands, high-signal files, and guardrails.

## Verification

```powershell
python -m unittest discover -s tests
python -m github_trend_lab verify
```
