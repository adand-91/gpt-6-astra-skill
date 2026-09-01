<!-- translation-of: HANDOFF.md sha256:9599ea17b22a59d9 -->

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
- 已把注释 Tag 对象 `00fb12747e93f9c48f24c434b5d329fbdad57bf4` 建在 commit
  `fb49947627516bca463094becde16a63d047e2d6`，并发布为非 latest 的
  [GitHub 预发布](https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.2)。
- 三项公开资产均已重下载且哈希一致；两种包均干净安装为 `0.2.0a2`，Demo、审查初始化／校验、
  `codex-scan`、私有权限、信封断言与不覆盖行为全部通过。

## 卡在哪儿

- Alpha 2 发布已无阻断；仅剩提交本次事实性发布记录这一项仓库收尾。
- 不声称已有外部用户采用、重复使用或 OpenAI 项目资格。

## 下一步计划

1. 更新双语指纹并运行 diff／Handoff 检查，把本次事实性发布记录提交／推送到 `main`，不移动
   已发布的 Alpha 2 Tag。
2. 核验该记录的 CI，然后停止并汇报 Release 链接、证据和最新 Stars／Forks／Watchers。
3. Alpha 3 只作为未来地图候选保留；没有用户新指令就不实施、不发布。

## 踩过哪些坑

- 活跃开发工作树包含后续待发版本；直接给它打 Tag 或整体提交会把后续代码错标为 Alpha 2，只有本
  隔离工作树中的封存快照有效。
- 测试会生成未跟踪 `__pycache__`；只能从本隔离工作树精确清理，不能广泛清理维护者工作树。
- 候选压缩包能证明产品边界，却不能代替公开来源证明；公开资产必须对应最终 Tag commit，并在发布后
  独立重下载。
- 本地 macOS 全绿不能代替 Linux／macOS／Windows CI；公开门禁失败就停止，不弱化测试、不移动 Tag。
- 内部校验记录可能带绝对路径；公开附件只能使用新生成、仅含文件名的 `SHA256SUMS`。

## 当前任务汇总

- 状态：`v0.2.0-alpha.2` 已发布并独立重下载／复验；仅剩本次事实性发布记录及其 CI。
- 版本边界：包 `0.2.0a2`；目标注释 Tag `v0.2.0-alpha.2`；没有包含或授权后续版本。
- 已验证门禁：122 项本地测试、完整 Python 3.10–3.13 × Linux／macOS／Windows 公开 CI，以及
  构建产物／安全冒烟均在 Tag commit 上通过。
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
- Tag 所在 commit `fb49947627516bca463094becde16a63d047e2d6` 已通过公开 CI runs
  `33468720368`、`33468928114`：Python 3.10–3.13 × Linux／macOS／Windows，以及构建
  产物／安全冒烟。
- 公开 wheel SHA-256：`6dbb7b104a4a094138b87a0931d60030f58b3f8cfd6188f575fad9cae9c9094c`；
  sdist：`d50b607a18e910d4c4be1d0d9658fd58ad33330da9b7191cc063efc30e188d62`；校验文件：
  `b19d5981b643bbcc5c929b28a852aa73a26eaad09098f83c55d29809907275f0`。
- 公开下载与批准文件逐字节一致，并通过干净安装与 Alpha 2 命令／隐私冒烟。

## 授权与禁止动作

- 本批授权已完成：Alpha 2 精确边界、CI、注释 Tag、非 latest 预发布、三项公开资产、独立下载
  复验及本次事实性仓库记录。
- 未授权：发布后续待发版本、移动现有 Tag、建 Issue／PR、推广、改仓库名、提交插件、申请 OpenAI
  项目、发送外部消息，或 reset／clean／stash 维护者累计工作树。
- 不移动已发布 Alpha 2 Tag，也不替换公开资产。

## 回滚

- 打 Tag 前用经过评审的前向 commit 修正错误，不改写共享历史。
- 打 Tag 后不移动或静默替换 Tag／资产；保留证据，若需纠正则另行取得新 Release 授权。
- 未触碰的累计开发工作树和封存最终候选目录都是恢复源，均不得破坏性清理。
