<!-- translation-of: README.md sha256:1f31d5a3e842eebd -->

# requirement-ledger

**一个让 Codex 或其他编程 Agent 持续优化任意 Git 项目的本地、隐私优先证据闭环。**
它把你明确提供的对话、错误、Git 状态和测试结果变成可追溯的问题候选、修复计划与前后对照证据。

[English](README.md) · [v0.1 契约](V0.1_CONTRACT.zh-CN.md) ·
[未完成项](docs/PROJECT_GAPS.md) · [安全政策](SECURITY.zh-CN.md)

> v0.1 不会自动修改项目。CLI 负责采集和组织证据；Codex 仍是开发者，任何真实修改都保持可见、
> 可审查。

## 为什么要做这个项目

AI 辅助项目往往把自己产生的最有价值信息丢掉了：

- 用户纠正了 Agent，但真实需求仍埋在聊天里；
- 同一个错误再次出现，却没人说得清它是上游通病、项目自身问题、个人配置问题，还是仍然未知；
- 没冻结 baseline，也没用同一个测试复验，就把补丁叫作“已修复”；
- 有价值的反馈没有到维护者手里，未经处理的真实日志却被直接贴进公开 Issue。

Requirement Ledger 把这个闭环显式化：

```text
显式 Codex/Claude/文本输入 + 测试日志 + 只读 Git 快照
  -> 私有证据
  -> 保守归因
  -> 不含原话的报告 + 修复草案
  -> 由宿主控制的 Codex 补丁
  -> 绑定摘要的 oracle 修改前后结果
```

它适用于普通软件项目。目标项目不需要使用 AI、Python 或本 Skill；只有证据采集器本身使用 Python。

## v0.1 已交付什么

- 零运行时依赖的标准包与 `requirement-ledger` 命令，支持 Python 3.10–3.13。
- 显式 Claude Code、Codex JSONL 和纯文本适配器，按事件过滤时间并检查输入读取时是否变化。
- 固定的只读 Git 快照：HEAD、status 摘要、脏文件数和跟踪文件数；绝不读取或输出 remote URL。
- 版本化的 `SourceRef`、`EvidenceItem`、`IssueRecord`、`FixProposal`、`ValidationResult`。
- `upstream`、`project-local`、`personal`、`unknown` 四类归因字段，并诚实地默认 `unknown`。
- 物理分离的私有证据与无原话报告、严格文件权限、不覆盖写入和失败即停止的隐私闸门。
- 标为 `DRAFT — NOT SENT`、`not-applied` 的修复计划；没有隐藏补丁、commit、push、Issue、
  PR、Release、上传或遥测。
- 完全合成、结果确定的端到端 Demo。

## 安装

克隆仓库并在本地安装：

```bash
git clone https://github.com/adand-91/requirement-ledger
cd requirement-ledger
python3 -m pip install .
requirement-ledger --version
```

运行时只使用 Python 标准库。构建隔离可能下载构建工具；已经准备好依赖的离线环境可以使用
`python3 -m pip install --no-build-isolation --no-deps .`。

### 安装 Codex 或 Claude Skill

本仓库同时也是完整的 Agent Skill：

```bash
# Codex
git clone https://github.com/adand-91/requirement-ledger ~/.codex/skills/requirement-ledger

# Claude Code
git clone https://github.com/adand-91/requirement-ledger ~/.claude/skills/requirement-ledger
```

Skill 会告诉宿主何时采集证据、何时停在方案，以及如何把审查后的计划交回正常开发流程。
它不会扩大任何权限。

## 60 秒合成 Demo

这条命令不会检查仓库、主目录或真实对话：

```bash
requirement-ledger demo --output-dir /tmp/requirement-ledger-demo
find /tmp/requirement-ledger-demo -maxdepth 1 -type f -print
```

它会生成五个文件：

```text
01-evidence.private.json   原始合成证据；私有格式
02-analysis.json           保守问题候选
03-proposals.json          DRAFT — NOT SENT、未应用的计划
04-report.md               不含原话的报告；仍需人工隐私复核
05-validation.json         合成的 baseline 失败 -> 修改后通过结果
```

源样例位于 [examples/anonymous](examples/anonymous/README.md)。

## 用在真实项目上

请亲自选择准确的仓库与证据文件。建议把私有证据放在项目目录之外：

```bash
requirement-ledger doctor --repo /path/to/project

requirement-ledger scan \
  --repo /path/to/project \
  --input /path/to/explicit-codex-or-claude-session.jsonl \
  --test-log /path/to/existing-test-output.log \
  --output /tmp/project-evidence.private.json

requirement-ledger analyze \
  --evidence /tmp/project-evidence.private.json \
  --output /tmp/project-analysis.json

requirement-ledger report \
  --analysis /tmp/project-analysis.json \
  --output /tmp/project-report.md

requirement-ledger suggest \
  --analysis /tmp/project-analysis.json \
  --output /tmp/project-proposals.json
```

