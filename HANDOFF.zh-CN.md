<!-- translation-of: HANDOFF.md sha256:98b388b0668ad51a -->

# HANDOFF

## 我们在做什么

本项目已转为独立的 GPT-6 Astra Skill Optimizer v1.0.0：联合审计一个选定项目与其明确关联的 Skill，基于可追溯官方资料检查 Astra 适配性，并在授权后实施最小改进。

## 完成了什么

- 新增独立插件 `plugins/gpt6-astra-skill-optimizer`，含 Skill、审计字段、官方来源登记和中英文发布说明。
- 固定联合审计流程：项目状态、Skill 指令、Astra 适配维度、证据、风险、建议、验收。
- 默认只读；修改需精确路径白名单和单独授权；不声称训练模型。
- 增加 5 个正向和 5 个负向/边界用例。
- 全套测试：211 项通过，7 项平台测试跳过；本地插件安装后源/缓存哈希一致。
- GitHub 正式 Release `v1.0.0` 已发布：https://github.com/adand-91/requirement-ledger/releases/tag/v1.0.0

## 卡在哪儿

当前没有发布阻断问题。尚未有足够的真实用户样本证明 Skill 审计建议在不同项目中稳定改善行为；这属于后续实测未知，不影响已发布文件身份。

## 下一步计划

在一个真实项目中使用自然语言触发“审计项目和相关 Skill”，记录项目层与 Skill 层各自的事实、推断和未知；若出现可复现失败，再准备 v1.0.1 修正。

## 踩过哪些坑

- 官方资料是版本化指导和审计证据，不是对 GPT-6 Astra 的再训练。
- 进度格式通过不等于项目质量或业务结果通过。
- 旧 Requirement Ledger/Jarvis 管家版本与当前独立优化器必须分开说明。
- Codex Ambassadors 申请当前暂停；OpenAI 开源支持、插件提交和外部邮件是不同渠道，不能混称为同一个贡献者活动。

## 当前任务汇总

授权范围：完成并推出 GPT-6 Astra Skill Optimizer v1.0.0；已完成 GitHub 发布。未授权/未执行：OpenAI 申请、邮件、自动化、交易、任意 Skill 扫描。权威检查点见对话接手中心；官方来源和审计规则见插件 Skill 目录。

## 当前架构与入口

独立 Skill-only 插件入口是 `plugins/gpt6-astra-skill-optimizer/.codex-plugin/plugin.json`；核心流程位于其 `skills/gpt6-astra-skill-optimizer/SKILL.md`，资料和测试场景位于 `references/`。

## 运行与依赖

插件不带 MCP server、hooks、Python runtime 或额外权限面；通过 Codex plugin marketplace 安装，默认只读取选定项目和明确关联 Skill。

## 验证证据

插件是 Skill-only，无 MCP server、hooks、Python runtime 或额外权限面。测试命令：

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q
```

发布提交：`cd09633`；正式标签：`v1.0.0`。工作区仍保留此前未提交的 Requirement Ledger 历史改动，未纳入本次正式插件提交。

## 授权与禁止动作

可以继续做真实项目的只读审计和经明确授权的 Skill 小修。禁止将来源称为模型训练、扫描开放 Skill 目录、修改未列入白名单的文件、发送外部申请/邮件、提交新公开版本或执行交易，除非用户另行明确授权。

## 回滚

恢复发布标签 `v1.0.0` 或删除本次新增的独立插件目录即可回退；不得重置或清理工作区中旧 Requirement Ledger 的未提交改动。
