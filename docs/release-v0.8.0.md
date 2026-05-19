# Agent Workbench v0.8.0

Agent Workbench v0.8.0 makes the complete first-run path shorter with an `--adapter all` shortcut.

## Demo

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter all --check --print-kickoff
```

## What Changed

- `--adapter all`: generate Claude Code, Codex, Cursor, and OpenCode handoff files in one option.
- `--print-kickoff`: print the generated kickoff prompt after writing files.
- Text output now prints a copyable `Proof:` line for screenshots and issue updates.
- `demo --format json` and `init --format json`: emit machine-readable proofs with written files, kickoff prompt, and optional readiness.
- `--output-json`: save demo and init proof payloads for CI and downstream agent harnesses.
- JSON proof payloads now include an artifact summary, a copyable proof summary, and a verification command for easier sharing and routing.
- `scan --format json` now reports existing agent instruction assets such as `AGENTS.md`, `CLAUDE.md`, `.codex/AGENTS.md`, `.cursor/rules/*.md`, `.github/copilot-instructions.md`, `GEMINI.md`, and `opencode.json`.
- Duplicate adapter requests are deduplicated, so `--adapter all --adapter codex` still writes each adapter once.
- `check --adapter all`: require Claude Code, Codex, Cursor, and OpenCode handoff files in the readiness gate.
- `check --strict`: treat warnings as `not_ready` for CI gates that should block on local risk notes.
- Readiness JSON now includes `next_action` so downstream agent harnesses can route ready, failed, and warning-only states.
- Generated `AGENTS.md` and `agent-task-pack.md` now list the adapter handoff files when adapters are requested.
- English and Chinese README paths now use the shorter all-adapter demo command.
- Launch assets now describe the v0.8.0 first-run path.

## Adapter Output

`--adapter all` writes:

- `.agent-workbench/CLAUDE.md`
- `.agent-workbench/.codex/AGENTS.md`
- `.agent-workbench/.cursor/rules/agent-workbench.md`
- `.agent-workbench/opencode.json`

The core output remains provider-neutral: `AGENTS.md` and `agent-task-pack.md` are still plain Markdown.
