<!-- translation-of: README.md sha256:905a33f39920ffbf -->

# Astra Skill Doctor

### 面向 GPT-6／Astra 的 Skill 适配与个人工作流优化

Astra Skill Doctor 专门处理新 GPT-6／Astra 发布后旧 Skill 约束失真的问题。用户选定一个项目和相关 Skill 后，它输出有证据的适配判断、最小改动和可复核验证；长期发展为类似 Jarvis 的个人与社区 Skill 优化系统。

这里的“说人话”不等于把字数压到最少，而是先给结论，再提供足够的依据、影响、行动和验收说明，
让用户不需要翻译术语或继续追问，就能真正理解问题。

**Astra Skill Doctor 是当前产品和仓库的公开身份。** 旧 Python 包和 CLI 在迁移期间保留为兼容入口。

当前插件是轻量 Skill 工作流；完整的 GPT-6／Astra 适配仍需真实项目反馈验证。

[English](README.md) · [产品完工合同](docs/V1_PRODUCT_CONTRACT.zh-CN.md) ·
[稳定契约](docs/V1_STABLE_CONTRACT.zh-CN.md) ·
[路线图](ROADMAP.zh-CN.md) · [安全政策](SECURITY.zh-CN.md) · [Codex 对齐调研](docs/CODEX_ALIGNMENT_RESEARCH.zh-CN.md)

> 仓库命名迁移与历史发布记录分开维护。

## 为什么需要它

长期 AI 辅助项目很容易把决定埋进聊天：当前目标发生漂移，旧要求被重新当成事实，修问题时误删有效能力，
或者把摘要误当成“报告真实且已获批准”的证明。Astra Skill Doctor 为 GPT-6/Astra 提供一条窄审查链：

```text
一个已选目标
  -> 目标和当前阶段
  -> 主要问题和必须保留的行为
  -> 一项可审查改进
  -> 明确下一步与权限
  -> 可选的精确来源绑定和交接检查
```

它不会发现所有任务、扫描主目录、编辑目标，也不会把分析变成权限。

## 快速接管 Codex 项目

安装核心和插件，选中一个 Codex 任务或项目，再新开一个任务并输入：

```text
嗨，贾维斯，接管这个已选项目。恢复它的目标、当前阶段、卡点和唯一下一步。
不要修改项目。
```

若宿主没有自动选择 Skill，可显式重试一次：
`$requirement-ledger-workflow 嗨，贾维斯，接管这个已选项目。`

首屏应该像下面这样，而不是先让用户提供 JSONL 路径或 schema 字段：

```text
# 项目总目标
……
## 项目总进度：约 60%（估算）
██████░░░░
当前工作区域：……
## 当前区域进度：约 80%（估算）
████████░░
当前卡点：当前无阻断问题。
你现在无需操作。
# 下一步
……
完成标准：……
```

这个快速结果只是 Codex 的决策辅助，属于 `host-selected / unbound`。只有证据状态或权限会改变
下一步时，才在正文里用人话说明；首屏不固定显示技术元数据。它不是 CLI 创建的来源包、最终报告或交接身份。

## 三种回答深度

贾维斯不会每收到一句话就输出完整项目卡。

| 你需要什么 | 贾维斯怎么回 |
| --- | --- |
| 一个明确答案 | 先直接回答，只补充决定性原因或实际影响。 |
| 把问题解释清楚 | 结论、必要原因或证据、实际影响和接下来的动作。 |
| 接管、完整进度或项目关键节点 | 完整八项汇报，包含两个进度条、唯一下一步和完成标准。 |

日报和周报保留各自的固定排版。日报最后只留一项价值最高的下一步；周报最多可排三项下周行动。
两种报告都不会机械地在开头加上日常项目卡。

## 六类项目管理场景

贾维斯会从日常表达中选择一个主要场景，不会先要求用户理解或选择内部工作流。

