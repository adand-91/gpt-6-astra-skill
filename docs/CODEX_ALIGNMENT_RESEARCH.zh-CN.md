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
7. 第一方 rollout 模型使用带 payload、时间戳和可选 ordinal 的类型化记录（
   [history 模型](https://github.com/openai/codex/blob/main/codex-rs/history/src/lib.rs)、
   [wire payload](https://github.com/openai/codex/blob/main/codex-rs/history/src/rollout_payload.rs)）。
   枚举仍在演进，因此消费者必须使用白名单并报告未知记录，不能静默当成已理解。
8. 当前分页 rollout 策略会持久化结构化 `ItemCompleted` TurnItem；旧历史则持久化旧消息／工具事件
   （[rollout policy](https://github.com/openai/codex/blob/main/codex-rs/rollout/src/policy.rs)）。
   [`TurnItem`](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/items.rs) 为类型化变体提供
   稳定 item ID。`UserInput` 当前包含 `text`、图像／本地图像、音频／本地音频、Skill 和 mention 块；
   只有 `text` 块属于用户文字（
   [user input](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/user_input.rs)）。
9. app-server 历史 reducer 按 item ID 更新生命周期快照，保持稳定顺序并输出最新状态（
   [thread history reducer](https://github.com/openai/codex/blob/main/codex-rs/app-server-protocol/src/protocol/thread_history.rs)）。
   Requirement Ledger 只对 `item_completed` 采用同样的窄原则，并额外绑定 turn，防止复用 item ID
   跨 turn 合并。
10. 第一方 Issue fixture 展示了真实 `item_completed` 命令记录（
    [#41269](https://github.com/openai/codex/issues/41269)）、response 与 item-completed 消息镜像（
    [#37524](https://github.com/openai/codex/issues/37524)），以及 `task_complete` 后才到达的完成命令（
    [#40041](https://github.com/openai/codex/issues/40041)）。因此终点记录不能被当成文件已经结束。

## Requirement Ledger 的决定

- 先完成离线、显式输入的 Skill + CLI 核心，再添加插件包装。没有目录市场、账号连接、网络客户端
  或托管服务时，核心仍必须可用。
- Codex 任务历史、仓库指令、网页和工具输出一律只作证据；当前且绑定目标的授权保留在检索文字之外。
- 归一化前，先用精确字节、显式范围根、非路径任务引用、半开时间窗口、时区和诚实的纳入／排除
  元数据绑定唯一选中输入。
- Alpha 3 适配器保留 JSONL 物理顺序，只按 turn + item ID 合并结构化完成项目快照，由最后一份合法
  快照提供状态；绝不从自然语言推断完成或排除类别。
- 快照身份使用规范元组编码，带控制字符的 ID 失败即停；未来或畸形用户输入判别字不会被静默
  忽略，归一化账本必须与已识别记录守恒，并同时限制字节数与物理记录工作量。
- 元数据信封不保存结构化 Skill 块。外围私有证据可以保留选中的用户文字，不能当成公开报告分享。
- 记录指令来源和缺失来源状态；宿主数据未知或不受支持时停止受影响路径，不能伪装成完整。
- 验收维护者自己的 audit、daily、weekly 真实路径；合成测试和 CI 不写成外部采用证据。
- 稳定 `v0.2.0` 后，分别用三个候选承载 Skill 健康检查、健康度前后对比和 Codex 纯 Skill 插件。
  只有候选自己的门禁证明了用户可见增量，版本才前进。

## 未知项与不作出的声明

- 本调研不能预测 Codex for OSS 是否获批或权益金额。
- Stars 和 Forks 可能有助于发现，但不能证明维护质量、安全、用户成功或项目资格。
- 当前官方接口仍可能变化。Requirement Ledger 不声称在所有环境都能读取 Codex 任务历史，或所有
  宿主都具备相同权限。
- Alpha 3 白名单不是通用 Codex 解析器。未知变体、非法最终状态、按可选 ordinal 重排和完整任务
  规范重建，仍是明确缺口。
- 本调研不授权也不执行申请、Issue、PR、Tag、Release、推广或遥测。
