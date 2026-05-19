# AGENTS.md for tiny-typescript-cli

## Mission

Help AI coding agents make small, verifiable changes in this repository without losing context or leaking secrets.

## Repository Map

- Files scanned: 5
- Lines scanned: 73
- Main file kinds: config=2, docs=1, typescript=1, javascript=1
- Package managers: node/npm

## Safe Commands

- `npm test`

## High-Signal Files

- `src/index.ts` (typescript, 25 lines)
- `package.json` (config, 14 lines)
- `tests/smoke.test.js` (javascript, 12 lines)
- `README.md` (docs, 11 lines)
- `tsconfig.json` (config, 11 lines)

## Guardrails

- No .gitignore found; create one before agent-driven edits.
