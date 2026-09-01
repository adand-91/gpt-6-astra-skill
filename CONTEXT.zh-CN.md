<!-- translation-of: CONTEXT.md sha256:2152348592ca8f24 -->

# 项目上下文

这里只放简短接手索引；私有证据留在仓库外。

## 当前检查点

- `v0.2.0-alpha.2`（`0.2.0a2`）已从封存的最终候选快照恢复到基于 `origin/main` 的隔离发布
  工作树；维护者累积了 Alpha 后改动的脏工作树保持原样。
- Alpha 2 新增显式有界 `codex-scan` 输入信封：任务／目标摘要、半开时间窗口、记录计数，以及如实
  标记的 partial／unknown 覆盖；不保留原始目标文字或本地路径。
- 恢复源码已通过 Python 3.12 下的 122 项测试、双语同步和 `git diff --check`；封存 wheel 与
  sdist 的 SHA-256 与记录一致。
- 候选 commit `c556704d19d813a9a414d011045d794dce06ef0d` 已通过公开 CI run
  `33468431105`：Python 3.10–3.13 × Linux／macOS／Windows 及构建产物／安全冒烟。最终发布
  文档 CI、注释 Tag、GitHub 预发布和公开下载复验仍待完成。

## 接手文件

- 变更：`CHANGELOG.zh-CN.md`；候选说明：`docs/release-notes/v0.2.0-alpha.2.zh-CN.md`
- 输入实现：`src/requirement_ledger/codex_input.py`；CLI：`src/requirement_ledger/cli.py`
- 回归：`tests/test_codex_input_envelope.py`；发布门禁：`docs/RELEASE_CHECKLIST.md`
- 每日列车：`UPDATE_MAP.zh-CN.md`；技术状态：`HANDOFF.zh-CN.md`

## 下一步

提交发布说明，在精确的发布分支 commit 上运行公开 CI，再快进 `main`。门禁失败就停止创建 Tag 和
Release；全绿后只允许创建 Alpha 2 注释 Tag、预发布、资产及独立下载复验。

## 安全边界

本批只授权 `v0.2.0-alpha.2` 的提交、推送、Tag、预发布、资产和验证。后续版本、Issue、PR、推广、
仓库改名、插件提交、项目申请、无关历史读取，以及破坏性修改维护者工作树仍不在范围内。
