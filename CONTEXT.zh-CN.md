<!-- translation-of: CONTEXT.md sha256:73542ae870479e09 -->

# 项目上下文

这里只放简短接手索引；私有证据留在仓库外。

## 当前检查点

- `v0.2.0-alpha.2`（`0.2.0a2`）已作为非 latest 的 GitHub 预发布公开。Tag 所在 commit：
  `fb49947627516bca463094becde16a63d047e2d6`；注释 Tag 对象：
  `00fb12747e93f9c48f24c434b5d329fbdad57bf4`。维护者累计脏工作树保持原样。
- Alpha 2 新增显式有界 `codex-scan` 输入信封：任务／目标摘要、半开时间窗口、记录计数，以及如实
  标记的 partial／unknown 覆盖；不保留原始目标文字或本地路径。
- 恢复源码已通过 Python 3.12 下的 122 项测试、双语同步和 `git diff --check`；封存 wheel 与
  sdist 的 SHA-256 与记录一致。
- Tag 所在 commit 已通过公开 CI runs `33468720368`、`33468928114`：Python 3.10–3.13 ×
  Linux／macOS／Windows 及构建产物／安全冒烟。三项公开资产均已重下载、核对哈希，并通过 wheel／
  sdist 干净安装与 Alpha 2 命令链。

## 接手文件

- Release：<https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.2>
- 变更：`CHANGELOG.zh-CN.md`；发布说明：`docs/release-notes/v0.2.0-alpha.2.zh-CN.md`
- 输入实现：`src/requirement_ledger/codex_input.py`；CLI：`src/requirement_ledger/cli.py`
- 回归：`tests/test_codex_input_envelope.py`；发布门禁：`docs/RELEASE_CHECKLIST.md`
- 每日列车：`UPDATE_MAP.zh-CN.md`；技术状态：`HANDOFF.zh-CN.md`

## 下一步

停在已完成的 Alpha 2 发布并汇报证据。Alpha 3 是地图中的下一个候选，但实施或发布需要用户另行
下达指令。

## 安全边界

不得移动 Alpha 2 Tag 或替换资产。后续版本、Issue、PR、推广、仓库改名、插件提交、项目申请、
无关历史读取，以及破坏性修改维护者工作树仍不在范围内。
