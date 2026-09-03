<!-- translation-of: CONTEXT.md sha256:69cd45d97d95c207 -->

# 项目上下文

这是简短接手索引；私有证据保留在仓库之外。

## 当前检查点

- 正在从 `origin/main` 的独立发布工作区重建 `v0.2.0-alpha.3`（`0.2.0a3`），并保留不可变的
  Alpha 2 公开发布记录。
- Alpha 3 为支持的现代 Codex rollout 记录增加有界归一化：有序完成项目快照、turn 终点、
  结构化排除、严格记录守恒、规范元组身份和 1,000,000 条记录工作上限。
- 重建源码已通过 132 项源码测试、19 项归一化／信封专项测试、翻译同步、编译、构建、干净安装、
  隐私与确定性输出检查。准确的最终 commit 必须在 Tag 前通过公开 Linux／macOS／Windows CI。
- 维护者累计的后续 Alpha 脏工作树保持不动。Beta、RC、稳定版、Jarvis 与后续易用性改动均不属于
  Alpha 3。

## 接手文件

- 变更：`CHANGELOG.md`；发布说明：`docs/release-notes/v0.2.0-alpha.3.md`
- 现代归一化：`src/requirement_ledger/transcript.py` 与 `src/requirement_ledger/codex_input.py`
- 回归测试：`tests/test_codex_modern_normalization.py` 与 `tests/test_codex_input_envelope.py`
- 发布门禁：`docs/RELEASE_CHECKLIST.md`；技术状态：`HANDOFF.md`

## 下一步

提交并推送已通过本地验证的源码，要求公开跨平台 CI 通过；若发布状态更新令 commit 变化，则再次
通过 CI。之后才创建注释 Tag 和非 latest 的 GitHub 预发布，并上传重新构建的资产。

## 安全边界

不要移动已有 Tag 或替换已发布资产。不要带入后续排队版本，不推广、不改仓库名、不提交插件或项目
申请、不创建 Issue／PR、不发送外部消息，也不改动维护者累计开发工作树。
