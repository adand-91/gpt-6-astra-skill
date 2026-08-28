# HANDOFF

## 我们在做什么

- 目标：把 Requirement Ledger 从早期对话复盘 Skill 升级为可安装、隐私优先、适用于任意 Git 项目的 `v0.1.0`，并在全部发布门通过后公开发布。
- 本轮范围：修复发布阻断，验证英语主版与中文镜像，构建 wheel/sdist，完成 GitHub 发布准备。
- 不在范围：自动修改用户项目、自动运行第三方代码、自动提交 Issue/PR、伪造维护记录，以及日报／周报和隔离执行等 `v0.2+` 功能。

## 完成了什么

- 修改：修复显式 transcript 绑定流程中的语法回归和自动 provider 路径传递；完成输入稳定性、Git 可信执行、输出祖先软链接、snapshot drift、资源上限与 digest-bound oracle 加固。
- 新增：标准 `src/` 包、统一 CLI、零运行时依赖的 `pyproject.toml`、CI、安全与社区文件、匿名样例、威胁模型、范围账本、发布清单和中英文核心文档。
- 打包：source distribution 显式包含项目 context 与双语 Handoff，且排除私有 evidence、字节码和缓存目录。
- 质量：暂存文件已完成 EOF 与 `git diff --check` 格式清理，发布提交不包含生成目录。
- 验证：95 项单元测试、编译、翻译同步、7 个定向安全回归、wheel/sdist 构建、干净安装、确定性 Demo、显式输入 smoke 和 Git 不变检查已通过。

## 卡在哪儿

- 当前阻断：第二次公开 CI 已证明 Windows LF 修复，但 Windows Python 3.12 暴露同文件的 path-stat/handle-stat 元数据差异；现已拆分身份与内容稳定性检查，等待第三次矩阵证明关闭。
- 尚未验证：修复提交上的 Python 3.10–3.13 × Ubuntu/macOS/Windows 矩阵，以及发布后源码归档和 Release 附件下载路径。

## 下一步计划

1. 提交并 push 一个连贯的 `v0.1.0` release-candidate commit。
2. 等待公开 CI；任何 job 失败都停止 tag 和 Release。
3. CI 全绿后创建 `v0.1.0` tag 和 GitHub Release，附上最终 wheel/sdist，并核验公开安装与 Demo。
4. 发布后只根据真实 Issue、使用反馈和回归测试维护 `0.1.x`；日报／周报与结构化测试适配器进入 `0.2.0`。

## 踩过哪些坑

- 失败／误判：文档曾声称发布门通过，但根目录没有 Handoff，随后 transcript 加固又引入未闭合 `try` 的语法错误，导致新 CLI 无法导入。
- 跨平台发现：Windows checkout 的 CRLF 转换会改变双语源文件哈希；仓库现在用 `.gitattributes` 固定文本 LF，并升级 CI Actions 到当前 Node 24 主版本。
- Python 3.12 发现：Windows 对同一文件的路径 stat 与句柄 stat 可报告不同的非内容字段；输入绑定现在用 `os.path.samestat` 判断身份，以 size/mtime 判断内容稳定性，并保留读前读后检查。
- 以后如何避免：状态文档不能替代当前命令证据；每次程序修改后先跑完整测试与翻译检查，再刷新 Handoff；发布只接受同一 commit 的 CI 结果。
- 维护边界：不把已经完成的功能拆成虚假版本，也不按日期制造空提交。定时任务只做真实检查，无真实变更就不发布。

## 当前任务汇总

- 状态：两个公开 CI 失败已转成回归证据；Windows Python 3.12 修复等待提交并重跑公开 CI。
- 当前有效产物：仓库工作树中的 `0.1.0` 源码、文档、测试与 CI；最终发布附件必须从待发布 commit 重新构建。
- 一句话结论：本地 Go，公开 Release 暂缓到 GitHub CI 全绿。

## 当前架构与入口

- 项目根目录：当前 Git 仓库根目录。
- 主入口：`requirement-ledger` console command；源码入口为 `src/requirement_ledger/cli.py`。
- 关键数据流：显式项目和证据 → 私有 evidence → 保守 analysis → 无原话 report 与未应用 proposal → 外部同一 oracle 的 baseline/after 验证。
- 权威契约：`V0.1_CONTRACT.md`；剩余工作：`docs/PROJECT_GAPS.md`；维护批次：`MAINTENANCE.md`。

## 运行与依赖

- 环境：Python 3.10–3.13；当前本地验收使用 Python 3.12.13、macOS arm64。
- 依赖：核心运行时仅 Python 标准库；构建时使用 PEP 517 与 setuptools。
- 运行命令：安装后执行 `requirement-ledger --version` 和 `requirement-ledger demo --output-dir NEW_EMPTY_DIRECTORY`。
- 隐私：真实 evidence 只写入新的 `.private.json`，不得进入 Issue、PR、Release 或聊天附件。

## 验证证据

- 实际命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`。
- 结果：95 tests，exit 0；翻译检查输出 `TRANSLATIONS_IN_SYNC`；编译和 7 个定向 fail-closed 回归均 exit 0。
- 构建结果：wheel 与 sdist 均可在干净环境安装，两个入口均报告 `requirement-ledger 0.1.0`。
- 行为结果：两次 installed Demo 字节一致；显式输入 smoke 生成私有 evidence，扫描前后 `git status` 无差异。
- 证据入口：`docs/RELEASE_CHECKLIST.md` 与 `docs/releases/v0.1.0.md`。

## 授权与禁止动作

- 已授权：完成并发布 `v0.1.0`，包括通过发布门后的 commit、push、tag 和 GitHub Release。
- 未授权／禁止：伪造或回填维护历史、制造空版本、自动发布未经真实测试支持的版本，以及把私有证据带入公开产物。
- 发布停止条件：任一单测、安全回归、构建、翻译、公开 CI 或公开安装验证失败。

## 回滚

- 本地改动回滚：发布前保留当前 Git diff；不得使用 hard reset 或 clean 覆盖用户工作，任何回退均通过可审查的反向补丁完成。
- 公开发布回滚：未 tag 前停止发布；已发布后若发现缺陷，保留不可变 tag 和 Release 记录，发布说明中标记问题并用真实修复发布 `0.1.1`，不改写公开历史。
