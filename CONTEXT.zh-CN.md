<!-- translation-of: CONTEXT.md sha256:6db6f55e6560aa81 -->

# 项目上下文

短接手索引。任务规则见 `AGENTS.md`；产品契约见 `docs/GPT6_ASTRA_SKILL_CONTRACT.md`；技术交接见 `HANDOFF.md`。

## 项目目标

构建 **Astra Skill Optimizer**：基于可追溯证据、最小改动和可复核验证，适配现有项目 Skill 与工作流。长期发展为类似 Jarvis 的个人与社区 Skill 优化系统。

## 当前检查点

- 产品名为 Astra Skill Optimizer，GitHub 仓库 slug 保留 `gpt-6-astra-skill`。
- 独立插件位于 `plugins/gpt6-astra-skill-optimizer`。
- 旧 Requirement Ledger 包和 CLI 保留为兼容入口。
- `1.0.2` 改名已推送到 `main`：测试共 213 项，206 项通过、7 项跳过；翻译和插件校验通过。
- 业务 Skill 和订单记录不属于本项目。

## 下一步与边界

使用 `docs/PRO_APPLICATION_BRIEF.md` 准备申请，再开展脱敏真实项目适配回归。不得混入接单、交易、私人客户记录或无关项目实现。
