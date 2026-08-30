<!-- translation-of: CONTEXT.md sha256:2cd6d8a76bd24385 -->

# 项目上下文

这里只放简短接手索引；私有证据留在仓库外。

## 当前检查点

- 正在准备 `v0.2.0-alpha.1`（`0.2.0a1`）。CI commit `a880e9b` 在类 Unix 通过、Windows
  因缺 IANA 数据失败；没有 Tag／Release。修正增加条件依赖 `tzdata` 和可执行错误。
- 本隔离工作树只含封存 Alpha 源码；混有 Alpha 后改动的维护者工作树保持原样。
- Alpha 范围仅包含私有、不覆盖的点名目标 `review-init --mode audit` 骨架、严格
  `review-check` 和配套双语宿主契约／模板。
- 日报／周报 CLI 初始化、现代 Codex 导出解析、候选延续、审查包绑定、交接复验、定时任务、自动
  修改和 Skill 健康扫描均未包含。
- 双语说明、更新地图、路线图、CI 冒烟和发布清单已定义 v0.2 路径。
- 修正后源码门禁：113 项测试、双语同步和 diff 检查；重新构建、干净安装、隐私／路径冒烟、修正后
  公开 CI、Tag、预发布和重新下载复验仍待完成。

## 接手文件

- 发布边界：`docs/release-notes/v0.2.0-alpha.1.zh-CN.md`
- 十天计划：`UPDATE_MAP.zh-CN.md`；长期产品路径：`ROADMAP.zh-CN.md`
- 产品契约：`V0.1_CONTRACT.zh-CN.md`、`V0.2_HOST_CONTRACT.zh-CN.md`
- 发布门禁：`docs/RELEASE_CHECKLIST.md`；技术状态：`HANDOFF.md`

## 下一步

重复全部本地门禁，提交／推送 Windows 修正并等待 CI。只有全绿后才创建注释 Tag
`v0.2.0-alpha.1` 和非 latest 预发布；记录证据前重新下载全部资产。

## 安全边界

授权覆盖精确 Alpha commit、推送 `main`、注释 Tag、发布资产和 GitHub 预发布；不覆盖 Issue、PR、
推广、活动申请、定时任务、无关历史读取、其他版本，或清理／回退维护者脏工作树。
