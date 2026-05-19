# Agent Workbench v0.5.0

Agent Workbench v0.5.0 makes the first-run path prove itself in one command.

## Install

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter claude --adapter cursor --check
```

## What ships

- `agent-workbench init --check`: generate `AGENTS.md` and `agent-task-pack.md`, then immediately run the readiness gate.
- `agent-workbench demo --check`: show the same generate-and-check loop in a no-secret demo repository.
- README and launch-kit updates that make the verified path the default public proof.
- Tests for both post-generation check paths.

## Verified first-run path

```powershell
agent-workbench init . --output .agent-workbench --project-name my-repo --check
```

The command exits with `0` only when the generated workbench passes the readiness checks.

## Why it matters

Trending developer tools tend to make the first useful result visible immediately. `--check` keeps Agent Workbench focused on that: one command writes the handoff and proves it is ready before a coding agent starts.

## Verification

```powershell
python -m unittest discover -s tests
python -m github_trend_lab verify
```
