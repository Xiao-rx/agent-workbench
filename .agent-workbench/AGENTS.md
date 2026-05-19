# AGENTS.md for agent-workbench

## Mission

Help AI coding agents make small, verifiable changes in this repository without losing context or leaking secrets.

## Repository Map

- Files scanned: 56
- Lines scanned: 4955
- Main file kinds: python=31, other=9, config=9, docs=5, script=2
- Package managers: python/pyproject

## Safe Commands

- `python -m unittest discover -s tests`

## High-Signal Files

- `src/github_trend_lab/agents.py` (python, 471 lines)
- `data/snapshots/product-direction-live.json` (config, 470 lines)
- `reports/product-direction-decisions.json` (config, 308 lines)
- `reports/daily-decisions.json` (config, 300 lines)
- `data/snapshots/trend-product-live.json` (config, 238 lines)
- `src/github_trend_lab/reporting.py` (python, 199 lines)
- `reports/daily-brief.md` (docs, 188 lines)
- `src/github_trend_lab/cli.py` (python, 185 lines)
- `src/agent_workbench/scanner.py` (python, 184 lines)
- `src/github_trend_lab/verification.py` (python, 159 lines)
- `reports/product-direction-brief.md` (docs, 148 lines)
- `src/github_trend_lab/models.py` (python, 128 lines)

## Guardrails

- .env.local exists; keep it ignored and never paste secrets into issues.
- .env.bak exists; keep it ignored and never paste secrets into issues.
