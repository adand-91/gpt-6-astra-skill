<!-- translation-of: README.md sha256:83a264332f0a6c8e -->

# requirement-ledger

一个管「代码前后那两段」的 agent skill：把真正被要求的东西问清楚，
以及对真正交出去的东西如实汇报。

[English](README.md)

## 它要解决什么

编码 agent 很会写代码，但对写代码前后的两件事很不行。

开头它会**静默补空**。没说的平台、没说的输出格式、没说的验收标准 —— agent 挑一个合理的，
当作既定事实写进方案，三轮之后你才发现整件事做错了方向。从来没人这么说过，
也从来没被标成「这是猜的」。

结尾它会**按新鲜度汇报**。长任务的收尾总结只覆盖最后两轮，因为上下文里就剩这些。
开头谈好的五条需求，既没交付也没提及。仅仅启动了的进程，被写成了「完成」。

这两种失败都很容易防，也都是发现得越晚越贵。

## 三层标注

每条需求带且只带一个可见标签：

| 标签 | 含义 |
|---|---|
| `已确认` | 用户说过，或用户认可了你的复述 |
| `AI推断` | Agent 选的默认值，因为猜错的代价可回滚 |
| `待确认` | 答案会改变交付物、成本、工期或验收 |

硬规则是 `AI推断` 永远不能被写成 `已确认` —— 不在总结里，不在方案里，不在提交信息里。
有默认值没问题，**没标签的**默认值才是 bug。

## 它做什么

- **开工**先复述，然后每轮最多三个问题，按答案能改变多少结果排序。不倾倒长问卷。
- 当猜错的撤销代价很低时**自己定而不是问**，并说明哪些是自己定的。
- **接得住不专业的用户**：给选项而不是逼他写规格；他的方案达不到目的时说出来**并且**给替代方案；
  估算之前先点明哪一项是真正的活。`已确认` 的意思是他说过，不是它正确。
- 在花大成本之前**锁定**一份一屏的确认单 —— 目标、包含、不包含、输入、输出、验收、
  约束、执行位置、未确认项。
- 把之后每个要求当面**归类**成 `缺陷`、`原范围优化` 或 `新增范围`，让范围没法悄悄增减。
- **收尾**时回溯到最早那条需求，逐条结成 `已完成`、`部分完成`、`明确取消` 或 `受阻`，
  并且拿文件系统而不是聊天记录核对。

完全双语：英文是权威源，中文是受校验的镜像，校验脚本接受任一语言写的确认单。

## 安装

### Claude Code

```bash
git clone https://github.com/YOUR-NAME/requirement-ledger ~/.claude/skills/requirement-ledger
```

### Codex

```bash
git clone https://github.com/YOUR-NAME/requirement-ledger ~/.codex/skills/requirement-ledger
```

### 其他 agent

这里没有任何绑定特定运行时的东西。`SKILL.md` 是一份自包含的指令文档，
带 YAML frontmatter 触发条件；`references/` 按需加载。
把 `SKILL.md` 贴进系统提示词、`CLAUDE.md`、`AGENTS.md` 或任何规则文件都能用：

```bash
cat SKILL.zh-CN.md >> AGENTS.md
```

## 脚本

两个都是零模型、零依赖，只用标准库。它们只查形式，不查真伪。

```bash
python3 scripts/check_confirmation_sheet.py sheet.md          # VALID_SHEET 或列出问题
python3 scripts/check_confirmation_sheet.py sheet.md --lang zh
python3 scripts/check_confirmation_sheet.py new.md --baseline old.md   # 抓静默提级
```

`--baseline` 比对确认单的两个版本，任何一条从 `AI推断` 变成 `已确认`
却没有在案的用户确认，就报错。这正是三层标注要防的那种失败，
所以值得用机械手段抓。

```bash
python3 scripts/check_translation_sync.py            # TRANSLATIONS_IN_SYNC 或报漂移
python3 scripts/check_translation_sync.py --update   # 翻译完重新盖章
python3 -m unittest discover -s tests -v             # 37 个测试
```

每个 `*.zh-CN.md` 都记着翻译时英文源文件的 SHA256，
所以一改权威源，镜像就会被机械地判定为「过期」，而不是悄悄变成错的。

## 目录结构

```
SKILL.md                  规范性 skill 文档（agent 实际加载的那份）
SKILL.zh-CN.md            受校验的中文镜像
references/               按需加载：澄清闭环、确认单规则、非专业用户、
                          变更控制、收尾、失败模式（15 条）
                          —— 每份都有 .zh-CN.md 镜像
templates/                确认单，以及九个字段的人话问句版（带示例回答）
                          —— 中英各一份
scripts/                  两个校验脚本
tests/                    unittest，无第三方依赖
```

## 它不是什么

- 不是规划框架、工单系统或方法论。一本账、三个标签、九个字段。
- 不是干活的替代品。失败模式第 3 条专门讲的就是「只澄清不动手」的 agent。
- 不适用于小的、可回滚的请求。给「帮我改个错别字」套一份九字段确认单是纯摩擦，
  而且会教会用户忽略那些真正重要的确认单。见失败模式第 10 条。
- 无法告诉你一份确认单是不是**对的**。脚本校验结构，内容只有用户能确认。

## 许可

MIT，见 [LICENSE](LICENSE)。
