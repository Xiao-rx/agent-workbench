# Agent Workbench v0.7.0

Agent Workbench v0.7.0 adds a Codex adapter while keeping the core output provider-neutral.

## Install

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter claude --adapter codex --adapter cursor --check
```

## What ships

- `--adapter codex`: generate `.codex/AGENTS.md` as a thin Codex handoff.
- The Codex adapter points back to `.agent-workbench/AGENTS.md` and `.agent-workbench/agent-task-pack.md` instead of duplicating instructions.
- README, Chinese README, and launch-kit examples now show Claude Code, Codex, and Cursor together.
- Tests cover Codex adapter generation from both `init` and `demo`.

## Codex adapter example

```powershell
agent-workbench init . --output .agent-workbench --adapter codex --check
```

This writes:

```text
.agent-workbench/.codex/AGENTS.md
```

## Why it matters

The product remains provider-neutral, but the first-run path now works cleanly for Codex users without requiring them to hand-wire a local instruction file.

## Verification

```powershell
python -m unittest discover -s tests
python -m github_trend_lab verify
```
