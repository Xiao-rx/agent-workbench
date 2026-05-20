# Agent Workbench

[English](README.md)

这是 Agent Workbench 的完整中文 README。主 README 也保留了中文介绍，方便中文用户在项目首页第一屏就理解它的用途。

用一条命令把任意代码仓库变成 AI coding agent 可以安全接手的工作区。

Agent Workbench 是一个 provider-neutral 的 Python CLI。它扫描仓库结构、包管理器、测试命令和本地风险信号，然后生成适合交给 coding agent 的工作资料：

- `AGENTS.md`：仓库地图、安全命令、高信号文件和操作护栏。
- `agent-task-pack.md`：首批任务、验收门槛和交付前检查清单。
- 可选 `CLAUDE.md`、Codex instructions、Cursor rule 和 `opencode.json`：给 Claude Code / Codex / Cursor / OpenCode 的轻量 handoff。
- 现有 agent 资产探测：识别 `AGENTS.md`、`CLAUDE.md`、`.codex/AGENTS.md`、`.cursor/rules/*.md`、`.github/copilot-instructions.md`、`GEMINI.md` 和 `opencode.json`。
- `scan --format json`：给脚本和下游工具复用的机器可读仓库地图。

默认输出不绑定任何模型、供应商或 agent 工具；你可以先用纯 Markdown 工作，再按需生成 Claude Code、Codex、Cursor 或 OpenCode 适配文件。

## 快速试用

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter all --strict --print-kickoff
```

这会创建一个无 secret 的示例仓库，并生成：

```text
.agent-workbench/
  AGENTS.md
  agent-task-pack.md
  CLAUDE.md
  .codex/AGENTS.md
  .cursor/rules/agent-workbench.md
  opencode.json
