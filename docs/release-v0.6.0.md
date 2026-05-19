# Agent Workbench v0.6.0

Agent Workbench v0.6.0 makes repository and readiness JSON reusable without shell redirection.

## Install

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter claude --adapter cursor --check
```

## What ships

- `agent-workbench scan --format json --output-json PATH`: write the repo map JSON to a file.
- `agent-workbench check --format json --output-json PATH`: write the readiness report JSON to a file.
- README and launch-kit examples for producing `.agent-workbench/repo-map.json` and `.agent-workbench/readiness.json`.
- Tests covering JSON artifact output and format validation.

## JSON artifacts

```powershell
agent-workbench scan . --format json --output-json .agent-workbench/repo-map.json
agent-workbench check . --format json --output-json .agent-workbench/readiness.json
```

Both commands create parent directories as needed and exit with the same status they would use when printing JSON to stdout.

## Why it matters

The Markdown files remain the human-facing handoff. JSON artifacts make the same workbench state easy for CI, scripts, and agent harnesses to consume without parsing console output.

## Verification

```powershell
python -m unittest discover -s tests
python -m github_trend_lab verify
```
