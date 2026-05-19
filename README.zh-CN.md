# Agent Workbench

[English](README.md)

用一条命令把任意代码仓库变成 AI coding agent 可以安全接手的工作区。

Agent Workbench 是一个 provider-neutral 的 Python CLI。它扫描仓库结构、包管理器、测试命令和本地风险信号，然后生成适合交给 coding agent 的工作资料：

- `AGENTS.md`：仓库地图、安全命令、高信号文件和操作护栏。
- `agent-task-pack.md`：首批任务、验收门槛和交付前检查清单。
- 可选 `CLAUDE.md` 和 Cursor rule：给 Claude Code / Cursor 的轻量 handoff。
- `scan --format json`：给脚本和下游工具复用的机器可读仓库地图。

默认输出不绑定任何模型、供应商或 agent 工具；你可以先用纯 Markdown 工作，再按需生成 Claude Code 或 Cursor 适配文件。

## 快速试用

```powershell
uv tool install git+https://github.com/Xiao-rx/agent-workbench.git
agent-workbench demo --adapter claude --adapter cursor
```

这会创建一个无 secret 的示例仓库，并生成：

```text
.agent-workbench/
  AGENTS.md
  agent-task-pack.md
  CLAUDE.md
  .cursor/rules/agent-workbench.md
```

## 在当前仓库生成工作区

```powershell
agent-workbench init . --output .agent-workbench --project-name my-repo
```

生成 Claude Code 和 Cursor handoff：

```powershell
agent-workbench init . --output .agent-workbench --adapter claude --adapter cursor
```

只查看仓库扫描结果：

```powershell
agent-workbench scan .
agent-workbench scan . --format json
```

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

- Release notes: [`docs/release-v0.3.0.md`](docs/release-v0.3.0.md)
- Launch kit: [`docs/launch-kit.md`](docs/launch-kit.md)
- 最新 release: <https://github.com/Xiao-rx/agent-workbench/releases/tag/v0.3.0>

## 内部增长闭环

这个仓库还包含一个内部 GitHub trend / feedback loop，用来观察热门项目、生成方向建议、记录 star history，并决定 Agent Workbench 下一轮应该改什么。

趋势分析不是产品本体。产品本体是 Agent Workbench CLI。
