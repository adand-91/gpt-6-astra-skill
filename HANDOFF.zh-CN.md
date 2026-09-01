<!-- translation-of: HANDOFF.md sha256:16c94bc0e1a5077c -->

# 交接

## 我们在做什么

- 发布剩余待发版本中的第一个 `v0.2.0-alpha.2`，不混入后续本地 Beta、RC、插件或 v1 改动。
- Alpha 2 的产品边界是：为用户点名的一份 Codex task 导出生成显式、有界、隐私优先的输入信封；
  它不是自动读取 Codex 历史或访问账号。
- 发布源码来自封存 Alpha 2 最终候选恢复成的隔离工作树；维护者累计脏工作树不是发布输入。

## 完成了什么

- 在隔离 `codex/release-v0.2.0-alpha.2` 工作树中，把封存 Alpha 2 源码恢复到
  `origin/main` 基线上。
- 包版本设为 `0.2.0a2`，新增 `codex-scan` 和 `src/requirement_ledger/codex_input.py`。
- 扫描器要求显式目标和半开时间窗口，记录来源身份与记录计数，识别畸形／越窗数据，并如实报告
  partial 或 unknown 覆盖，不虚构完整性。
- 输出用摘要代替原始目标字符串和来源路径；已有大小、不覆盖、安全写入和校验边界继续生效。
- 新增 `tests/test_codex_input_envelope.py`，同步更新 CLI、pipeline、transcript、安全 I/O、文档、
  威胁模型、架构、发布清单和双语契约。
- Python 3.12 下重新核验：122 项测试通过；刷新发布记录前，双语同步和 `git diff --check` 通过。
- 封存资产与冻结记录一致：
  - wheel SHA-256：`0190c7902e64ab8e8c98363421274d92343b974edf7bf53462ae2077d1d246cd`
  - sdist SHA-256：`ad888a21b17408d02a8a17120bc84cb9f9b0e2c53c7b57b4e906d31b4b95de6e`

## 卡在哪儿

- 当前没有已知本地产品阻断。候选 commit `c556704d19d813a9a414d011045d794dce06ef0d`
  已通过公开 CI；发布说明 commit 仍需自己的全绿 CI 才能打 Tag。
- 如果第一次 CI 后修改了会打包进分发物的发布文档，就必须从最终 Tag 源码重新构建公开资产。
- 候选 commit 的 Windows 原生覆盖已通过；最终精确 commit 的 CI 仍为硬门禁。
- 不声称已有外部用户采用、重复使用或 OpenAI 项目资格。

## 下一步计划

1. 更新双语指纹并重跑 122 项测试、diff 检查和 Handoff 时序校验。
2. 只把 Alpha 2 精确边界提交／推送到 `main`，等待公开跨平台 CI。
3. 全绿后只做事实性发布状态更新，从最终源码重建 wheel、sdist 和仅含文件名的
   `SHA256SUMS`，复验、推送并等待最终精确 commit 的 CI。
4. 创建注释 Tag `v0.2.0-alpha.2`，发布为非 latest 的 GitHub 预发布，再重新下载并核验全部
   资产以及 wheel/sdist 干净安装。
5. 在 Alpha 2 后停止，汇报 Release 链接、证据和最新 Stars／Forks／Watchers。

## 踩过哪些坑

- 活跃开发工作树包含后续待发版本；直接给它打 Tag 或整体提交会把后续代码错标为 Alpha 2，只有本
  隔离工作树中的封存快照有效。
- 测试会生成未跟踪 `__pycache__`；只能从本隔离工作树精确清理，不能广泛清理维护者工作树。
- 候选压缩包能证明产品边界，却不能代替公开来源证明；公开资产必须对应最终 Tag commit，并在发布后
  独立重下载。
- 本地 macOS 全绿不能代替 Linux／macOS／Windows CI；公开门禁失败就停止，不弱化测试、不移动 Tag。
- 内部校验记录可能带绝对路径；公开附件只能使用新生成、仅含文件名的 `SHA256SUMS`。

