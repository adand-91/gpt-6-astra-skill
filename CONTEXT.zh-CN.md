<!-- translation-of: CONTEXT.md sha256:00b16d8963c0dfee -->

# 项目上下文

短接手索引。任务规则见 `AGENTS.md`；产品契约见 `docs/GPT6_ASTRA_SKILL_CONTRACT.md`；技术交接见 `HANDOFF.md`。

## 项目目标

构建 **Astra Skill Doctor**：当 GPT-6/Astra 新模型让旧约束失效时，适配现有项目的 Skill 与工作流。长期发展为类似 Jarvis 的个人与社区 Skill 优化系统。

## 当前检查点

- 仓库身份迁移进行中，建议 GitHub slug 为 `gpt-6-astra-skill`。
- 独立 Astra 审计插件位于 `plugins/gpt6-astra-skill-optimizer`。
- 旧 Requirement Ledger 包和 CLI 在迁移期间保留为兼容入口。
- 本地最新源码测试：213 项通过，7 项跳过。
- 业务 Skill 和订单记录不属于本项目。

## 下一步与边界

先冻结命名和产品契约迁移表，再更新公开仓库元数据与当前文档。不得混入接单、交易、私人客户记录或无关项目实现。
