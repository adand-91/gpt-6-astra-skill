<!-- translation-of: CONTEXT.md sha256:019b2377b7e14f18 -->

# 项目上下文

这是 Requirement Ledger 的短接手索引。历史对话和私有证据不应进入本仓库。

## 当前检查点

- 阶段：`v0.1.0` 已公开发布；`main` 进入证据驱动的真实维护阶段。
- 产品：显式 Git 项目 + 显式对话／测试证据 → 私有证据 → 保守归因 → 无原话报告和未应用修复计划
  → 外部同一 oracle 验证。
- 安全：CLI 不发现主目录会话、不运行项目代码、不安装依赖、不联网、不修改工作树、不 commit、
  不 push，也不执行 GitHub／账号动作。
- 验证：96 项本地测试、编译、翻译、定向安全回归、wheel/sdist 构建与干净安装、确定性 Demo、
  显式输入冒烟、Git 不变检查和隐私金丝雀均已通过。
- 发布：annotated tag `v0.1.0` 指向 `ebda351`；GitHub Release 已公开并附 wheel 与 sdist。
  公开重新下载哈希、干净 wheel 安装、版本命令和 Demo 均已通过。

## 接手文件

- 产品与权限：`V0.1_CONTRACT.zh-CN.md`
- 架构与威胁模型：`docs/ARCHITECTURE.md`、`docs/THREAT_MODEL.md`
- 剩余工作：`docs/PROJECT_GAPS.md`
- 维护与分批：`MAINTENANCE.zh-CN.md`
- 发布门与说明：`docs/RELEASE_CHECKLIST.md`、`docs/releases/v0.1.0.md`
- 滚动技术交接：`HANDOFF.md`

## 下一步

观察真实使用和 Issue。只有出现可复现证据时才发布 `0.1.x` 修复；日报／周报与结构化测试适配器
作为真实 `0.2.0` 工作规划。
