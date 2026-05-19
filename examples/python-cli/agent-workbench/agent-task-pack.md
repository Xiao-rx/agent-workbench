# Agent Task Pack: tiny-python-cli

## Kickoff Prompt

```text
You are working in tiny-python-cli. Read AGENTS.md first, inspect `README.md`, make one small improvement, and verify it before summarizing the change.
```

## Verification Commands

- `python -m unittest discover -s tests`

## High-Signal Files

- `README.md` (docs, 10 lines)
- `tiny_cli/cli.py` (python, 15 lines)
- `tests/test_cli.py` (python, 13 lines)
- `pyproject.toml` (config, 5 lines)
- `tiny_cli/__init__.py` (python, 2 lines)

## First Jobs

1. Run the verification commands and capture any existing failures.
2. Inspect `README.md` and one adjacent test or documentation file.
3. Make the smallest useful change that improves the first-run path or reduces agent confusion.
4. Re-run verification and summarize the changed files, result, and any follow-up risk.

## Acceptance Gate

- Every change explains the problem, the touched files, and the verification command.
- No secrets, generated caches, or local environment files are committed.
- Large rewrites must be split into reviewable commits.

## Guardrails

- No .gitignore found; create one before agent-driven edits.