`scan` 不会发现 `~/.codex`、`~/.claude` 或其他项目。JSONL 默认自动识别来源；文件名特殊时可用
`--provider codex|claude|text` 指定。ISO-8601 时间窗口按 JSONL 事件应用；纯文本没有时间戳，
所以会拒绝时间参数，而不是假装过滤成功。

### 不运行项目代码也能记录验证结果

v0.1 刻意不执行任意第三方项目测试。请让 Codex 或现有沙箱先冻结准确的 argv、工作目录、相关
环境与 fixture 摘要，把该描述做 SHA-256，然后在审查后的改动前后运行。两个小型 JSON 与命令行
都必须提供同一个 64 位十六进制摘要：

```json
{"oracle": "unit-regression", "oracle_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "exit_code": 1}
```

```json
{"oracle": "unit-regression", "oracle_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "exit_code": 0}
```

```bash
requirement-ledger verify \
  --oracle unit-regression \
  --oracle-digest aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  --baseline /tmp/baseline.json \
  --after /tmp/after.json \
  --output /tmp/validation.json
```

只有 oracle 名称和摘要都一致，并且从失败变成成功，才是 `improved`。身份不一致、布尔值／非整数
退出码或超出 0–255 的退出码都是 `inconclusive`；baseline 成功、修改后失败是 `regressed`。

## 不装懂的归因

每条问题把疑似范围和最终范围分开记录：

| 范围 | 确认条件 |
|---|---|
| `upstream` | 独立项目／会话、相同 provider／版本、清洁复现，并排除本地与个人原因 |
| `project-local` | 直接仓库证据，以及在其他地方不复现的清洁对照 |
| `personal` | 另行授权的个人配置证据或清洁配置对照 |
| `unknown` | 上述条件不成立时的默认值 |

一次抱怨不是上游结论，一次项目测试失败也不能证明依赖有错。证据不完整或相互冲突时禁止确认。
规范细节见 [v0.1 契约](V0.1_CONTRACT.zh-CN.md)。

## 隐私与安全

私有证据可能含用户原话，文件名必须以 `.private.json` 结尾；操作系统支持时会使用严格权限。
不要把它附到 Issue、PR、邮件或聊天中。

报告会排除原话、本地路径、会话 ID、命令参数、remote 和原始错误。写报告前，自动闸门会检查
常见秘密、认证／Cookie 请求头、邮箱、电话、主目录、带凭据 remote、UUID、IP 地址和终端
控制字符。命中后返回 `E_PRIVACY_BLOCK`，且不会创建报告文件。

**自动隐私检查通过不能证明文件可以安全分享。** 每份报告都会说明仍需人工复核。

v0.1 CLI 没有项目代码执行器、补丁应用器、依赖安装器、网络客户端、遥测、浏览器、GitHub 写入
或账号集成。唯一子进程通过可信绝对路径执行固定只读 Git 探针，并清除会重定向 Git 的环境变量。
输出父目录必须预先存在，独占写入前会检查每一级祖先。使用真实证据前请阅读
[威胁模型](docs/THREAT_MODEL.md)与[安全政策](SECURITY.zh-CN.md)。

## 旧版复盘工具

原始 Skill 流程继续作为兼容入口保留：

```bash
python3 scripts/scan_transcript.py path/to/session.jsonl
python3 scripts/check_retro_report.py path/to/report.md
python3 scripts/check_translation_sync.py
```

旧扫描器在显式使用 `--engine` 时仍能发现本地 Agent 目录。它的 `--no-text` 只删除消息／错误正文，
路径、会话元数据与命令形状仍可能存在，**绝不是 share-safe**。新工作流应使用标准包管线，并把
所有旧输出视为私有数据。

## 开发

```bash
python3 -m pip install --no-build-isolation --no-deps -e .
python3 -m unittest discover -s tests -v
python3 -m compileall -q src scripts tests
python3 scripts/check_translation_sync.py
```

所有样例必须完全合成。绝不要把真实对话、秘密、私有 remote、客户名、会话标识或个人路径放入
Issue 或测试。参见 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)、
[SUPPORT.zh-CN.md](SUPPORT.zh-CN.md)和[项目缺口账本](docs/PROJECT_GAPS.md)。

## 哪些部分是刻意没有完成的

v0.1 不提供安全的自主修改。在移动这条边界前，必须先有隔离后端、对象绑定批准令牌、冻结 oracle
执行、事务性应用与回滚故障注入。结构化测试适配器、清洁复现、日报／周报、可选采用证据、治理
与签名发布也仍未完成。

这些事项长期记录在 [docs/PROJECT_GAPS.md](docs/PROJECT_GAPS.md)，不让“看起来完整”冒充“已经完工”。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
