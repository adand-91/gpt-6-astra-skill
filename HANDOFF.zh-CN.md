<!-- translation-of: HANDOFF.md sha256:cd8de2057f6017c2 -->

# HANDOFF

## 我们在做什么

- 目标：发布 `v0.1.1`，把产品明确定位为 Requirement Ledger AI，并用完全合成的 Skill 改进案例证明现有证据闭环可以服务 Codex／Claude host 的获授权修改。
- 本轮范围：搜索与首次使用定位、15 天技术路线、版本单一来源、双语案例、变更日志、Release Notes、构建与发布验证。
- 不在范围：自动修改 Skill／项目、自动运行第三方代码、自动 GitHub 动作，以及日报／周报等 `v0.2.0` 功能。

## 完成了什么

- 修改：产品名与 README 首屏改为 Requirement Ledger AI；包描述和关键词覆盖 AI、Skill、Codex、Claude Code、反馈闭环与项目优化搜索入口。
- 新增：`ROADMAP.md`／中文镜像、完全合成的双语 Skill 改进案例，以及 `v0.1.1` Release Notes。
- 版本：`__version__` 升为 `0.1.1`，模型记录与构建元数据均从这一唯一来源读取；仓库 slug、包名和 CLI 均保持兼容。
- 案例：完整实跑 `doctor -> scan -> analyze -> report -> suggest -> host edit -> verify`，得到基线 `1`、修改后 `0`、`improved`、`unknown`，且报告未包含原始失败文本。
- 验证：97 项单测、翻译同步、编译、diff、wheel/sdist、两个干净安装、确定性 Demo 与 sdist 内容检查全部通过。

## 卡在哪儿

- 当前阻断：无代码阻断；公开发布必须等待 release commit 的 GitHub CI 全绿。
- 尚未验证：`v0.1.1` 的公开 CI、公开 Release 资产重下载与外部真实用户路径。

## 下一步计划

1. 提交并推送当前候选，等待同一 commit 的完整公开 CI。
2. CI 全绿后创建 annotated tag `v0.1.1` 与 GitHub Release，上传从 release commit 构建的 wheel/sdist。
3. 重新下载公开资产，核对哈希、安装、版本与 Demo，再记录发布证据。
4. 发布后进入 `v0.2.0`：日报、周报、人工确认的问题分组与首批结构化测试适配器。

## 踩过哪些坑

- 失败／误判：文档曾声称发布门通过，但根目录没有 Handoff，随后 transcript 加固又引入未闭合 `try` 的语法错误，导致新 CLI 无法导入。
- 跨平台发现：Windows checkout 的 CRLF 转换会改变双语源文件哈希；仓库现在用 `.gitattributes` 固定文本 LF，并升级 CI Actions 到当前 Node 24 主版本。
- Windows 发现：Python 3.12/3.13 对同一文件的路径 stat 与句柄 stat 可报告不同的非内容字段；transcript 和 test-log 绑定现在都用 `os.path.samestat` 判断身份，以 size/mtime 判断内容稳定性，并保留读前读后检查。
- 以后如何避免：状态文档不能替代当前命令证据；每次程序修改后先跑完整测试与翻译检查，再刷新 Handoff；发布只接受同一 commit 的 CI 结果。
- 维护边界：不把已经完成的功能拆成虚假版本，也不按日期制造空提交。定时任务只做真实检查，无真实变更就不发布。
- 本轮发现：最小临时 venv 可能没有 setuptools，`--no-build-isolation` 会因此失败；干净构建环境必须先具备声明的构建工具。案例中的预期失败也必须用 `if` 捕获，才能兼容启用 `set -e` 的 shell。
- 路线口径：15 天可以完成经过技术发布门的 `v1.0.0`，但不能制造外部采用或长期维护证据；这些属于发布后的真实指标。

## 当前任务汇总

- 状态：`v0.1.1` 本地 Release Candidate 已完成，等待提交、公开 CI 与正式发布。
- 当前有效产物：英语权威 README／Roadmap／案例／Release Notes、同步中文镜像，以及通过本地验证的 `0.1.1` wheel/sdist。
- 一句话结论：本批真实增加了可发现定位、Skill 使用闭环和 15 天正式版路线；尚未对外宣称发布。

## 当前架构与入口

- 项目根目录：当前 Git 仓库根目录。
- 主入口：`requirement-ledger` console command；源码入口为 `src/requirement_ledger/cli.py`。
- 关键数据流：显式项目和证据 → 私有 evidence → 保守 analysis → 无原话 report 与未应用 proposal → 外部同一 oracle 的 baseline/after 验证。
- 权威契约：`V0.1_CONTRACT.md`；15 天路线：`ROADMAP.md`；剩余工作：`docs/PROJECT_GAPS.md`；维护边界：`MAINTENANCE.md`。

## 运行与依赖

- 环境：Python 3.10–3.13；当前本地验收使用 Python 3.12.13、macOS arm64。
- 依赖：核心运行时仅 Python 标准库；构建时使用 PEP 517 与 setuptools。
- 运行命令：安装后执行 `requirement-ledger --version` 和 `requirement-ledger demo --output-dir NEW_EMPTY_DIRECTORY`。
- 隐私：真实 evidence 只写入新的 `.private.json`，不得进入 Issue、PR、Release 或聊天附件。

## 验证证据

- 实际命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`。
- 结果：97 tests，exit 0；翻译检查输出 `TRANSLATIONS_IN_SYNC`；编译与 `git diff --check` 均 exit 0。
- 构建结果：wheel 与 sdist 均在独立环境安装并报告 `requirement-ledger 0.1.1`；sdist 包含双语 Roadmap 与 Skill 案例，不含字节码、缓存或私有 evidence。
- 行为结果：两次 installed Demo 字节一致；合成 Skill 案例完整通过，基线 `1`、修改后 `0`、validation `improved`、scope `unknown`、报告不含原始失败文本。
- 公开结果：尚无；必须由 release commit 的 CI、Tag、Release 和重新下载验收补齐。
- 证据入口：`docs/RELEASE_CHECKLIST.md` 与 `docs/releases/v0.1.1.md`。

## 授权与禁止动作

- 已授权：完成并发布当前 `v0.1.1` 批次，包括通过发布门后的 commit、push、tag 和 GitHub Release。
- 未授权／禁止：伪造或回填维护历史、制造空版本、自动发布未经真实测试支持的版本，以及把私有证据带入公开产物。
- 发布停止条件：任一单测、安全回归、构建、翻译、公开 CI 或公开安装验证失败。

## 回滚

- 本地改动回滚：发布前保留当前 Git diff；不得使用 hard reset 或 clean 覆盖用户工作，任何回退均通过可审查的反向补丁完成。
- 公开发布回滚：未 tag 前停止发布；已发布后若发现缺陷，保留不可变 tag 和 Release 记录，发布说明中标记问题并用真实修复发布后续 `0.1.x`，不改写公开历史。