## 当前任务汇总

- 状态：Alpha 2 候选 commit 已进入 `main` 并通过公开 CI run `33468431105`；尚待最终发布说明
  commit／CI、Tag、Release、公开下载复验和最终汇报。
- 版本边界：包 `0.2.0a2`；目标注释 Tag `v0.2.0-alpha.2`；没有包含或授权后续版本。
- 本地门禁：Python 3.12 下 122 项测试、双语同步和 diff 检查通过；本次发布说明刷新后、推送前会
  重跑全部门禁。
- 发布前 GitHub 快照：47 Stars、1 Fork、0 Watchers；最新稳定版仍为 `v0.1.1`。
- 一句话结果：Alpha 2 把显式 Codex 导出变成有边界的证据信封，不假装读取完整历史，也不保留用户
  点名目标／路径原文。

## 当前架构与入口

- CLI 与路由：`src/requirement_ledger/cli.py`。
- Codex 输入边界：`src/requirement_ledger/codex_input.py`。
- 审查／报告管线：`src/requirement_ledger/pipeline.py`、`review.py`、`transcript.py`。
- 安全输出／错误契约：`src/requirement_ledger/safeio.py`、`errors.py`。
- 回归：`tests/test_codex_input_envelope.py` 及既有 `tests/`。
- 用户／发布说明：`README.zh-CN.md`、`CHANGELOG.zh-CN.md`、
  `docs/release-notes/v0.2.0-alpha.2.zh-CN.md` 及英文权威文件。

## 运行与依赖

- 支持 Python 3.10–3.13；Windows 条件安装 `tzdata>=2024.1`，类 Unix 系统使用标准库时区数据。
- 源码测试：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`。
- 双语门禁：`python3 scripts/check_translation_sync.py`。
- 构建：`python3 -m build --sdist --wheel`；构建工具不是运行时依赖。
- 发布冒烟必须干净安装两种压缩包，并覆盖版本、Demo、review 和 `codex-scan` 路径。

## 验证证据

- 私有发布归档保留封存 Alpha 2 源码快照；其本地路径不发布到本仓库。
- 封存 wheel：`requirement_ledger-0.2.0a2-py3-none-any.whl`，SHA-256
  `0190c7902e64ab8e8c98363421274d92343b974edf7bf53462ae2077d1d246cd`。
- 封存 sdist：`requirement_ledger-0.2.0-alpha.2.tar.gz`，SHA-256
  `ad888a21b17408d02a8a17120bc84cb9f9b0e2c53c7b57b4e906d31b4b95de6e`。
- 候选 commit `c556704d19d813a9a414d011045d794dce06ef0d` 已通过公开 CI run
  `33468431105`：Python 3.10–3.13 × Linux／macOS／Windows，以及构建产物／安全冒烟。
- 发布前本地结果：Python 3.12.13 下 122 项测试通过，双语与空白检查通过；最终 commit CI 和
  Release 下载证据要在真实产生后补记。

## 授权与禁止动作

- 已授权：提交／推送 Alpha 2 精确边界，等待 CI，创建 Alpha 2 注释 Tag 与非 latest 预发布，上传
  三项公开资产并复验公开下载。
- 未授权：发布后续待发版本、移动现有 Tag、建 Issue／PR、推广、改仓库名、提交插件、申请 OpenAI
  项目、发送外部消息，或 reset／clean／stash 维护者累计工作树。
- 源码不一致、本地／公开门禁失败、Tag／Release 冲突或疑似私密数据时，立即停止发布，只在同一
  Alpha 2 边界内诊断。

## 回滚

- 打 Tag 前用经过评审的前向 commit 修正错误，不改写共享历史。
- 打 Tag 后不移动或静默替换 Tag／资产；保留证据，若需纠正则另行取得新 Release 授权。
- 未触碰的累计开发工作树和封存最终候选目录都是恢复源，均不得破坏性清理。
