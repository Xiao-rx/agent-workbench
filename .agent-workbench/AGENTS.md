# AGENTS.md for agent-workbench

## Mission

Help AI coding agents make small, verifiable changes in this repository without losing context or leaking secrets.

## Repository Map

- Files scanned: 68
- Lines scanned: 5478
- Main file kinds: python=37, other=10, config=10, docs=9, script=2
- Package managers: python/pyproject

## Safe Commands

- `python -m unittest discover -s tests`

## High-Signal Files

- `src/github_trend_lab/agents.py` (python, 471 lines)
- `data/snapshots/product-direction-live.json` (config, 470 lines)
- `reports/product-direction-decisions.json` (config, 308 lines)
- `reports/daily-decisions.json` (config, 305 lines)
- `data/snapshots/trend-product-live.json` (config, 249 lines)
- `README.md` (docs, 210 lines)
- `src/github_trend_lab/reporting.py` (python, 199 lines)
- `reports/daily-brief.md` (docs, 193 lines)
- `src/github_trend_lab/cli.py` (python, 185 lines)
- `src/agent_workbench/scanner.py` (python, 184 lines)
- `src/github_trend_lab/verification.py` (python, 159 lines)
- `reports/product-direction-brief.md` (docs, 148 lines)

## Guardrails

- .env.local exists; keep it ignored and never paste secrets into issues.
- .env.bak exists; keep it ignored and never paste secrets into issues.
