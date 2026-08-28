<!-- translation-of: docs/use-cases/improve-an-agent-skill.md sha256:90d8b50a764f9275 -->
# 用合成证据改进 Codex 或 Claude Skill：案例

这是 Requirement Ledger v0.1.1 的完全合成、可公开、可复现案例。它演示：收到一次明确纠正后，获授权的 host 如何改进一个小型 agent `SKILL.md`；Requirement Ledger 始终只是离线证据和规划工具。

下文没有真实对话、仓库、客户、会话、路径、密钥或测试结果。发布演示时，不要把案例输入或输出位置替换成私有材料。

## 结果

合成 Skill 最初要求 agent 扩大 retry helper 的改动范围。合成用户纠正要求保留公共 API 和依赖，只调整重试上限。最终改动是对 Skill 的小而可审查的编辑，把这条纠正固化成明确约束。一个由 host 在 CLI 外部运行的确定性 oracle 在编辑前失败、编辑后通过。

这**不能**证明是上游缺陷。一段已提供对话和一次本地 oracle 不足以做该归因；除非另行满足 v0.1 的确认条件，候选必须保守地保持为 `unknown`。

## v0.1 边界与职责

| 活动 | 负责者 | v0.1 状态 |
| --- | --- | --- |
| 绑定明确指定的 Git 工作树并收集已提供文件 | `requirement-ledger` | 只读 Git 快照；证据保持私有 |
| 生成分析、无引用报告和修复提案 | `requirement-ledger` | 生成候选分析和 `DRAFT — NOT SENT` / `not-applied` 计划 |
| 解读纠正并审查提案 | 人与 host agent | 语义修改前必需 |
| 编辑合成 `SKILL.md` | 获明确实施授权后的 Codex/Claude host | 可见的普通仓库修改；不是 CLI 功能 |
| 运行 oracle 并记录前后退出码 | Host 或既有沙箱 | CLI 外部操作 |
| 比较两份记录的结果 | `requirement-ledger verify` | 不执行 oracle |

CLI 不会应用 Skill 补丁、运行项目代码、安装依赖、提交、推送、发布，或访问网络/账号。隐私检查通过也不等于获得分享授权。

## 合成输入

以下配置应在同一个 shell 会话中执行，会生成隔离的临时 Git fixture，内容均为虚构。`case_root` 是新建的临时目录，不是真实仓库，也不是 home 目录路径。

```bash
case_root="$(mktemp -d /tmp/requirement-ledger-skill-case.XXXXXX)"
mkdir -p "$case_root/evidence" "$case_root/private" "$case_root/review"
git init "$case_root"

printf '%s\n' \
  '# Retry helper editing' \
  '' \
  'When asked to improve the retry helper, broaden the change across public functions if useful.' \
  > "$case_root/SKILL.md"

printf '%s\n' \
  '# User' \
  '' \
  'Please improve the retry helper.' \
  '' \
  '# Assistant' \
  '' \
  'I changed every public function and added a dependency.' \
  '' \
  '# User' \
  '' \
  'Keep the public API and dependencies unchanged; only stop retrying after the configured limit.' \
  > "$case_root/evidence/transcript.md"

printf '%s\n' \
  'FAILED synthetic_skill_oracle - required narrow-change constraints are absent' \
  > "$case_root/evidence/baseline-test.log"

cat > "$case_root/oracle.py" <<'PY'
from pathlib import Path

skill = Path("SKILL.md").read_text(encoding="utf-8")
required = (
    "Keep the public API and dependencies unchanged.",
    "Only change retry behaviour so it stops after the configured limit.",
)
raise SystemExit(0 if all(text in skill for text in required) else 1)
PY

git -C "$case_root" add SKILL.md oracle.py
git -C "$case_root" -c user.name='Synthetic Example' -c user.email='synthetic@example.invalid' commit -m 'synthetic baseline'
```

对话和基线日志是明确传给 `scan` 的输入。`oracle.py` 是刻意极小的合成 oracle，不是 agent 运行时，也不是 Requirement Ledger 组件。

## 可复现的证据与规划命令

请先按仓库 README 在本地安装 Requirement Ledger。随后在同一 shell 会话执行下列命令；它们只使用 v0.1.1 已有的 CLI 选项。

```bash
requirement-ledger doctor --repo "$case_root"

requirement-ledger scan \
  --repo "$case_root" \
  --input "$case_root/evidence/transcript.md" \
  --provider text \
  --test-log "$case_root/evidence/baseline-test.log" \
  --output "$case_root/private/skill-evidence.private.json"

requirement-ledger analyze \
  --evidence "$case_root/private/skill-evidence.private.json" \
  --output "$case_root/private/skill-analysis.json"

requirement-ledger report \
  --analysis "$case_root/private/skill-analysis.json" \
  --output "$case_root/review/skill-report.md"

requirement-ledger suggest \
  --analysis "$case_root/private/skill-analysis.json" \
  --output "$case_root/private/skill-proposals.json"
```

不要把输出目录名当成隐私边界。`.private.json` 证据包可能含有原始输入文本，必须保持私有；本案例的 analysis 与 proposal 同样是本地审查材料。输出路径必须是新路径，且父目录必须预先存在。

## 预期公开输出摘要

