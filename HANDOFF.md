# HANDOFF

## 我们在做什么

本项目当前公开产品名为 **Astra Skill Doctor**：面向 GPT-6/Astra 新模型的 Skill 与工作流适配系统。短期处理一个明确项目及其相关 Skill 的失真、验证和最小修正；长期发展为类似 Jarvis 的个人与开源社区 Skill 优化系统。

## 完成了什么

- 已有独立适配插件 `plugins/gpt6-astra-skill-optimizer`，具备证据、正反案例、最小改动和回滚边界。
- 已建立并更新产品契约 `docs/GPT6_ASTRA_SKILL_CONTRACT.md`，并同步更新 v1 产品契约与路线图，明确新名称、短期目标、长期愿景和纯粹性边界。
- 本地包元数据、插件显示名和当前 README 已切换到 Astra Skill Doctor；旧 Python 包与 CLI 暂保留为兼容入口，并新增 `gpt6-astra-skill` 命令。
- GitHub 仓库为 `gpt-6-astra-skill`，本地远端与 GitHub 页面已核实一致；公开显示名改为 Astra Skill Doctor。
- 1.0.1 命名迁移已推送到 `main`；源码测试 213 项通过、7 项跳过；翻译同步检查、插件结构校验和差异空白检查均通过。

## 卡在哪儿

- 仓库、包、CLI、旧插件和历史文档仍有兼容命名，尚未完成逐项迁移。
- 实时服务化能力不属于当前已交付范围；短期先完成 Skill 适配闭环。
- 历史发布记录仍保留旧版本语境；本轮已将当前产品契约和路线图改为新身份，历史记录不作为新版本发布证明。
- 尚无足够真实项目样本证明 GPT-6/Astra 适配建议在不同项目中稳定有效。

## 下一步计划

用一个脱敏真实项目做首个 Astra Skill Doctor 适配回归，并根据结果补齐兼容迁移表。

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

历史发布提交：`cd09633`；历史正式标签：`v1.0.0`。本轮形成并推送 `1.0.1` 候选到 `main`，未覆盖历史标签；申请简报已生成但尚未提交。工作区仍保留此前未提交的历史改动，未纳入历史插件提交。

## 授权与禁止动作

本轮已明确授权提交并推送 1.0.1 命名迁移版本。仍禁止扫描开放 Skill 目录、修改未列入白名单的文件、发送外部申请/邮件或执行交易；Pro 账号申请本轮只准备材料，不代用户提交。

## 回滚

恢复发布标签 `v1.0.0` 或删除本次新增的独立插件目录即可回退；不得重置或清理工作区中旧 Requirement Ledger 的未提交改动。
