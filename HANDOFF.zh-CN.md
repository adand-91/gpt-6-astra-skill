<!-- translation-of: HANDOFF.md sha256:1f2d399d70e8dfd7 -->

# HANDOFF

## 我们在做什么

本项目正在统一为 **Astra Skill Doctor**：面向 GPT-6/Astra 新模型的 Skill 与工作流适配系统。短期处理一个明确项目及其相关 Skill 的失真、验证和最小修正；长期发展为类似 Jarvis 的个人与开源社区 Skill 优化系统。

## 完成了什么

- 已有独立适配插件 `plugins/gpt6-astra-skill-optimizer`，具备证据、正反案例、最小改动和回滚边界。
- 已建立产品契约 `docs/GPT6_ASTRA_SKILL_CONTRACT.md`，明确新名称、短期目标、长期愿景和纯粹性边界。
- 本地包元数据和当前 README 已切换到 Astra Skill Doctor；旧 Python 包与 CLI 暂保留为兼容入口。
- GitHub 仓库已改名为 `gpt-6-astra-skill`。
- 新增定位修改后，Jarvis 全量测试 213 项通过、7 项跳过；插件结构校验通过。

## 卡在哪儿

- 仓库、包、CLI、旧插件和历史文档仍有兼容命名，尚未完成逐项迁移。
- 实时服务化能力不属于当前已交付范围；短期先完成 Skill 适配闭环。
- 历史文档对 v1.0.0 的发布状态存在冲突，需要以 Git 和远端事实统一。
- 尚无足够真实项目样本证明 GPT-6/Astra 适配建议在不同项目中稳定有效。

## 下一步计划

先完成仓库远端命名核实、当前公开文档统一和兼容迁移表；随后用一个脱敏真实项目做首个 Astra Skill Doctor 适配回归。

## 踩过哪些坑

- 旧模型时代的硬约束可能在新模型上变成阻碍，不能只看 Skill 文案是否完整。
- 通过格式检查不等于模型行为、项目质量或真实结果通过。
- 接单教练、交易和其他业务 Skill 不属于本项目产品内容。

## 当前任务汇总

当前目标：完成 Astra Skill Doctor 的命名、定位和迁移边界，并准备短期适配闭环。未授权/未执行：扫描无关 Skill、自动改动外部项目、发送外部申请、交易和其他业务动作。

## 当前架构与入口

独立 Skill-only 插件入口是 `plugins/gpt6-astra-skill-optimizer/.codex-plugin/plugin.json`；核心流程位于其 `skills/gpt6-astra-skill-optimizer/SKILL.md`，资料和测试场景位于 `references/`。

## 运行与依赖

插件保持轻量 Skill 分发层，不带 hooks、Python runtime 或额外权限面；通过 Codex plugin marketplace 安装，默认只读取选定项目和明确关联 Skill。

## 验证证据

插件是 Skill-only，不带 hooks、Python runtime 或额外权限面。测试命令：

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q
```

Git 标签：`v1.0.0`。工作区仍保留历史未提交改动，未自动清理或重置。

## 授权与禁止动作

可以继续做真实项目的只读审计和经明确授权的 Skill 小修。禁止扫描开放 Skill 目录、修改未列入白名单的文件、发送外部申请/邮件、提交新公开版本或执行交易，除非另行明确授权。

## 回滚

恢复迁移前的本地文档与元数据，或按 Git 记录回退；不得重置或清理无关未提交改动。
