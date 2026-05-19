# Agent Task Pack: agent-workbench

## Kickoff Prompt

```text
You are working in agent-workbench. Read AGENTS.md first, inspect `README.md`, make one small improvement, and verify it before summarizing the change.
```

## Verification Commands

- `python -m unittest discover -s tests`

## High-Signal Files

- `README.md` (docs, 174 lines)
- `src/agent_workbench/scanner.py` (python, 184 lines)
- `tests/test_agent_workbench.py` (python, 145 lines)
- `src/agent_workbench/generator.py` (python, 122 lines)
- `src/agent_workbench/cli.py` (python, 104 lines)
- `src/agent_workbench/models.py` (python, 30 lines)

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

- .env.local exists; keep it ignored and never paste secrets into issues.
- .env.bak exists; keep it ignored and never paste secrets into issues.