面向公开的报告刻意不含原文引用，且仍要求人工审查。它应概述一个候选问题：用户要求的是狭义 retry 改动，但先前回答做了扩大改动；并应指出需要保持 API 与依赖边界。报告不得重现对话、本地路径、命令参数、Git remote 数据、会话 ID 或原始报错文字。

私有产物用途不同：

- `skill-evidence.private.json`：可追溯的私有证据包。
- `skill-analysis.json`：保守分析；不得从这一案例制造已确认归因。
- `skill-proposals.json`：`DRAFT — NOT SENT` 修复计划，所有动作均为 `not-applied`。
- `skill-report.md`：无引用报告，不是“可以安全分享”的声明。

如果只想获得完全固定的输出演示、不想创建临时 Git fixture，可运行内置的独立合成 walkthrough：

```bash
requirement-ledger demo --output-dir /tmp/requirement-ledger-demo
```

它产生文档所述的五个合成文件：私有证据、分析、提案、报告与验证。它适合产品导览；上面的 fixture 则演示 host 负责的 Skill 编辑闭环。

## 由 host 负责的 Skill 修改

若用户只授权分析，应在 `suggest` 后停止。若用户明确授权实施，host 应先检查提案、仓库自身规则和 dirty 状态，然后只做能编码本次纠正的最小改动，不自行外推。

本 fixture 中，获授权的 host 将 `SKILL.md` 内那条宽泛指令替换为以下两行：

```markdown
Keep the public API and dependencies unchanged.
Only change retry behaviour so it stops after the configured limit.
```

Host 应审查可见 diff，并保留无关工作。本案例并不授予 Requirement Ledger 修改任何真实 Codex/Claude Skill 的权限，也不授权 commit、push、release、Issue、PR、上传、遥测或发布。

## 同一 oracle 验证

Host（不是 Requirement Ledger）在编辑前冻结 oracle 描述。此处描述是公开且刻意简单的：argv 为 `python3 oracle.py`，工作目录为 `$case_root`，没有相关环境变量，fixture 为 `oracle.py` 的 SHA-256。Host 先计算文件摘要并放入描述，再计算描述摘要，并在 Skill 编辑前后运行完全相同的 oracle。

```bash
oracle_file_digest="$(shasum -a 256 "$case_root/oracle.py" | awk '{print $1}')"
oracle_descriptor="argv=python3 oracle.py;cwd=case-root;env=none;fixture_sha256=$oracle_file_digest"
oracle_digest="$(printf '%s' "$oracle_descriptor" | shasum -a 256 | awk '{print $1}')"

if (cd "$case_root" && python3 oracle.py); then
  baseline_exit=0
else
  baseline_exit=$?
fi
printf '{"oracle":"synthetic-skill-constraints","oracle_digest":"%s","exit_code":%s}\n' \
  "$oracle_digest" "$baseline_exit" > "$case_root/private/baseline.json"
```

在获授权 host 完成编辑后，运行同一命令并记录第二个结果：

```bash
if (cd "$case_root" && python3 oracle.py); then
  after_exit=0
else
  after_exit=$?
fi
printf '{"oracle":"synthetic-skill-constraints","oracle_digest":"%s","exit_code":%s}\n' \
  "$oracle_digest" "$after_exit" > "$case_root/private/after.json"

requirement-ledger verify \
  --oracle synthetic-skill-constraints \
  --oracle-digest "$oracle_digest" \
  --baseline "$case_root/private/baseline.json" \
  --after "$case_root/private/after.json" \
  --output "$case_root/private/skill-validation.json"
```

按照指定基线和精确编辑，外部生成的基线退出码为 `1`，编辑后为 `0`；所以 `verify` 可以记录 `improved`。它只比较两份 JSON 记录，既不运行 `python3 oracle.py`，也不应用编辑，更不能证明修改后的 Skill 在一般情形有效。oracle 名、描述摘要或记录形状改变会得到 `inconclusive`；基线通过、修改后失败是 `regressed`。

## 隐私警告

除非有人审查了具体材料并单独授权披露，否则不要把对话输入、测试日志、私有证据、分析、提案、oracle 记录或本地审查笔记放进公开 Issue、PR、聊天或附件。真实案例应将证据包存放在目标仓库外、用户私有的位置。

Requirement Ledger 的报告 gate 能检测多种常见敏感模式，但自动通过只表示 `AUTOMATED_CHECK_PASSED_REVIEW_REQUIRED`，绝不表示“可以安全分享”。不要拿 legacy retrospective 输出替代它：legacy 的 `--no-text` 输出也不是 share-safe。

## 本案例体现的 v0.1 限制

- 输入必须明确指定；CLI 不会发现 Codex/Claude 历史、home 目录或其他仓库。
- CLI 只执行固定的只读 Git probes；不会运行合成 oracle 或任意项目测试。
- 一次纠正和一次本地失败只能产生证据与候选，不能确认 `upstream`、`project-local` 或 `personal`。
- `suggest` 生成本地草案，不是已应用补丁或已发送维护者报告。
- Host 的编辑需另行授权、可见且可审查。
- `verify` 比较由相同 64 个十六进制字符的 oracle 摘要绑定的外部记录；它不是测试运行器。
- 本流程不会 commit、push、创建 Issue/PR/Release、上传数据、使用遥测或调用网络服务。
