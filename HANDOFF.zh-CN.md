<!-- translation-of: HANDOFF.md sha256:25f2678949bdfad7 -->

# HANDOFF

## 我们在做什么

将 `v0.2.0-beta.1` 发布为非 latest GitHub 预发布版，然后汇报仓库指标。
授权范围是既有日报／周报骨架增量，不含后续 Jarvis 功能。

## 完成了什么

- 在隔离发布工作区从公开 Alpha 3 重建候选。
- 验证冻结 Beta 1 的 wheel、sdist 和源码 SHA-256；仅复制版本元数据、review／CLI 改动和两个测试文件，保留旧发布记录。
- 更新中英文发布文档，新增安装后日报／周报 CI 检查。
- 源码与解包源码各通过 138 项测试；翻译、编译、差异检查通过。
- 两种干净安装报告 0.2.0b1；三模式创建／检查、私有权限、不覆盖、错误输入和确定性 Demo 全部通过。
- 独立代码复核未发现阻断；其建议的周报 CLI 覆盖已纳入本地安装检查与新增 CI 步骤。

## 卡在哪儿

本地无已知发布阻断。精确提交的公开 CI、发布与下载验证仍待完成。

## 下一步计划

推送候选，通过三平台 CI，发布不可变附注标签和预发布版，再下载验证制品并汇报指标。完成 Beta 1 回执后停止。

## 踩过哪些坑

冻结源码含 AppleDouble 元数据和过时 Alpha 发布状态，均未复制。累计 1.0.0 源码不能当作 Beta 1 快照。
翻译摘要须跟随实际译文更新；首轮旧摘要失败已修正并重跑。

## 当前任务汇总

- 包版本 0.2.0b1，计划标签 v0.2.0-beta.1，公开基线 Alpha 3。
- 本地资格通过，公开发布待完成。
- 用户授权 Beta 1 提交、推送、CI、标签、Release、制品与仓库指标查询。
- 后续版本、改名、推广、插件提交、项目申请仍排除。

## 当前架构与入口

`src/requirement_ledger/review.py` 计算窗口并生成私有空骨架；`cli.py` 暴露显式参数。
没有新增历史发现、联网或自动调度。

## 运行与依赖

Python 3.10–3.13；Windows 沿用条件 tzdata 依赖。
测试：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`。
构建：在隔离构建环境运行 `python -m build --sdist --wheel`。

## 验证证据

源码／解包源码各 138 项。翻译：`python3 scripts/check_translation_sync.py`。
编译：`python3 -m compileall -q src scripts tests`。空白：`git diff --check`。
归档检查排除字节码、私有 JSON、维护者路径和后续模块。公开哈希与 CI 回执在实际完成后登记。

## 回滚

发布前用经过审查的前向提交修正。不移动公开标签或替换制品。累计开发工作区和先前发布保持不变。
