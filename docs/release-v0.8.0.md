# Agent Workbench v0.8.0

Agent Workbench v0.8.0 makes the complete first-run path shorter with an `--adapter all` shortcut.

## Demo

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter all --strict --print-kickoff
```

## What Changed

- `--adapter all`: generate Claude Code, Codex, Cursor, and OpenCode handoff files in one option.
- `--print-kickoff`: print the generated kickoff prompt after writing files.
- Text output now prints a copyable `Proof:` line for screenshots and issue updates.
- `demo --format json` and `init --format json`: emit machine-readable proofs with written files, kickoff prompt, and optional readiness.
- `--output-json`: save demo and init proof payloads for CI and downstream agent harnesses, and imply JSON output so the proof command stays shorter.
- `demo --proof [PATH]`: write a strict all-adapter JSON proof with one option for fresh-clone demos, screenshots, and CI artifacts; the shortcut also prints copyable `Proof:` and `Proof command:` lines, records the reproducible `proof_command`, and defaults the path inside the generated workbench when omitted.
- `demo --report [PATH]`: write a shareable no-secret Markdown demo report with generated files, readiness status/counts, the readiness gate, existing agent assets, the kickoff prompt, a copy/paste share summary, and a Share Feedback link; the shortcut uses the same strict all-adapter demo path and defaults the path inside the generated workbench when omitted.
- `init --proof [PATH]`: write the same proof shape for a real repository bootstrap path, with the proof file defaulting inside the generated workbench when omitted.
- `init --report [PATH]`: write the same shareable Markdown report shape for a real repository bootstrap path, with the report defaulting inside the generated workbench when omitted and carrying the same share summary and feedback link.
- GitHub issue form plus embedded report feedback metadata for sanitized `demo --report` and `init --report` feedback, so real first-run reports can feed the growth loop without exposing secrets.
- JSON outputs include `kind` and `schema_version` so downstream tools can route scan, readiness, and proof payloads without guessing.
- JSON proof payloads include a structured `handoff` object with the generated `AGENTS.md`, `agent-task-pack.md`, and the recommended `next_action`.
- JSON proof payloads now include an artifact summary, a copyable proof summary with adapter and existing agent asset counts, a `share_snippet` for issues/social posts, readiness status/counts when checks run, a verification command, both string and structured readiness commands that preserve adapter and strict gates, and feedback metadata for easier sharing and routing.
- JSON proof payloads now include pre-write existing `agent_assets`, and the no-secret demo includes a safe Copilot instructions file so the first run visibly exercises asset detection without counting newly generated handoffs as prior project context.
- `.env.example` now documents placeholder-only optional trend/monitor credentials, while README and Chinese README make clear that Agent Workbench itself does not need a token and `.env.local` stays ignored.
- `scan --format json` now reports existing agent instruction assets such as `AGENTS.md`, `CLAUDE.md`, `.codex/AGENTS.md`, `.cursor/rules/*.md`, `.github/copilot-instructions.md`, `GEMINI.md`, and `opencode.json`.
- Duplicate adapter requests are deduplicated, so `--adapter all --adapter codex` still writes each adapter once.
- `check --adapter all`: require Claude Code, Codex, Cursor, and OpenCode handoff files in the readiness gate.
- `check --strict`: treat warnings as `not_ready` for CI gates that should block on local risk notes.
- `demo --strict` and `init --strict`: run the readiness check and fail the first-run proof when readiness warnings are present.
- CI now validates the installed CLI with `demo --proof` and `demo --report`, so the public proof path stays reproducible from a fresh checkout.
- `init ROOT --output RELATIVE_PATH` now resolves the output directory inside `ROOT`, matching `check --workbench` and making one-command setup safer for repositories outside the current shell directory.
- Codex and Cursor handoffs now reference the resolved workbench path, so custom output directories still pass `check --adapter all`.
- README and launch kit now state the MIT license explicitly, matching the trend signal that reuse rights should be clear before adoption.
- Python verification detection now avoids suggesting unittest discovery unless `tests/` exists, falling back to `compileall` for Python source-only repositories.
- Readiness JSON now includes `next_action` so downstream agent harnesses can route ready, failed, and warning-only states.
- Generated `AGENTS.md` and `agent-task-pack.md` now list the adapter handoff files when adapters are requested.
- `trend-lab insight`: summarize the latest decision JSON into a compact local product-iteration brief.
- English and Chinese README paths now use the shorter all-adapter demo command.
- Launch assets now describe the v0.8.0 first-run path.

## Adapter Output

`--adapter all` writes:

- `.agent-workbench/CLAUDE.md`
- `.agent-workbench/.codex/AGENTS.md`
- `.agent-workbench/.cursor/rules/agent-workbench.md`
- `.agent-workbench/opencode.json`

The core output remains provider-neutral: `AGENTS.md` and `agent-task-pack.md` are still plain Markdown.
