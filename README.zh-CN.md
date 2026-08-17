<!-- translation-of: README.md sha256:879780ef889c58c6 -->

# requirement-ledger

一个 agent skill：把项目自己的对话读回来，告诉你三件事 —— 用户真正需要的是什么、
哪儿出了错以及错在哪一层、哪些重复的活值得做成一个 Skill。

[English](README.md)

## 它要解决什么

项目结束后大家会问的那些问题，答案本来就在对话记录里。没人回头读，
所以答案丢了，同一个错要付两遍钱。

让 agent 直接总结一下，你得到的东西比不做更糟：肉眼估的数字、
把开场那句请求当成需求、一张按「有多吵」排序的报错清单，
以及把最后两轮的总结当成整个项目的总结。然后这份文档会被当事实引用。

对话记录能好好回答这三个问题，但前提是**计数必须机械，引用必须逐字**。

## 它怎么工作

**第 0 步永远是脚本。** `scan_transcript.py` 读 Claude Code、Codex 或纯文本对话记录，
报出那些不许猜的东西：真实用户回合、每条用户原话、纠偏、失败的工具调用、
重复的命令形状、重复的工具序列。然后模型才开始解释 ——
而且不许产出脚本没报过的数字。

**第 1 步 真需求。** 从纠偏里建，不从第一条消息里建。每一次纠偏都标出
「交出去的东西」和「想要的东西」岔开的位置，而他用来掰回来的那句话，
通常直接把需求说了出来。然后反向回溯到**最早**那条需求，逐条记它的去向：
已完成、部分完成、明确取消、受阻，还是静默丢弃。

**第 2 步 错误。** 每条判一个层级，因为层级决定这事修不修得动：规则缺失、
规则没触发、规则冲突、位置错误、工具限制、一次性。只有前四种能动手，
而把前两种搞混，产出的规则注定不起作用。

**第 3 步 可自动化的部分。** 重复是「该去看看」的触发条件，不是「必须建」的命令。
判据是**判断是否稳定**，不是按键是否重复。「本轮不新增 Skill」是正常结论。

三个标签贯穿全程且绝不混：`原话`（他的话，逐字，带时间戳）、
`推断`（你的解读，标成你的）、`未知`（对话回答不了 —— 就写未知，不许填上）。

## 安装

### Claude Code

```bash
git clone https://github.com/adand-91/requirement-ledger ~/.claude/skills/requirement-ledger
```

### Codex

```bash
git clone https://github.com/adand-91/requirement-ledger ~/.codex/skills/requirement-ledger
```

### 其他 agent

`SKILL.md` 是一份自包含的指令文档；`references/` 按需加载，脚本是纯 Python。
贴进系统提示词、`CLAUDE.md`、`AGENTS.md` 或任何规则文件都能用：

```bash
cat SKILL.zh-CN.md >> AGENTS.md
```

## 机械层

零依赖，只用标准库。

```bash
python3 scripts/scan_transcript.py --engine both --since 7d
python3 scripts/scan_transcript.py --engine claude --project myproject --format json --out facts.json
python3 scripts/scan_transcript.py path/to/session.jsonl
python3 scripts/scan_transcript.py --engine both --since 7d --no-text   # 可安全外发
```

真实对话记录是很凶的，这个脚本是围着这一点写的，不是围着理想情况写的：

- 会话能到 250 MB，单行能有 152 万字符的 base64。它逐行流式读，
  超长行只量不解析，从不解码 base64。大约 3 秒 1 GB；
  带 `--since` 时先按 mtime 跳过过期文件。
- **两个引擎都把工具输出当用户消息回灌。** 把那些算进去，
  一段 79 个回合的对话会变成 918 个「用户回合」，而且需求提炼会被工具日志污染。
  Claude 适配器排除 `tool_result` 块；Codex 适配器优先用
  `event_msg/user_message`，那才是真正手敲的输入。
- Claude Code 用 slug 化的 cwd 给目录命名，所有非 ASCII 字符都变成短横 ——
  一个叫 `接单工作台` 的项目住在 `-Users-…-Desktop------` 里，
  只能靠每个文件内部记录的 cwd 找到。`--project` 两边都匹配。
- 纠偏是关键词召回，所以只作为**候选**上报。「这个不错」含「不」但是在夸。
  每一条由模型判定。

## 校验产出

```bash
python3 scripts/check_retro_report.py report.md          # VALID_RETRO 或列出问题
python3 scripts/check_retro_report.py report.md --lang zh
python3 scripts/check_translation_sync.py                # 中文镜像有没有过期
python3 -m unittest discover -s tests -v                 # 56 个测试
```

`check_retro_report.py` 拦掉那些会让复盘变得有害的写法：数字没有出处、
结论没有标签、缺窗口或窗口没写时区偏移、用程度词冒充实测、
为了显得完整而凑出来的空小节。它只查形式不查真伪。中英文小节名和标签都认。

## 目录结构

```
SKILL.md                  规范性 skill 文档（agent 实际加载的那份）
SKILL.zh-CN.md            受校验的中文镜像
references/               取证规则、真需求提炼、错误层级、
                          Skill 提炼、16 条失败模式 —— 每份都有 .zh-CN.md 镜像
templates/                复盘报告 和 优化记录，中英各一份
scripts/                  scan_transcript.py（机械层）、
                          check_retro_report.py、check_translation_sync.py
tests/                    unittest，无第三方依赖
```

每个 `*.zh-CN.md` 都记着英文源的 SHA256，所以一改权威源，
镜像就会被机械地判定为过期，而不是悄悄变成错的。

## 它不是什么

- 不是任务进行中的需求澄清。它是往回跑的，处理已经发生过的活。
- 不是看板或指标工具。那些计数存在的意义是让文字保持诚实。
- 无法判断一份报告是不是**对的**。脚本校验结构；内容只有当时在场的人能确认。
- 不是一个可以放着不管的 Skill 生成器。它出提案；只有收到明确开干才写真的
  `SKILL.md`，而没人验证过的生成 Skill 是一个带着触发器的负债。

## 隐私

脚本读你本机的对话记录，输出里按设计包含逐字用户原文 —— 那些原文就是证据。
不上传任何东西。任何你打算外发、粘贴或附上的输出，都用 `--no-text`：
它保留全部计数，去掉引文。

## 许可

MIT，见 [LICENSE](LICENSE)。