| 用户怎么说 | 主要场景 | 得到什么 |
| --- | --- | --- |
| “接管这个项目。” | 首次建档 | 目标、阶段、证据新鲜度、权限、卡点和第一项动作 |
| “今天推进了什么？” | 进度复盘 | 周期、已完成、变化、风险和下一周期唯一重点 |
| “客户把需求改了。” | 需求变化 | 旧／新要求、影响、失效假设、决定和安全下一步 |
| “为什么卡住了？” | 卡点诊断 | 症状、事实、复现状态、候选原因、缺失证据和下一项检查 |
| “这个版本能发吗？” | 版本验收 | 范围与标准，并分开通过／失败／跳过／未知 |
| “生成一份交接。” | 换对话交接 | 目标、决定、未完成、风险、证据入口和新任务首句 |

普通汇报后最多显示三个与当前阶段相关的建议。只有用户问“你还能做什么”时，才展开完整菜单。
遇到陌生实现时，贾维斯可以先查现有 Skill、官方工具、GitHub 原项目、文档和相关公开论坛，再说明哪些值得复用；
发现候选不等于自动安装或运行。用户明确提出的修正和已复现的失败可以变成聚焦改进候选；贾维斯不会宣称被动观察、
自动记忆或在后台自学习。日报和周报可以随时生成；无人值守发送仍需单独配置计划任务和通知路径。

## 两级审查

| 级别 | 何时使用 | 输入 | 如实结果 |
| --- | --- | --- | --- |
| **Codex 快速审查** | 现在就要得到下一项维护决定。 | 一个由宿主选中的任务或项目；无需额外时间窗、JSONL、范围根或文件路径。 | 人话、`analysis-only`、`host-selected`、`unbound`；动态状态在核验前保持 `partial`、`unstable` 或 `unknown`。 |
| **证据绑定审查** | 结果必须可复验或需要交接。 | 明确目标、半开时间窗、IANA 时区、非主目录范围根、精确文件及可选候选状态。 | 私有来源包、通过检查的最终报告、精确绑定和只读交接复验。 |

v1 CLI 的 `review-init --mode audit` 属于第二级，因此仍要求显式 `--start`、`--end` 和
`--timezone`。插件绝不能暗示快速审查已经通过证据绑定链。

完整目标体验和发布门见[贾维斯 v1 产品完工合同](docs/V1_PRODUCT_CONTRACT.zh-CN.md)。
本地 Python 版本 `1.0.0` 是稳定技术核心，不等于全部产品门和公开发布门已经通过。

## 为什么以 Codex 为先

- 入口是一个已选中的 Codex 任务／项目加一次显式 Skill 调用；用户无需先学新表格，才能得到有用答案。
- 插件是轻量、纯 Skill 的 Codex 分发层；确定性 schema、隐私边界、过期状态拒绝、精确字节绑定和
  验证仍在独立可测试的普通 Python CLI 中。
- 宿主文本、仓库指令、工具输出和旧报告都只是证据，不是新权限；这与 Codex 的明确审批和分层指令
  模型一致。
- 这不是 Claude Code 移植版。Anthropic 的公开 Skills 示例只用于打包调研；v1 不依赖 Claude 专属
  Hook、插件运行时或配置，也不复制任何 Anthropic Skill 文本或代码。我们的差异是“指令之外还有
  可执行验证”，而不是空泛宣称某个编码 Agent 在所有场景都更强。

事实／项目决定／未知项的区分见 [Codex 对齐调研](docs/CODEX_ALIGNMENT_RESEARCH.zh-CN.md)。

## 架构

```text
Codex 宿主已选上下文 --快速审查--> 人话、未绑定决定

明确目标／窗口／文件
  -> 独立 requirement-ledger CLI
  -> 来源包 + 候选延续 + 最终报告
  -> 精确审查绑定 + 只读交接检查
  -> 宿主另行获授权后实施
```

仓库内插件保持轻量，不包含第二运行时、App、Hook、插件自有认证／凭据流、更新器、模型调用、遥测、
数据库或网络客户端。规范边界见 [v1 稳定契约](docs/V1_STABLE_CONTRACT.zh-CN.md)。

## 本地安装核心

### macOS + Homebrew Python

在此 checkout 中使用隔离工具环境：

```bash
uv tool install .
requirement-ledger --version
```

