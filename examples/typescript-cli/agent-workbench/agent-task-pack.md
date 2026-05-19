# Agent Task Pack: tiny-typescript-cli

## Kickoff Prompt

```text
You are working in tiny-typescript-cli. Read AGENTS.md first, inspect `README.md`, make one small improvement, and verify it before summarizing the change.
```

## Verification Commands

- `npm test`

## High-Signal Files

- `README.md` (docs, 11 lines)
- `src/index.ts` (typescript, 25 lines)
- `package.json` (config, 14 lines)
- `tests/smoke.test.js` (javascript, 12 lines)
- `tsconfig.json` (config, 11 lines)

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
