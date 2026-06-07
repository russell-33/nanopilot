# NanoPilot

`NanoPilot` 是一个面向代码仓库的轻量本地 coding agent。它直接跑在终端里，先看当前工作区，再用一组受约束的工具去读文件、改文件、跑命令，并把会话状态保存在本地 `.nanopilot/` 目录里。

它更像一个能在仓库里持续工作的命令行助手，不是纯聊天窗口。你可以拿它做代码排查、测试修复、仓库分析，或者让它在当前项目里执行一次性的工程任务。

## 适合做什么

- 在本地仓库里排查测试失败
- 读取当前代码结构并给出修改建议
- 基于现有文件做小步迭代，而不是脱离仓库空想
- 在会话中保留上下文，支持继续上一次工作

## 主要特性

- 包名是 `nanopilot`
- CLI 命令是 `nanopilot`
- 模块入口是 `python -m nanopilot`
- 会话保存在 `.nanopilot/sessions/`
- 每次运行的工件保存在 `.nanopilot/runs/<run_id>/`
- 支持四类模型后端：
  - Ollama
  - OpenAI 兼容 Responses API
  - Anthropic 兼容 Messages API
  - DeepSeek Anthropic 兼容 API

## 安装

需要 Python 3.10+。以下命令都在项目根目录执行。

如果你用 `uv`，先确保本机已经安装 `uv`：

```bash
brew install uv
```

然后同步环境：

```bash
uv sync
```

如果你使用普通 Python 环境，建议先创建并激活虚拟环境，再装成可编辑模式：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## 快速开始

在当前仓库里启动交互模式。当前推荐使用 DeepSeek：

```bash
uv run nanopilot --provider deepseek
```

指定另一个工作目录：

```bash
uv run nanopilot --cwd /path/to/repo
```

直接跑一次性任务：

```bash
uv run nanopilot --provider deepseek "inspect the test failures and propose a fix"
```

如果当前环境已经安装过包，也可以直接这样启动：

```bash
python -m nanopilot --provider deepseek
```

## 模型后端

NanoPilot 启动时会读取项目根目录的 `.env`。本地真实 key 放在 `.env`，仓库只保留 `.env.example`。配置优先级是：

```text
显式 CLI 参数 > .env 里的 NANOPILOT_* 变量 > 旧环境变量 > 代码默认值
```

本地第一次配置：

```bash
cp .env.example .env
```

然后把要使用的 provider key 填进去。`.env` 已经被 `.gitignore` 忽略，不要提交真实 key。

### Ollama

```bash
ollama serve
ollama pull qwen3.5:4b
uv run nanopilot --provider ollama --model qwen3.5:4b
```

### OpenAI 兼容接口

默认 OpenAI 兼容接口使用 right.codes 的 Codex endpoint：

```bash
NANOPILOT_OPENAI_API_BASE="https://www.right.codes/codex/v1"
NANOPILOT_OPENAI_API_KEY="your-api-key"
NANOPILOT_OPENAI_MODEL="gpt-5.4"
```

也可以改成其他 OpenAI-compatible 服务：

```bash
NANOPILOT_OPENAI_API_BASE="https://your-api.example/v1"
NANOPILOT_OPENAI_API_KEY="your-api-key"
NANOPILOT_OPENAI_MODEL="gpt-5.4"
```

```bash
uv run nanopilot --provider openai
```

### Anthropic 兼容接口

默认 Anthropic 兼容接口使用 right.codes 的 Claude endpoint：

```bash
NANOPILOT_ANTHROPIC_API_BASE="https://www.right.codes/claude/v1"
NANOPILOT_ANTHROPIC_API_KEY="your-api-key"
NANOPILOT_ANTHROPIC_MODEL="claude-sonnet-4-6"
```

```bash
uv run nanopilot --provider anthropic
```

如果你的服务端对多个兼容接口复用了同一套密钥，`nanopilot` 也支持从 `NANOPILOT_ANTHROPIC_API_KEY` 回退到 `ANTHROPIC_API_KEY`、`NANOPILOT_RIGHT_CODES_API_KEY`、`RIGHT_CODES_API_KEY`、`NANOPILOT_OPENAI_API_KEY` 或 `OPENAI_API_KEY`。

### DeepSeek

```bash
NANOPILOT_DEEPSEEK_API_KEY="your-api-key"
NANOPILOT_DEEPSEEK_MODEL="deepseek-v4-pro"
```

```bash
uv run nanopilot --provider deepseek
```

默认 DeepSeek base URL 是 `https://api.deepseek.com/anthropic`，走 DeepSeek 的 Anthropic 兼容接口。如果需要改到代理服务，可以设置 `NANOPILOT_DEEPSEEK_API_BASE` 或启动时传 `--base-url`。

## 常用交互命令

- `/help`：查看内置命令
- `/memory`：查看提炼后的工作记忆
- `/session`：查看当前会话文件路径
- `/reset`：清空当前会话状态
- `/exit` 或 `/quit`：退出 REPL

## 安全与持久化

`NanoPilot` 不会默认把所有动作都放开。像 shell 执行、文件写入这类高风险操作，会受审批模式控制：

- `--approval ask`
- `--approval auto`
- `--approval never`

每次运行结束后，都会在 `.nanopilot/runs/<run_id>/` 下写出这些文件：

- `task_state.json`
- `trace.jsonl`
- `report.json`

这些内容默认只保存在本地，不需要跟仓库一起提交。

## 开发

如果装了 Ruff，可以这样检查：

```bash
uv run ruff check .
```
