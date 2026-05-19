# Agent Workbench v0.3.0

Agent Workbench v0.3.0 makes the first-run path easier to inspect, share, and reuse from other tools.

## Install

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter claude --adapter cursor
```

## What ships

- `agent-workbench scan --format json`: print the repository map as machine-readable JSON.
- `agent-workbench demo --adapter claude --adapter cursor`: show the provider-neutral output and optional tool handoffs in the shortest demo path.
- A TypeScript CLI proof path under `examples/typescript-cli`.
- A Chinese README introduction for Chinese-speaking users landing on the repository.

## JSON scan example

```powershell
agent-workbench scan . --format json
```

The JSON payload includes the repository root, file and line totals, package managers, safe test commands, risk notes, and file-level signals.

## Why it matters

The Markdown files remain the main product surface for humans and coding agents. The JSON scan output gives downstream tooling a stable way to reuse the same repository map without parsing text.

## Verification

```powershell
python -m unittest discover -s tests
python -m github_trend_lab verify
```
