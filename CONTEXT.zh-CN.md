<!-- translation-of: CONTEXT.md sha256:877880b0d86f947b -->

# 项目上下文

这是 Requirement Ledger 的短接手索引。历史对话和私有证据不应进入本仓库。

## 当前检查点

- 阶段：`v0.1.1` 已获准发布；实现 commit 的公开 CI run `33158962532` 已通过，最终证据 commit
  仍需在打 Tag 前通过。
- 品牌：Requirement Ledger AI——面向 Codex、Claude Code 与任意 Git 项目的 AI 项目／Skill
  反馈闭环。仓库 slug 与 CLI 继续使用 `requirement-ledger`。
- 产品：显式 Git 项目 + 显式对话／测试证据 → 私有证据 → 保守归因 → 无原话报告和未应用修复计划
  → 外部同一 oracle 验证。
- 安全：CLI 不发现主目录会话、不运行项目代码、不安装依赖、不联网、不修改工作树、不 commit、
  不 push，也不执行 GitHub／账号动作。
- 验证：97 项本地测试、编译、翻译、wheel/sdist 构建与干净安装、确定性 Demo、包内容检查和
  合成 Skill 案例均已通过。案例得到 oracle `1 -> 0`、`improved`、`unknown` 归因，报告不含
  原始失败文本。
- 发布：当前公开版本仍为 `v0.1.0`。`v0.1.1` 尚未打 Tag 或发布；最终仅证据 commit 及其 CI
  是打 Tag 前剩余的门。

## 接手文件

- 产品与权限：`V0.1_CONTRACT.zh-CN.md`
- 架构与威胁模型：`docs/ARCHITECTURE.md`、`docs/THREAT_MODEL.md`
- 剩余工作：`docs/PROJECT_GAPS.md`
- 维护与分批：`MAINTENANCE.zh-CN.md`；15 天路线：`ROADMAP.zh-CN.md`
- 发布门与说明：`docs/RELEASE_CHECKLIST.md`、`docs/releases/v0.1.1.md`
- 合成 Skill 案例：`docs/use-cases/improve-an-agent-skill.zh-CN.md`
- 滚动技术交接：`HANDOFF.md`

## 下一步

推送最终证据更新，要求公开 CI 再次全绿，再从完全相同的 commit 创建 Tag 与 Release。发布后
从显式证据窗口开始设计 `v0.2.0` 报告；不加入自主修改或 GitHub 动作。
