# AGENTS.md for agent-workbench

## Mission

Help AI coding agents make small, verifiable changes in this repository without losing context or leaking secrets.

## Repository Map

- Files scanned: 87
- Lines scanned: 7622
- Main file kinds: python=39, docs=21, config=12, other=11, script=2, typescript=1
- Package managers: python/pyproject

## Agent Tool Handoffs

- Claude Code: `CLAUDE.md`
- Codex: `.codex/AGENTS.md`
- Cursor: `.cursor/rules/agent-workbench.md`
- OpenCode: `opencode.json`

## Existing Agent Assets

- Claude Code instructions: `CLAUDE.md`

## Safe Commands

- `python -m unittest discover -s tests`

## High-Signal Files

- `tests/test_agent_workbench.py` (python, 726 lines)
- `src/github_trend_lab/agents.py` (python, 490 lines)
- `data/snapshots/product-direction-live.json` (config, 470 lines)
- `src/agent_workbench/cli.py` (python, 344 lines)
- `reports/product-direction-decisions.json` (config, 308 lines)
- `reports/daily-decisions.json` (config, 302 lines)
- `README.md` (docs, 278 lines)
- `src/agent_workbench/generator.py` (python, 254 lines)
- `data/snapshots/trend-product-live.json` (config, 238 lines)
- `src/agent_workbench/scanner.py` (python, 206 lines)
- `src/github_trend_lab/reporting.py` (python, 204 lines)
- `src/agent_workbench/checks.py` (python, 201 lines)

## Guardrails

- .env.local exists; keep it ignored and never paste secrets into issues.
- .env.bak exists; keep it ignored and never paste secrets into issues.
