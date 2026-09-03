<!-- translation-of: HANDOFF.md sha256:1632e48447e80fd8 -->

# 交接说明

## 我们在做什么

- 把 `v0.2.0-alpha.3` 作为现有版本列车的下一个非 latest 预发布版公开。
- 它唯一的产品增量是对受支持现代 Codex rollout 记录做有界归一化。
- 从 `origin/main` 在独立工作区重建，保留公开的 Alpha 2 记录，也不触碰维护者后续累计工作。

## 完成了什么

- 已核验唯一冻结 Alpha 3 源码、wheel、sdist 与校验值。
- 只复用经审计的 Alpha 2 到 Alpha 3 实现、测试、CI、契约和发布说明增量；排除生成的 egg-info
  及所有 Beta／RC／v1／Jarvis 改动。
- 已加入 `codex-modern-normalization/v1`、`codex-input-envelope/v2`、有序 item／terminal 核算、
  结构化排除、规范元组哈希、严格输入／状态校验、准确记录守恒和 1,000,000 条记录工作上限。
- 重建文档保留 Alpha 2 的公开 Tag、CI、资产哈希和重新下载证据。
- 已重跑 132 项源码测试、19 项专项测试、翻译同步、编译和差异检查。新 wheel 与 sdist 均报告
  `0.2.0a3`；干净安装、确定性 Demo、审查、不覆盖、私有权限、现代信封隐私与解包 sdist 测试通过。
- 初始发布 commit `5d97742` 已通过公开 CI `33707942357`：12 组 Python 3.10–3.13 ×
  Linux／macOS／Windows 任务及构建产物／失败即停安全冒烟全部成功。
- 已在 commit `dfa04a0d21ff0aca5c97d87b40546c58fe39d199` 创建注释 Tag 对象
  `af32da5b81c12317177042875ffd08a8f03b816c`，并作为非 latest
  [GitHub 预发布](https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.3)公开。
- 三份公开资产均已重新下载且哈希一致；wheel 与 sdist 都干净安装为 `0.2.0a3`，下载后的 wheel
  通过确定性 Demo、审查、现代信封隐私和 item／terminal 断言。

## 卡在哪儿

- 当前没有已知源码设计阻断。
- Alpha 3 发布已无阻断，只剩把真实发布记录写回并通过 CI。
- 外部用户采用和 OpenAI 项目资格仍未证明，也不是本版本声明。

## 下一步计划

1. 提交并向 `main` 推送本真实发布记录，不移动不可变 Tag。
2. 核验记录 CI，汇报发布数据，然后停止。
3. 较大的 Jarvis／易用性改动留到 `v1.0.0-rc.1`；更早的候选按正常节奏发布，仍需分别授权。

## 踩过哪些坑

- 冻结 Alpha 3 源码早于 Alpha 2 公开发布，错误地把 Alpha 2 写成未发布。只能复用其已审计增量，
  不能用整个快照覆盖 `origin/main`。
- 修正公开文档会改变 sdist，因此冻结候选归档不能直接作为最终公开资产；必须从准确 Tag commit 重建。
- 活跃开发工作树包含后续排队版本，绝不能把它用于 Alpha 3 Tag，也不能清理或重置。

## 当前任务汇总

- 状态：`v0.2.0-alpha.3` 已公开并独立重新下载验证；只剩本真实发布记录及其 CI。
- 版本边界：包版本 `0.2.0a3`；计划 Tag 为 `v0.2.0-alpha.3`。
- 本地发布证据：132 项源码测试、19 项专项测试、构建、双归档干净安装、确定性 Demo、审查、
  隐私与失败即停检查均已通过。
- 公开发布证据：最终 CI `33708129443` 与 `33708228485` 已通过；公开资产哈希记录如下并已独立核验。
- 已授权：准确 Alpha 3 commit／push／Tag／预发布／资产／重新下载验证及真实发布记录。未授权：后续
  版本、推广、改名、插件／项目申请、Issue、PR 或无关外部消息。

## 当前架构与入口

- CLI／路由：`src/requirement_ledger/cli.py` 与 `src/requirement_ledger/pipeline.py`。
- 输入边界：`src/requirement_ledger/codex_input.py`。
- 现代 rollout 适配：`src/requirement_ledger/transcript.py`。
- 回归测试：`tests/test_codex_modern_normalization.py`、`tests/test_codex_input_envelope.py`
  及现有 `tests/` 全套。

## 运行与依赖

- 支持 Python 3.10–3.13；Windows 按条件使用 `tzdata>=2024.1`。
- 源码测试：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`。
- 翻译门禁：`python3 scripts/check_translation_sync.py`。
- 构建：`python3 -m build --sdist --wheel`；构建工具不是运行时依赖。

## 验证证据

- 冻结 wheel SHA-256：`a46fa9b62dd5c8e702419743e312820214c5527f1da7d7405f26b3769e224b99`。
- 冻结 sdist SHA-256：`5c813a5fc3cf6f93f187b2cf02fe345e0f4be381567c8d2618faa57060601687`。
- 冻结 wheel 的 Python 模块和冻结 sdist 的共有文件均与源码快照逐字节一致。以下公开哈希从
  Tag commit 生成。
- 公开 wheel SHA-256：`c809a6bd92810a8509401e0d7c93eb976d073db5aafa8d97244c941a929ea7ec`。
- 公开 sdist SHA-256：`1a7deb8725ada52470f0b9739b93aaea47659eedf75b2bf475774b3576d2a740`。
- 公开校验文件 SHA-256：`18083577d5bb9fcd4020be11a8cab0900904d23e9bb0e9db605b2894f54f8164`。

## 授权与禁止动作

- 已授权：发布准确 Alpha 3 边界并做公开验证。
- 未授权：发布后续版本、移动旧 Tag、替换旧资产、推广、改名、提交插件／项目申请、创建
  Issue／PR，或修改脏开发工作树。

## 回滚

- Tag 前若门禁失败，用经过复核的前向 commit 修复，或停止发布。
- Tag 后绝不移动或静默替换 Tag／资产；如需修正，使用另行授权的更正版本。
