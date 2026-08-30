<!-- translation-of: CONTEXT.md sha256:3880b20b871f479e -->

# 项目上下文

这里只放简短接手索引；私有证据留在仓库外。

## 当前检查点

- 正在准备 GitHub 预发布版 `v0.2.0-alpha.1`，包版本为 `0.2.0a1`。精确发布 commit 通过公开
  CI 之前，公开状态仍为 `v0.1.1`。
- 本隔离工作树从 `origin/main` 开始，只恢复封存 Alpha 源码；维护者混有 Alpha 后改动的工作树
  保持原样。
- Alpha 范围仅包含私有、不覆盖的点名目标 `review-init --mode audit` 骨架、严格
  `review-check` 和配套双语宿主契约／模板。
- 日报／周报 CLI 初始化、现代 Codex 导出解析、候选延续、审查包绑定、交接复验、定时任务、自动
  修改和 Skill 健康扫描均未包含。
- 双语变更日志、更新说明、十天更新地图、README、路线图、CI 冒烟和发布清单已准确区分本次能力
  与稳定 `v0.2.0` 路径。
- 当前源码门禁：112 项测试、双语同步和 diff 检查通过；最终构建、干净安装、隐私／路径冒烟、
  公开 CI、Tag、预发布和重新下载复验仍待完成。

## 接手文件

- 发布边界：`docs/release-notes/v0.2.0-alpha.1.zh-CN.md`
- 十天计划：`UPDATE_MAP.zh-CN.md`；长期产品路径：`ROADMAP.zh-CN.md`
- 产品契约：`V0.1_CONTRACT.zh-CN.md`、`V0.2_HOST_CONTRACT.zh-CN.md`
- 发布门禁：`docs/RELEASE_CHECKLIST.md`；技术状态：`HANDOFF.md`

## 下一步

最终确定 `HANDOFF.md`，运行完整本地发布门禁，提交并推送精确 Alpha 源码，等待公开 CI，再创建
注释 Tag `v0.2.0-alpha.1` 和非 latest 的 GitHub 预发布版。记录发布证据前重新下载并复验所有资产。

## 安全边界

授权覆盖精确 Alpha commit、推送 `main`、注释 Tag、发布资产和 GitHub 预发布；不覆盖 Issue、PR、
推广、活动申请、定时任务、无关历史读取、其他版本，或清理／回退维护者脏工作树。
