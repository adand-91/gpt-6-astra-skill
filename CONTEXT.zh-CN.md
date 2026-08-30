<!-- translation-of: CONTEXT.md sha256:f4fd79c8e1f0fd22 -->

# 项目上下文

这里只放简短接手索引；私有证据留在仓库外。

## 当前检查点

- `v0.2.0-alpha.1`（`0.2.0a1`）已作为非 latest 的 GitHub 预发布公开。Tag 所在 commit：
  `243b01ac5be88825ec4a1f4f9c5cec3b2841a90e`；注释 Tag 对象：
  `856f4d0fd198a74825f134289af3b0475042ec85`。最新稳定版仍是 `v0.1.1`。
- CI run `33291029715` 已通过 Python 3.10–3.13 × Linux／macOS／Windows 和构建产物／安全
  冒烟。三项公开资产均已重新下载、核对哈希、干净安装，并通过 Demo 与审查创建／校验。
- Alpha 1 交付私有、不覆盖的点名目标 `review-init --mode audit` 骨架、严格
  `review-check`、双语说明和更新地图；尚不会读取 Codex 历史或初始化日报／周报。
- 更新地图以每个成功发布日一个有真实增量的候选版为目标：
  `alpha.1 → alpha.2 → alpha.3 → beta.1 → beta.2 → beta.3 → rc.1 → rc.2 → rc.3 → v0.2.0`。
  门禁失败就顺延，不发布空版本。
- 本隔离工作树是 Alpha 发布权威源；维护者混有 Alpha 后改动的脏工作树保持原样。

## 接手文件

- Release：<https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.1>
- 变更：`CHANGELOG.zh-CN.md`；更新说明：`docs/release-notes/v0.2.0-alpha.1.zh-CN.md`
- 每日发布列车：`UPDATE_MAP.zh-CN.md`；产品路线：`ROADMAP.zh-CN.md`
- 发布证据：`docs/RELEASE_CHECKLIST.md`；技术状态：`HANDOFF.md`

## 下一步

把本次事实性发布／更新地图记录提交到 `main` 并核验 CI。下一个产品候选版是 Alpha 2：为用户
点名的一份 Codex task／导出增加显式有界输入信封。

## 安全边界

不移动 Alpha Tag，不替换其资产。候选日期不能绕过发布门禁。Issue、PR、推广、活动申请、定时
任务、无关历史读取和破坏性修改维护者工作树仍不在本批范围。
