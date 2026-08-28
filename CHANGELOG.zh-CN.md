<!-- translation-of: CHANGELOG.md sha256:bce723bd0186734e -->

# 变更日志

本项目的显著变化均记录在这里。版本遵循
[语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

暂无变更。

## [0.1.0] - 2026-08-28

### 新增

- 可安装、零运行时依赖的标准包与 `requirement-ledger` 命令。
- 显式输入的 Claude、Codex 和纯文本事件规范化。
- 版本化证据、问题、建议与验证记录。
- 不读取 remote 的只读 Git 快照。
- 私有证据、保守四类归因、无原话报告与修复草案。
- 合成端到端 Demo、CI 矩阵、Issue Forms、安全／支持／贡献政策、维护策略、威胁模型、架构、
  范围账本与发布检查清单。

### 安全

- 新工作流不发现主目录，也不运行项目代码。
- 分享报告使用失败即停止的自动隐私闸门，并且仍需人工复核。
- 修复建议始终为 `DRAFT — NOT SENT` 与 `not-applied`。
- 生成的反馈在真人发送之前始终为 `DRAFT — NOT SENT`。
- 本地动作始终是建议，绝不自动应用。
- CLI 不运行项目代码、不安装依赖、不联网、不遥测，也不执行 commit、push、Issue、PR、
  Release 或上传。
- 仓库文本固定为 LF，确保 Windows 上双语哈希确定；transcript 绑定将同一文件身份与跨平台稳定的
  内容元数据分开验证。
