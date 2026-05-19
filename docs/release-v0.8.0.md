# Agent Workbench v0.8.0

Agent Workbench v0.8.0 makes the complete first-run path shorter with an `--adapter all` shortcut.

## Demo

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter all --check
```

## What Changed

- `--adapter all`: generate Claude Code, Codex, and Cursor handoff files in one option.
- Duplicate adapter requests are deduplicated, so `--adapter all --adapter codex` still writes each adapter once.
- Generated `AGENTS.md` and `agent-task-pack.md` now list the adapter handoff files when adapters are requested.
- English and Chinese README paths now use the shorter all-adapter demo command.
- Launch assets now describe the v0.8.0 first-run path.

## Adapter Output

`--adapter all` writes:

- `.agent-workbench/CLAUDE.md`
- `.agent-workbench/.codex/AGENTS.md`
- `.agent-workbench/.cursor/rules/agent-workbench.md`

The core output remains provider-neutral: `AGENTS.md` and `agent-task-pack.md` are still plain Markdown.
