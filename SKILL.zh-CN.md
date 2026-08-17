<!-- translation-of: SKILL.md sha256:74ebeaecc5b6a5fa -->
<!-- SKILL.md 是权威源。改动先改英文，再用 scripts/check_translation_sync.py --update 重新盖章。 -->

# 需求账本

一个项目干完之后大家会问的那些问题，答案本来就躺在它自己的对话里：他到底想要什么、哪儿出了错、
哪些活我们手工做了三遍。没人回头读，所以答案丢了，同一个错下次再付一遍钱。

这个 Skill 负责把它读回来。先机械地读，再解释性地读。

## 唯一的硬规则

**每一个数字都来自脚本。模型一个都不许自己估。**

肉眼数消息、目测比例、把子代理口述的数字当结论 —— 这就是这个 Skill 要防的那件事。
带编造数字的复盘比不做更糟，因为它后来会被当事实引用。细则见
[evidence-rules.zh-CN.md](references/evidence-rules.zh-CN.md)。

## 第 0 步 拿到事实

在读任何东西之前，永远先跑这个：

```bash
python3 scripts/scan_transcript.py --engine both --since 7d --format json --out /tmp/facts.json
python3 scripts/scan_transcript.py --engine claude --project myproject   # 单个项目
python3 scripts/scan_transcript.py path/to/session.jsonl                 # 单个会话
```

读 Claude Code（`~/.claude/projects`）、Codex（`~/.codex/sessions`），或一份纯文本对话记录。
逐行流式读 —— 真实会话能到 250 MB，单行能有 152 万字符的 base64，所以任何文件都不整读。
大约每 3 秒 1 GB。

它交给你的东西：真实用户回合数（**不是** tool result —— 两个引擎都把工具输出当用户消息回灌）、
每条用户原话、被标记为待判定的纠偏、失败的工具调用和对应工具名、重复的命令形状、重复的工具序列。

输出要发给别人时加 `--no-text`：保留全部计数，去掉逐字原文。

## 第 1 步 真需求

他真正需要的东西，很少是他开口那句。从**纠偏**里建，不从第一条消息里建：
每一次纠偏都是「在做的东西」和「想要的东西」岔开的地方，而他用来掰回来的那句话，
通常直接把真需求说出来了。

每条都带标签，标签绝不混：

| 标签 | 含义 |
|---|---|
| `原话` | 用户自己的话，逐字引用，带时间戳 |
| `推断` | 你对他意思的解读 —— 必须一直标成你的 |
| `未知` | 对话回答不了这条；就写未知，不许填上 |

方法，以及怎么回溯到最早那条需求而不是最近那条：
[real-requirement.zh-CN.md](references/real-requirement.zh-CN.md)。

## 第 2 步 错误

不是一张报错清单。每条都要判层级，因为层级决定这事到底修不修得了：规则缺失、
规则存在但没触发、两条规则冲突、规则放错位置、真实工具限制，还是一次性偶发。

只有前四种值得动手。把工具限制当成流程问题，产出的规则注定不起作用。
见 [mistakes.zh-CN.md](references/mistakes.zh-CN.md)。

## 第 3 步 可自动化的部分

脚本的 `repeated_commands` 和 `repeated_tool_sequences` 是原始候选：手工做过三遍以上的活。
其中大部分**不该**做成 Skill。判据是**判断是否稳定**，不是按键是否重复 ——
[skill-extraction.zh-CN.md](references/skill-extraction.zh-CN.md) 里有筛子、提案格式，
以及优化记录必须记什么。

## 授权

默认产出是**提案 + 优化记录**。不写进任何真实 Skill 目录，不改生产文件，不动任何规则。

只有收到明确的「开干 / 执行 / 写吧」，才生成真正的 `SKILL.md`，而且先确认目标：
能复用或扩展已有 Skill 就不新建。两个覆盖同一块地的 Skill，比它们要替掉的手工活更糟。

## 产出

两个文件都先落盘，再在聊天里总结 —— 聊天总结活不过一次上下文重置：

- 复盘报告，用 [templates/retro-report.zh-CN.md](templates/retro-report.zh-CN.md)；
- 优化记录，用 [templates/optimization-record.zh-CN.md](templates/optimization-record.zh-CN.md)，
  第 3 步有产出时才写。

然后机械校验一遍：

```bash
python3 scripts/check_retro_report.py path/to/report.md --lang zh
```

`VALID_RETRO` 表示必备小节都在、每条结论都带标签、没有数字缺出处。它只查形式不查真伪。

开工前值得先知道的失败模式：
[anti-patterns.zh-CN.md](references/anti-patterns.zh-CN.md)。
