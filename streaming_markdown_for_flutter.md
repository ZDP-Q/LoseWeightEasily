# 面向 LLM 流式输出的 Markdown 渲染算法设计（Flutter 适用）

## 1. 背景与目标

在 LLM（大语言模型）**流式输出**（chunk/token 逐步到达）的场景下，传统 Markdown 渲染器（一次性解析完整文本）会面临：

- Markdown 结构尚未闭合（代码块、强调、列表等）
- UI 频繁抖动、闪烁
- 需要在“当前不完整内容”和“最终完整结果”之间保持一致性

**目标**：

- 流式安全（Streaming-safe）
- 渐进渲染（Progressive Rendering）
- 最终一致（Final Consistency）
- 支持回滚与修正（Speculative + Revertible）

---

## 2. 总体架构（三层模型）

```
LLM 流式输出
      ↓
Streaming Lexer（流式词法层）
      ↓
Incremental AST Builder（增量语法树）
      ↓
Speculative Renderer（推测式渲染）
      ↓
Flutter UI
```

---

## 3. 核心思想：推测 + 可撤销

> 不要求每一步都完全正确  
> 但要求：**任何一步都可以被修正**

---

## 4. 第一层：Streaming Lexer（流式词法分析）

### 4.1 职责

- 逐字符 / 逐 chunk 读取
- 不回退字符
- 不构建 Markdown 结构，仅输出 Token

### 4.2 Token 示例

```dart
enum TokenType {
  text,
  newline,
  star,      // *
  backtick,  // `
  dash,      // -
  gt,        // >
  hash,      // #
  pipe,      // |
}
```

### 4.3 跨 Chunk 状态

```dart
class LexerState {
  int pendingBackticks = 0;
  int pendingStars = 0;
}
```

---

## 5. 第二层：Incremental AST Builder（增量语法树）

### 5.1 Streaming AST（S-AST）

区别于标准 Markdown AST，每个节点带有**状态**：

```dart
enum NodeStatus {
  open,       // 尚未结束
  tentative,  // 推测结构
  closed,     // 已确认
  invalid,    // 被推翻
}
```

### 5.2 代码块节点示例

```dart
class CodeBlockNode {
  String fence;        // ```
  String? language;    // js / dart
  List<String> content;
  NodeStatus status;
}
```

规则：

- 收到 ``` → OPEN
- 再次收到 ``` → CLOSED
- EOF 未闭合 → 强制 CLOSED（修复）

### 5.3 强调（Bold / Italic）

```markdown
**hello
```

处理策略：

- 初始为 TENTATIVE
- 若后续闭合 → CLOSED
- 若段落结束仍未闭合 → INVALID → 降级为普通文本

---

## 6. 第三层：Speculative Renderer（推测式渲染）

### 6.1 渲染原则

- CLOSED：完全语义化渲染
- OPEN / TENTATIVE：**弱语义渲染**
- INVALID：回退为纯文本

### 6.2 Flutter 渲染建议

| AST 状态    | Flutter Widget      |
| --------- | ------------------- |
| OPEN      | Container + Opacity |
| TENTATIVE | RichText（标记可回滚）     |
| CLOSED    | 正常 Markdown Widget  |

示例：

```dart
Opacity(
  opacity: 0.6,
  child: CodeBlockWidget(code),
)
```

---

## 7. Render Island（最小重渲染单元）

- 每个 Block Node = 一个 Render Island
- 仅重绘：
  - 最近仍处于 OPEN / TENTATIVE 的节点
- 已 CLOSED 的节点不再重建 Widget

优势：

- 降低 Flutter rebuild 成本
- 避免整棵 Widget Tree 抖动

---

## 8. EOF（流结束）最终修复规则

在 LLM 输出结束时，执行 Finalization Pass：

1. 所有 OPEN → CLOSED
2. 所有 TENTATIVE：
   - 能自洽 → CLOSED
   - 否则 → INVALID（转 TEXT）
3. 重新执行一次最终渲染

保证：

> 最终渲染结果 == 非流式 Markdown 渲染结果

---

## 9. 性能与工程建议（Flutter）

- UI 刷新 ≤ 30 FPS（Ticker / Timer）
- Lexer / AST 可更高频运行（Isolate）
- 使用 ValueNotifier / StreamBuilder 局部刷新
- AST 与 Widget Tree 解耦

---

## 10. 总结

> **这是一个“永远在猜，但从不怕猜错”的 Markdown 渲染算法**

它特别适合：

- Chat UI
- Copilot / AI Assistant
- Flutter + LLM 流式输出场景

---

如需：

- Flutter 具体代码骨架
- 与 markdown_it / flutter_markdown 的对比
- 完整 Demo 架构

可在此设计之上继续扩展。
