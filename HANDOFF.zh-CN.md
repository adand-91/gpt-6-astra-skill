<!-- translation-of: HANDOFF.md sha256:88ddbba21d4dca6e -->

# 交接

## 我们在做什么

- 目标：发布并核验 `v0.2.0-alpha.1`，再记录走向稳定 `v0.2.0` 的十个成功发布日路线。
- 发布结果：注释 Tag `v0.2.0-alpha.1`、PEP 440 包 `0.2.0a1`、非 latest 的 GitHub
  预发布，以及三项已公开重下载／复验资产。
- 本轮范围：提交事实性发布证据与维护者要求的每日候选序列；不移动已发布 Tag，也不混入后续本地
  Beta、RC 或 v0.3 草稿。
- 不在范围：不建 Issue、PR，不发推广帖，不申请活动，不自动建定时任务，不遥测，不无人值守修改，
  不读无关历史，不发空版本或回填日期。

## 完成了什么

- 从 `origin/main` 建立隔离发布工作树；维护者混有 Alpha 后改动的脏工作树没有被 reset、clean、
  stash，也没有作为发布输入。
- 恢复封存 Alpha 源码，同时保留仓库控制文件（`.github/**`、`.gitattributes`、`.gitignore`），
  排除 sdist 生成的 `PKG-INFO`、`setup.cfg` 和 `src/requirement_ledger.egg-info/**`。
- 包版本统一为 `0.2.0a1`；v0.1.1 CLI 与证据 Schema 保持兼容。
- 新增 `review-init --mode audit`：一个显式目标、半开时间窗口、IANA 时区；平台支持时使用私有
  权限；初始为零已读取来源、覆盖不完整、`analysis-only` 授权，且不覆盖已有输出。
- 新增 `review-check` 和委托给它的独立脚本。唯一包内校验器检查 Schema、模式、状态、目标、窗口
  顺序、offset／时区一致性、必需章节、证据标签、候选状态、生态字段、来源结构和授权。
- 新增双语宿主契约与一次性／日报／周报参考模板。Alpha 1 只初始化一次性审查；日报、周报是文档
  与校验面，不是安装版初始化模式。
- 双语 Alpha 更新说明改为“更新了什么／解决什么问题／快速开始／已验证门禁／已知限制”。
- 新增双语 `UPDATE_MAP` 并改写 `ROADMAP`。最终发布列车以每个成功发布日一个真实增量为目标：
  `alpha.1 → alpha.2 → alpha.3 → beta.1 → beta.2 → beta.3 → rc.1 → rc.2 → rc.3 → v0.2.0`。
- 扩展 CI 发布冒烟：安装构建 wheel，创建／校验点名审查，检查私有权限和不覆盖失败，并要求 sdist
  包含更新地图与审查测试。
- 首次公开 CI 在 Linux、macOS 通过，但证明 Windows Python 没有系统 IANA 时区数据库。修正后
  只在 Windows 声明 `tzdata>=2024.1`，矩阵安装平台依赖，并用回归让未装依赖时的错误可执行。
- 发布清单新增 Alpha 专节；内部封存证据和含路径校验文件明确排除在公开资产之外。
- 修正 commit `243b01ac5be88825ec4a1f4f9c5cec3b2841a90e` 已通过公开 CI run
  `33291029715`：Python 3.10–3.13 × Linux／macOS／Windows 及构建产物／安全冒烟全绿。
- 已创建注释 Tag 对象 `856f4d0fd198a74825f134289af3b0475042ec85` 和公开的非 latest
  [预发布](https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.1)。
- 已重新下载 wheel、sdist 与 `SHA256SUMS`，三项均与本地验收文件逐字节一致；两种压缩包均
  干净安装，并通过版本、Demo、审查初始化与报告校验。

## 卡在哪儿

- 当前阻断：Alpha 发布已无阻断。本次事实性证据／更新地图 commit 仍需进入 `main` 并通过自身
  CI，之后才能关闭隔离发布工作树。
- Alpha 1 之后的产品缺口：安装包不会读取 Codex 历史，也不能初始化日报／周报；这些是可见目标，
  不是已交付声明。
- 采用证据缺口：不声称已有外部用户安装或重复使用。

## 下一步计划

1. 对本次文档记录运行双语同步、113 项测试、diff 与 Handoff 时序校验；提交／推送到 `main`，
   不移动 Alpha Tag，并核验公开 CI。
2. 用新的精确候选边界开发 Alpha 2：一个显式有界 Codex 输入信封，包含身份／摘要、目标／窗口、
   纳入／排除覆盖，以及路径、大小和变化漂移失败门。
3. 后续只按 `UPDATE_MAP.zh-CN.md` 的每日序列推进；候选门禁失败就顺延全部依赖目标，不发布空
   Release。

## 踩过哪些坑

- 封存 Alpha 校验文件包含私有绝对路径。封存 wheel/sdist 的完整性有效，但该校验文件与内部证据／
  日志不能上传；公开资产重新构建，并生成只含文件名的新校验文件。
- 源码分发包不是 Git checkout。直接恢复会删除 CI／控制文件并加入生成元数据；发布重建只把真实
  源码覆盖到 `origin/main`。
