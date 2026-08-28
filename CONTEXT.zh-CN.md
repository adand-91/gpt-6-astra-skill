<!-- translation-of: CONTEXT.md sha256:aa603d0ab83603af -->

# 项目上下文

这是 Requirement Ledger 的短接手索引。历史对话和私有证据不应进入本仓库。

## 当前检查点

- 阶段：本地 `v0.1.0` 发布候选；在通过发布门并获得发布授权前，公开仓库仍是旧的纯复盘版本。
- 产品：显式 Git 项目 + 显式对话／测试证据 → 私有证据 → 保守归因 → 无原话报告和未应用修复计划
  → 外部同一 oracle 验证。
- 安全：CLI 不发现主目录会话、不运行项目代码、不安装依赖、不联网、不修改工作树、不 commit、
  不 push，也不执行 GitHub／账号动作。
- 验证：95 项本地测试、编译、翻译、定向安全回归、wheel/sdist 构建与干净安装、确定性 Demo、
  显式输入冒烟、Git 不变检查和隐私金丝雀均已通过。
- 发布：尚未发生 v0.1 commit、tag、push 或 GitHub Release。

## 接手文件

- 产品与权限：`V0.1_CONTRACT.zh-CN.md`
- 架构与威胁模型：`docs/ARCHITECTURE.md`、`docs/THREAT_MODEL.md`
- 剩余工作：`docs/PROJECT_GAPS.md`
- 维护与分批：`MAINTENANCE.zh-CN.md`
- 发布门与说明：`docs/RELEASE_CHECKLIST.md`、`docs/releases/v0.1.0.md`
- 滚动技术交接：`HANDOFF.md`

## 下一步

刷新 `HANDOFF.md`，制作并 push 一个完整的发布候选提交，然后等待公开跨平台 CI。只有 CI 全绿后，
才能创建 tag 并发布 GitHub Release `v0.1.0`。
