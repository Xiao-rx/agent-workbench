# AGENTS.md for tiny-python-cli

## Mission

Help AI coding agents make small, verifiable changes in this repository without losing context or leaking secrets.

## Repository Map

- Files scanned: 5
- Lines scanned: 45
- Main file kinds: python=3, config=1, docs=1
- Package managers: python/pyproject

## Safe Commands

- `python -m unittest discover -s tests`

## High-Signal Files

- `tiny_cli/cli.py` (python, 15 lines)
- `tests/test_cli.py` (python, 13 lines)
- `README.md` (docs, 10 lines)
- `pyproject.toml` (config, 5 lines)
- `tiny_cli/__init__.py` (python, 2 lines)

## Guardrails

- No .gitignore found; create one before agent-driven edits.
