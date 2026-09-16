<!-- translation-of: HANDOFF.md sha256:ac8a51fccc94da04 -->

# HANDOFF

## 我们在做什么

准备 Astra Skill Optimizer 1.0.3，按用户授权发布 GitHub 并申请 Codex for OSS。短期产品适配选定项目的 GPT-6／Astra Skill，长期 Jarvis 是个人项目管理师方向，不冒称自主项目管理已完成。

## 完成了什么

- 纳入官方基线与 Astra 适配两轮合同，保留领域核心功能。
- 修复常见 YAML 描述误报；不支持的语法交人工复核。独立抽查发现的多行 plain 描述截断也已加入回归。
- 沿用范围内已有修改授权，不重复请示；从通用 Skill、字段和案例移除特定业务报价及沟通策略。
- 中英文安装说明提供两个插件入口，进度示例不再编造百分比。
- 包与插件均为 1.0.3；两个已安装快照与源码字节一致。
- 修正历史审计报告：23 项静态记录不是全库运行时证明；原始私有材料另行保存在仓库外。

## 卡在哪儿

本地验证当前无阻断问题。推送、公开 CI、Release 和申请回执必须分别核实；本检查点只记录本地验收。
跨项目 Astra 质量提升和新任务自动触发仍未证明。

## 下一步计划

发布验收后的 1.0.3 提交与资产，再提交真实申请并私下保留回执。用户已在当前任务授权这些动作。

## 踩过哪些坑

旧正则把不识别的 YAML 写法误当成缺字段。静态 PASS 不是模型行为合格证。源码版本和目录列表不证明缓存新鲜，须核对安装回执和字节。七项跳过不能算通过。系统 Python 的 build 入口不可用，改用隔离的 `uv build` 成功，无需修改系统包。私有目录不能进入公开产物。

## 当前任务汇总

本地候选：223 项测试，216 通过、7 项在 macOS 跳过。独立 Agent 只读抽查覆盖审计、缺上下文和沿用授权三种情况；其具体模型名无法核验，不作为 Astra 基准。未修改第三方领域 Skill 或账号。

## 当前架构与入口

`src/requirement_ledger` 保留兼容核心，两个 CLI 入口是 `gpt6-astra-skill` 和 `requirement-ledger`。
插件位于 `plugins/`，目录元数据位于 `.agents/plugins`。
`scripts/audit_skill_catalog.py` 为只读启发式检查器，`examples/skill-audit/SKILL.md` 为公开合成回归输入。

## 运行与依赖

Python 3.10+；Windows 保留条件依赖 `tzdata`。未新增运行时依赖、服务、模型调用、调度或账号集成。
Codex 使用带版本快照，更新后需新任务加载指令；安装与刷新命令见 README。

## 验证证据

在仓库根目录运行，退出码均为 0：

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q
python3 scripts/audit_skill_catalog.py examples/skill-audit
python3 scripts/check_translation_sync.py
python3 -m compileall -q src scripts tests
git diff --check
```

两份 Skill 与插件校验均通过。`uv build` 构建 wheel 和 sdist；干净 wheel 环境验证两个 CLI 版本，运行两遍 demo 字节一致。
文档定稿后重建最终发布资产。目录审计的十一项回归覆盖正常、缺失、不支持、重复、多行元数据、空输入与启发式说明。
其他操作系统的证据以 GitHub CI 为准。

## 授权与禁止动作

当前指令授权准备发布此版本和申请 Codex for OSS，不授权编造资格、更换申请身份、给员工发信、交易、修改无关业务 Skill 或新增后台自动化。
申请身份和原始本地审计证据保存在仓库外。

## 回滚

必要时以新提交反向恢复本轮改动，重装前一标签的插件并新建任务。不重置用户工作树、不改写已发布标签、不删除私有历史证据。不需要 CLI 结构迁移。
