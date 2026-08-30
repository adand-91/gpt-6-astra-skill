<!-- translation-of: HANDOFF.md sha256:ec1c17643a9c1ce1 -->

# 交接

## 我们在做什么

- 目标：发布第一个可安装、Codex-first 点名目标审查预览版 `v0.2.0-alpha.1`，不混入后续本地
  Beta、RC 或 v0.3 工作。
- 本轮范围：把封存 `0.2.0a1` 源码恢复到干净的 `origin/main` 工作树，完善双语发布说明，增加
  逐门禁十天更新地图，并在 GitHub 预发布前走完整发布流程。
- 发布形态：注释 Tag `v0.2.0-alpha.1`、PEP 440 包版本 `0.2.0a1`、GitHub
  `prerelease=true`，且不作为最新稳定版。
- 不在范围：不建 Issue、PR，不发推广帖，不申请活动，不建定时任务，不遥测，不无人值守修改目标，
  不读无关历史，也不发布其他版本。

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
- 新增双语 `UPDATE_MAP` 并改写 `ROADMAP`：稳定 v0.2 是一个十天目标，Alpha 2、Beta 1、RC 1、
  RC 2 和稳定版都由退出门决定，不由日期单独决定。
- 扩展 CI 发布冒烟：安装构建 wheel，创建／校验点名审查，检查私有权限和不覆盖失败，并要求 sdist
  包含更新地图与审查测试。
- 发布清单新增 Alpha 专节；内部封存证据和含路径校验文件明确排除在公开资产之外。

## 卡在哪儿

- 当前阻断：精确发布 commit 尚未通过公开 Linux／macOS／Windows CI。
- 尚未关闭的发布门禁：最终本地构建与干净安装、commit／push、公开 CI、注释 Tag、GitHub
  预发布、公开资产重新下载、校验和复验，以及发布后证据 commit。
- Alpha 1 之后的产品缺口：安装包不会读取 Codex 历史，也不能初始化日报／周报；这些是可见目标，
  不是已交付声明。
- 采用证据缺口：不声称已有外部用户安装或重复使用。

## 下一步计划

1. 在本工作树运行全量源码测试、双语同步、编译、Skill 结构、diff／隐私复核和 Handoff 新旧时间检查。
2. 从最终源码构建 wheel 与 sdist；测试解压 sdist；分别干净安装；复验版本、确定性 Demo、审查创建／
   校验、`0600` 权限和不覆盖。
3. 生成只含文件名的 `SHA256SUMS`；确认资产和源码不含私有本机路径、任务标识、私有证据、字节码、
   缓存或后续版本模块。
4. 提交精确 Alpha 源码并推送 `main`；公开 CI 未完成或失败时不打 Tag。
5. 精确 commit 全绿后，创建并推送注释 Tag `v0.2.0-alpha.1`，用已验收 wheel、sdist 和校验文件
   创建非 latest 的 GitHub 预发布。
6. 重新下载公开资产，复核校验和与安装／冒烟，再把发布证据提交到 `main`，不移动发布 Tag。

## 踩过哪些坑

- 封存 Alpha 校验文件包含私有绝对路径。封存 wheel/sdist 的完整性有效，但该校验文件与内部证据／
  日志不能上传；公开资产重新构建，并生成只含文件名的新校验文件。
- 源码分发包不是 Git checkout。直接恢复会删除 CI／控制文件并加入生成元数据；发布重建只把真实
  源码覆盖到 `origin/main`。
- 维护者工作树已包含后续 Beta、RC 和 v0.3 模块。给其 HEAD 打 Tag 或整体提交 diff，会把后续功能
  错标成 Alpha 1；隔离工作树才是发布权威源。
- Alpha 带有日报／周报模板和校验词汇，但 CLI 会有意拒绝 `review-init --mode daily|weekly`；更新
  说明已明确写出。
- 更新地图中的天数是决策目标，不是发布承诺；空版本、回填日期和虚构维护均被排除。

## 当前任务汇总

- 状态：本地发布源码已准备，源码门禁全绿；公开发布尚未完成。
- 当前版本：包 `0.2.0a1`，计划注释 Tag `v0.2.0-alpha.1`；预发布复验前，公开稳定版仍为
  `v0.1.1`。
- 当前源码结果：112 项测试通过，双语同步通过，`git diff --check` 通过。
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

- 支持运行环境：Python 3.10–3.13；运行时依赖：仅 Python 标准库。
- 构建后端：通过 PEP 517 使用 setuptools；构建工具不是运行时依赖。
- 源码测试命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`。
- 双语门禁：`python3 scripts/check_translation_sync.py`。
- 构建命令：在隔离构建环境中运行 `python3 -m build --sdist --wheel`。
- CLI 冒烟：`requirement-ledger review-init ...`，随后运行
  `requirement-ledger review-check REPORT`。

## 验证证据

- 独立发布审计核验了封存 wheel、sdist、源码快照、版本和哈希，并在发布前发现绝对路径校验文件问题。
- 封存候选源码与解压 sdist 的 100 个打包文件逐字节一致；wheel 的 11 个 Python 模块与同一源码一致。
- 当前重建源码：112 项测试通过；`TRANSLATIONS_IN_SYNC`；`git diff --check` 退出 0；包版本报告
  `requirement-ledger 0.2.0a1`。
- 最终资产哈希和公开 CI 不写进本文件，因为它们只能在源码提交后产生；必须作为构建后与发布后
  证据附加／记录。

## 授权与禁止动作

- 已授权：准备并提交精确 Alpha 源码；推送 `main`；CI 通过后创建并推送注释 Alpha Tag；上传已
  验收 wheel、sdist 和校验文件；创建并复验 GitHub 预发布；提交事实性发布证据。
- 未授权：Issue、PR、推广帖、活动申请、定时任务、通知、无关／全量历史读取、其他版本、删除证据，
  或破坏性修改维护者工作树。
- 本地或公开门禁失败会停止 Tag／Release，不会授权削弱测试、改写证据或发布未完整检查的资产。

## 回滚

- 推送前，只在保留证据后移除隔离发布工作树／分支；维护者工作树与公开仓库不受影响。
- 推送后、打 Tag 前，通过新的经审查 commit 修复或回退；不改写历史或 force-push。
- 预发布后，`v0.1.1` 仍是最新稳定版。没有维护者另行决定时，不移动 Tag 或删除预发布；证据要求时
  发布纠正预发布版或事实性撤回说明。