- 维护者工作树已包含后续 Beta、RC 和 v0.3 模块。给其 HEAD 打 Tag 或整体提交 diff，会把后续功能
  错标成 Alpha 1；隔离工作树才是发布权威源。
- Alpha 带有日报／周报模板和校验词汇，但 CLI 会有意拒绝 `review-init --mode daily|weekly`；更新
  说明已明确写出。
- 更新地图中的天数指下一个成功发布日，不是无条件日历许可；空版本、回填日期、绕过失败门禁和
  虚构维护均被排除。
- 标准库 `zoneinfo` 在 Windows 上并非自带完整数据。“所有平台零运行时依赖”的说法掩盖了真实
  兼容要求；文档现已区分类 Unix 与 Windows，CI 也安装条件时区数据库。

## 当前任务汇总

- 状态：`v0.2.0-alpha.1` 已发布并独立重下载／复验；仅剩发布后证据／更新地图 commit 及其
  CI 这一项仓库收尾。
- 当前版本：包 `0.2.0a1`、已发布注释 Tag `v0.2.0-alpha.1`；最新稳定 Release 仍为
  `v0.1.1`。
- 已验证源码结果：113 项测试、完整跨平台 CI、wheel/sdist 干净安装、确定性 Demo、私有／不覆盖
  审查骨架和严格报告校验。
- 一句话结论：Alpha 1 是面向一个点名审查的可安装、隐私优先起点和机械契约检查器，尚不是自动
  上下文读取器或三模式调度器。

## 当前架构与入口

- CLI：`src/requirement_ledger/cli.py`；版本：`src/requirement_ledger/__init__.py`。
- Alpha 审查契约与骨架：`src/requirement_ledger/review.py`。
- 独立检查器：`scripts/check_review_report.py`；回归测试：`tests/test_review_report.py`。
- 宿主产品契约：`V0.2_HOST_CONTRACT.zh-CN.md`；模式／上下文／个性化资料位于 `references/`。
- 公开说明：`README.zh-CN.md`、`CHANGELOG.zh-CN.md`、`docs/release-notes/`、
  `UPDATE_MAP.zh-CN.md` 和 `ROADMAP.zh-CN.md`；英文权威文件与中文镜像并列维护。
- 发布政策与证据索引：`docs/RELEASE_CHECKLIST.md`。

## 运行与依赖

- 支持运行环境：Python 3.10–3.13。类 Unix 系统仅使用标准库；Windows 因操作系统没有 IANA
  时区数据库，按条件安装 `tzdata>=2024.1`。
- 构建后端：通过 PEP 517 使用 setuptools；构建工具不是运行时依赖。
- 源码测试命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`。
- 双语门禁：`python3 scripts/check_translation_sync.py`。
- 构建命令：在隔离构建环境中运行 `python3 -m build --sdist --wheel`。
- CLI 冒烟：`requirement-ledger review-init ...`，随后运行
  `requirement-ledger review-check REPORT`。

## 验证证据

- 独立发布审计核验了封存 wheel、sdist、源码快照、版本和哈希，并在发布前发现绝对路径校验文件问题。
- 封存候选源码与解压 sdist 的 100 个打包文件逐字节一致；wheel 的 11 个 Python 模块与同一源码一致。
- 初始 commit `a880e9b48c921f5c32c9e362f5848de420eb9f52`：CI run `33290681748` 的
  Linux／macOS 全部通过，Windows 全部在 IANA 时区加载失败，release-smoke 跳过；没有创建 Tag
  或 Release。
- 修正 Tag commit `243b01ac5be88825ec4a1f4f9c5cec3b2841a90e` 的 CI run
  `33291029715` 已通过 12 个 Python／OS 矩阵 job 与构建产物／安全冒烟。
- 公开 wheel SHA-256：
  `3123b30db1610e0b930c0d0f26a3a24ec3dbe47917d5da7d1f7c3b800dac615b`。
- 公开 sdist SHA-256：
  `1e5407f5f48d8bdd19f18749aa6bc978002415a90061426cf5bef9b40103ae05`。
- 公开 `SHA256SUMS` SHA-256：
  `c7f4789bc5d26fc686f49194f3da48d3426fd75c8326a1163b73edd627406011`。
- 公开下载与本地验收资产逐字节一致；校验和、双干净安装、版本、确定性 Demo、
  `review-init` 与 `review-check` 全部通过。

## 授权与禁止动作

- 本批已授权：增加／推送事实性发布证据与每日更新地图。维护者已要求十个成功发布日方向；每个
  精确候选仍必须具备真实增量、通过门禁、说明准确，并对精确 commit 做发布决定。
- 未授权：Issue、PR、推广帖、活动申请、定时任务、通知、无关／全量历史读取、删除证据，或破坏性
  修改维护者工作树。
- 本地或公开门禁失败会停止 Tag／Release，不会授权削弱测试、改写证据或发布未完整检查的资产。

## 回滚

- 事实／地图记录有误时，用新的经审查 commit 回退，不改写历史。
- 本批将已发布 Alpha Tag 与资产视为不可变。证据若失效，保留记录，并在维护者另行决定后发布
  纠正预发布或事实性撤回；绝不静默移动 Tag。
- 原始维护者脏工作树仍是 Alpha 后草稿的恢复源，不能 reset、clean、stash 或整体覆盖。
