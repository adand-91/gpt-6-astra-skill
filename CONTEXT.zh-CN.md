<!-- translation-of: CONTEXT.md sha256:86e722442ce5a0ef -->

# 项目上下文

这是简短接手索引；私有证据保留在仓库之外。

## 当前检查点

- `v0.2.0-alpha.3`（`0.2.0a3`）已作为非 latest GitHub 预发布公开。Tag commit：
  `dfa04a0d21ff0aca5c97d87b40546c58fe39d199`；注释 Tag 对象：
  `af32da5b81c12317177042875ffd08a8f03b816c`。
- Alpha 3 为支持的现代 Codex rollout 记录增加有界归一化：有序完成项目快照、turn 终点、
  结构化排除、严格记录守恒、规范元组身份和 1,000,000 条记录工作上限。
- 重建源码已通过 132 项源码测试、19 项归一化／信封专项测试、翻译同步、编译、构建、干净安装、
  隐私与确定性输出检查。准确的最终 commit 必须在 Tag 前通过公开 Linux／macOS／Windows CI。
- 维护者累计的后续 Alpha 脏工作树保持不动。Beta、RC、稳定版、Jarvis 与后续易用性改动均不属于
  Alpha 3。
- Tag commit 已通过最终公开 CI `33708129443` 与 `33708228485`：12 组 Python 3.10–3.13 ×
  Linux／macOS／Windows 任务及构建产物／安全冒烟全部成功。三份公开资产均已重新下载、核对哈希，
  并通过干净安装验证。

## 接手文件

- 变更：`CHANGELOG.md`；发布说明：`docs/release-notes/v0.2.0-alpha.3.md`
- 发布页：<https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.3>
- 现代归一化：`src/requirement_ledger/transcript.py` 与 `src/requirement_ledger/codex_input.py`
- 回归测试：`tests/test_codex_modern_normalization.py` 与 `tests/test_codex_input_envelope.py`
- 发布门禁：`docs/RELEASE_CHECKLIST.md`；技术状态：`HANDOFF.md`

## 下一步

停在已经完成的 Alpha 3 发布，汇报证据和当前 GitHub 数据。后续排队版本继续按正常节奏发布；
较大的 Jarvis／易用性改动继续留到 `v1.0.0-rc.1`。

## 安全边界

不要移动已有 Tag 或替换已发布资产。不要带入后续排队版本，不推广、不改仓库名、不提交插件或项目
申请、不创建 Issue／PR、不发送外部消息，也不改动维护者累计开发工作树。
