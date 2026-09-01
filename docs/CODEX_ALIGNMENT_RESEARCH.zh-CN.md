# Codex 对齐调研

调研日期：2026-08-30。范围：OpenAI 官方资料和当前第一方仓库。本说明区分公开事实、项目决定和
未知项；它不是 OpenAI 背书，也不是项目申请。

## 已公开事实

1. [Codex for Open Source](https://developers.openai.com/community/codex-for-oss) 会考虑仓库使用、
   生态重要性、活跃维护和申请人的维护者角色；其
   [条款](https://learn.chatgpt.com/docs/codex-for-oss-terms) 要求信息准确且仓库访问已获授权。
   OpenAI 没有公开最低 Stars、Forks 或 Release 数，也没有承诺获批、时间或固定权益。
2. [Agent Skills](https://learn.chatgpt.com/docs/build-skills) 是聚焦的工作流，`SKILL.md` 指令按需
   渐进加载。OpenAI 指南强调明确输入、输出、停止条件和未知状态，而不是让宽泛提示词静默扩展范围。
3. [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) 指令从全局、仓库到当前
   目录分层，越近的文件优先。因此证据必须记录实际生效的指令层，不能把仓库里每段文字都当成同等
   权威。
4. [审批与安全](https://learn.chatgpt.com/docs/agent-approvals-security) 要求网络、沙箱、权限和审批
   边界保持显式。仓库文字、PR 文字、截图和工具结果都是不可信输入，不能授予实施或发布权限。
5. 官方 [`openai/skills`](https://github.com/openai/skills) 仓库已弃用，并把作者指向
   [`openai/plugins`](https://github.com/openai/plugins) 和
   [Build Plugins 指南](https://developers.openai.com/plugins/build/skills)。插件是当前分发界面，
   但聚焦的本地 Skill 仍是有效的编写和测试单元。
6. [Codex 变更日志](https://learn.chatgpt.com/docs/changelog) 显示任务协作、插件配置、MCP 可靠性、
   权限、沙箱和长对话历史仍在快速演进。因此兼容性必须由 fixture 证明；宿主能力缺失或结构变化时
   应失败即停止。

## Requirement Ledger 的决定

- 先完成离线、显式输入的 Skill + CLI 核心，再添加插件包装。没有目录市场、账号连接、网络客户端
  或托管服务时，核心仍必须可用。
- Codex 任务历史、仓库指令、网页和工具输出一律只作证据；当前且绑定目标的授权保留在检索文字之外。
- 归一化前，先用精确字节、显式范围根、非路径任务引用、半开时间窗口、时区和诚实的纳入／排除
  元数据绑定唯一选中输入。
- 记录指令来源和缺失来源状态；宿主数据未知或不受支持时停止受影响路径，不能伪装成完整。
- 验收维护者自己的 audit、daily、weekly 真实路径；合成测试和 CI 不写成外部采用证据。
- 稳定 `v0.2.0` 后，分别用三个候选承载 Skill 健康检查、健康度前后对比和 Codex 纯 Skill 插件。
  只有候选自己的门禁证明了用户可见增量，版本才前进。

## 未知项与不作出的声明

- 本调研不能预测 Codex for OSS 是否获批或权益金额。
- Stars 和 Forks 可能有助于发现，但不能证明维护质量、安全、用户成功或项目资格。
- 当前官方接口仍可能变化。Requirement Ledger 不声称在所有环境都能读取 Codex 任务历史，或所有
  宿主都具备相同权限。
- 本调研不授权也不执行申请、Issue、PR、Tag、Release、推广或遥测。
