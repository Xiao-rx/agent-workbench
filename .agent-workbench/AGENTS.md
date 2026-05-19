# AGENTS.md for agent-workbench

## Mission

Help AI coding agents make small, verifiable changes in this repository without losing context or leaking secrets.

## Repository Map

- Files scanned: 71
- Lines scanned: 5684
- Main file kinds: python=38, other=11, config=10, docs=10, script=2
- Package managers: python/pyproject

## Safe Commands

- `python -m unittest discover -s tests`

## High-Signal Files

- `src/github_trend_lab/agents.py` (python, 471 lines)
- `data/snapshots/product-direction-live.json` (config, 470 lines)
- `reports/product-direction-decisions.json` (config, 308 lines)
- `reports/daily-decisions.json` (config, 305 lines)
- `data/snapshots/trend-product-live.json` (config, 249 lines)
- `README.md` (docs, 217 lines)
- `src/github_trend_lab/reporting.py` (python, 199 lines)
- `reports/daily-brief.md` (docs, 193 lines)
- `src/github_trend_lab/cli.py` (python, 185 lines)
- `src/agent_workbench/scanner.py` (python, 184 lines)
- `src/agent_workbench/generator.py` (python, 178 lines)
- `tests/test_agent_workbench.py` (python, 175 lines)

## Guardrails

- .env.local exists; keep it ignored and never paste secrets into issues.
- .env.bak exists; keep it ignored and never paste secrets into issues.