此 macOS checkout 已用 `uv tool install .` 成功安装 `requirement-ledger 1.0.0`。Homebrew 管理的
Python 遵循 PEP 668，可能拒绝系统级 `pip install`；本项目不要使用 `--break-system-packages`。

### 已有虚拟环境

```bash
python3 -m pip install .
requirement-ledger --version
```

核心使用 Python 标准库。Windows 安装还会获得小型条件依赖 `tzdata`，以便使用 IANA 审查窗口。
旧公开 Alpha wheel 不是这个本地候选。

## 安装或刷新本地 Codex 插件

```bash
codex plugin marketplace add /absolute/path/to/requirement-ledger
codex plugin add requirement-ledger@requirement-ledger-local
codex plugin list --marketplace requirement-ledger-local
```

Codex 会安装带版本的插件快照。本地开发时，编辑此 checkout 不能证明新任务已经加载改变后的 Skill
字节。如果同一个未发布版本已经安装，应显式刷新，然后新建 Codex 任务：

```bash
codex plugin remove requirement-ledger@requirement-ledger-local
codex plugin add requirement-ledger@requirement-ledger-local
```

以 `codex plugin --help` 作为本机命令权威。移除插件不会卸载 Python 包。

## 证据绑定 CLI 工作流

把私有来源包、候选状态、报告和绑定放在同一个获批准的非主目录范围中。以下每个占位符都必须替换为
一个明确本地值。

```bash
# 1. 创建并验证有界 audit 骨架。
requirement-ledger review-init --mode audit --target project:example \
  --start 2026-08-01T08:00:00+08:00 --end 2026-08-02T08:00:00+08:00 \
  --timezone Asia/Shanghai --output /approved/review/final-report.md
requirement-ledger review-check /approved/review/final-report.md

# 2. 只绑定所选文件，然后验证其当前字节。
requirement-ledger source-pack --target project:example --scope-root /approved/review \
  --source /approved/review/input.jsonl --output /approved/review/sources.private.json
requirement-ledger source-verify --pack /approved/review/sources.private.json \
  --target project:example --scope-root /approved/review \
  --source /approved/review/input.jsonl

# 3. 延续精确候选状态，检查完整报告，绑定并复验交接。
requirement-ledger candidate-sync --target project:example --scope-root /approved/review \
  --current /approved/review/current-candidates.private.json \
  --output /approved/review/candidates.private.json
# 用完整的 status=final 报告替换骨架后：
requirement-ledger review-check /approved/review/final-report.md
requirement-ledger review-bind --target project:example --scope-root /approved/review \
  --report /approved/review/final-report.md --source-pack /approved/review/sources.private.json \
  --source /approved/review/input.jsonl --candidate-state /approved/review/candidates.private.json \
  --output /approved/review/review-binding.private.json
requirement-ledger review-handoff-check --binding /approved/review/review-binding.private.json \
  --target project:example --report /approved/review/final-report.md \
  --source-pack /approved/review/sources.private.json --scope-root /approved/review \
  --source /approved/review/input.jsonl --candidate-state /approved/review/candidates.private.json
```

`review-handoff-check` 默认阻断不完整证据。`--allow-incomplete-archive` 只用于归档不完整身份，
不会授权实施或发布。

## 兼容性与边界

- v0.1 CLI 仍可用于显式证据、保守归因、修复草案，以及外部记录的前后 oracle 结果。
- CLI 不运行项目代码、不应用补丁、不修改工作树、不 commit、不 push、不建 Issue、不发布 Release、
  不上传数据，也不使用遥测。
- 私有证据和来源包可能包含敏感关联或摘要；机械检查通过不等于获得公开许可。
- SHA-256 摘要只证明所选输入内的字节／状态身份，不能证明真实性、作者、完整性、语义正确性、批准
  或执行权限。
- 当前候选的 Windows 原生故障注入测试尚未在 Windows 上执行；macOS skip 不是跨平台证据。

自动化此工作流前，请阅读 [稳定契约](docs/V1_STABLE_CONTRACT.zh-CN.md)、
[威胁模型](docs/THREAT_MODEL.md) 和 [发布清单](docs/RELEASE_CHECKLIST.md)。