```

普通文本输出也会打印 `Proof:` 行，内容和 JSON 里的 `proof_summary` 对齐，并包含 adapter 与现有 agent asset 数量；运行 readiness check 时还会带上 readiness 数量；如果启用了 check、adapter 或 strict gate，还会给出可复制的 readiness gate 命令。
demo 仓库内置一个安全的 `.github/copilot-instructions.md`，生成结果会直接展示现有 agent 资产探测效果。

## 在当前仓库生成工作区

```powershell
agent-workbench init . --output .agent-workbench --project-name my-repo --check
```

相对 `--output` 会解析到目标仓库根目录内，所以 `agent-workbench init C:\path\to\repo --output .agent-workbench` 会写入 `C:\path\to\repo\.agent-workbench`。
生成的 Codex 和 Cursor handoff 会指回同一个解析后的 workbench 路径，即使输出目录不是默认的 `.agent-workbench`。

生成 Claude Code、Codex、Cursor 和 OpenCode handoff：

```powershell
agent-workbench init . --output .agent-workbench --adapter all
```

`--adapter all` 会一次生成 Claude Code、Codex、Cursor 和 OpenCode 的轻量适配文件。
`--print-kickoff` 会把生成的 kickoff prompt 直接打印到终端，方便立刻交给 coding agent。

如果想把 demo 或 init 结果交给脚本或下游 agent harness，可以输出 JSON：

```powershell
agent-workbench demo --proof
agent-workbench demo --report
agent-workbench init . --output .agent-workbench --proof
agent-workbench init . --output .agent-workbench --report
```

`demo --proof [PATH]` 会写出 strict all-adapter JSON proof，适合截图、CI 和下游 agent harness 复用，并且会在 stdout 打印同一份可复制的 `Proof:` 摘要和 `Proof command:` 复现命令。省略 `PATH` 时，proof 会保存到生成 workbench 目录里的 `demo-proof.json`。
`demo --report [PATH]` 会写出无 secret 的 Markdown demo report，包含生成文件、readiness 状态、readiness gate、现有 agent 资产和 kickoff prompt；它默认走和 `--proof` 一样的 strict all-adapter demo 路径，省略 `PATH` 时会保存到生成 workbench 目录里的 `demo-report.md`。
`init --proof [PATH]` 也会写出可分享的 JSON init proof，并默认把文件保存到生成 workbench 目录里。
`init --report [PATH]` 会为真实仓库写出 Markdown init report，包含生成文件、readiness 状态、readiness gate、现有 agent 资产和 kickoff prompt；省略 `PATH` 时会保存到生成 workbench 目录里的 `init-report.md`。
JSON proof 会包含 `kind`、`schema_version`、写入文件列表、简要 artifact summary、带有 `AGENTS.md`、`agent-task-pack.md` 和 `next_action` 的 `handoff` 对象、写入前已经存在的 `agent_assets`、可复制的 `proof_summary`、使用快捷参数时可复现的 `proof_command`、首个 verification command（如果存在）、check 运行后的 `readiness_summary` 和 `readiness_counts`、会保留 adapter 和 strict 门槛的 `readiness_command` 与结构化 `readiness_args`、kickoff prompt，以及可选 readiness。
scan JSON 也会包含 `kind`、`schema_version` 和 `agent_assets`，方便下游 agent harness 判断当前 payload 类型，以及仓库里是否已经有 Claude、Codex、Cursor、Copilot、Gemini 或 OpenCode 指令资产。
Python verification command 只会在匹配路径存在时报告：有 `tests/` 时使用 unittest discovery，否则有 Python 源码时退到 `compileall`。
如果希望 warning 也让 demo/init proof 失败，可以使用 `--strict`；它会自动运行 readiness check。

只查看仓库扫描结果：

```powershell
agent-workbench scan .
agent-workbench scan . --format json
agent-workbench scan . --output-json .agent-workbench/repo-map.json
```

检查当前仓库是否已经可以交给 agent：

```powershell
agent-workbench check .
agent-workbench check . --format json
agent-workbench check . --strict --format json
agent-workbench check . --adapter all --format json
agent-workbench check . --output-json .agent-workbench/readiness.json
```

如果存在 Claude Code、Codex、Cursor 或 OpenCode handoff 文件，`check` 也会一起验证这些适配文件是否指向核心 workbench；用 `--adapter all` 可以要求四类 handoff 都必须存在。
在 CI 里可以加 `--strict`，让 warning 也把仓库判为 `not_ready`，例如缺少 `.gitignore` 或存在本地 secret 风险文件时硬拦。
JSON readiness 报告会包含 `kind`、`schema_version`、`counts` 和 `next_action`，下游 agent harness 可以不用解析人类文本，就知道下一步是交给 agent、刷新 workbench，还是先处理 warning。
所有命令里，`--output-json PATH` 都会自动切到 JSON 输出，所以 CI 和脚本不需要再额外写 `--format json`。

## 真实示例

- Python 输入仓库：[`examples/python-cli/source`](examples/python-cli/source)
- Python 生成结果：[`examples/python-cli/agent-workbench/AGENTS.md`](examples/python-cli/agent-workbench/AGENTS.md)
- TypeScript 输入仓库：[`examples/typescript-cli/source`](examples/typescript-cli/source)
- TypeScript 生成结果：[`examples/typescript-cli/agent-workbench/AGENTS.md`](examples/typescript-cli/agent-workbench/AGENTS.md)

## 为什么值得用

AI coding agent 最容易在缺少上下文时犯错。Agent Workbench 的目标不是成为另一个 agent，而是先给现有仓库生成一份短、准、可检查的操作手册，让 agent 在动手前知道：

- 这个仓库大概是什么结构。
- 应该运行哪些验证命令。
- 哪些文件最值得先看。
- 哪些本地 secret、缓存或环境文件不能碰。
- 本轮任务怎样才算交付完成。

## 当前版本

- 下一版 release notes: [`docs/release-v0.8.0.md`](docs/release-v0.8.0.md)
- Launch kit: [`docs/launch-kit.md`](docs/launch-kit.md)
- 当前已发布 release: <https://github.com/Xiao-rx/agent-workbench/releases/tag/v0.7.0>
- 许可证：[`MIT`](LICENSE)，复用权利明确。

## 凭据与 secret

Agent Workbench 产品 CLI 不需要任何 token；`scan`、`init`、`check`、`demo --proof` 和 `demo --report` 都只处理本地文件。

只有内部 trend / monitor 命令为了提高 GitHub API 限额或采样目标仓库时才需要可选凭据。需要时复制安全样板：

```powershell
Copy-Item .env.example .env.local
```

`.env.example` 只包含占位符，可以提交；真实 token 只放进 `.env.local`。`.env.local` 和 `.env.bak` 都会被 git 忽略，本地 verification 会在发布前检查这些文件仍然被忽略。

## 内部增长闭环

这个仓库还包含一个内部 GitHub trend / feedback loop，用来观察热门项目、生成方向建议、记录 star history，并决定 Agent Workbench 下一轮应该改什么。

本地可以用 `python -m github_trend_lab insight --decisions reports/daily-decisions.json` 快速查看最新决策摘要，再决定下一轮产品改动。

趋势分析不是产品本体。产品本体是 Agent Workbench CLI。
