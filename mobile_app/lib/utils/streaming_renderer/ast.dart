enum NodeStatus {
  open,
  tentative,
  closed,
  invalid,
}

abstract class SNode {
  NodeStatus status;
  String? key;
  SNode({this.status = NodeStatus.open, this.key});
}

abstract class SBlockNode extends SNode {
  SBlockNode({super.status, super.key});
  
  // 核心：缓存生成的 Markdown 文本，避免在渲染层重复计算
  String cachedMarkdown = '';
  
  void updateMarkdown();
}

class ParagraphNode extends SBlockNode {
  final List<SInlineNode> children = [];
  ParagraphNode({super.status, super.key});

  @override
  void updateMarkdown() {
    cachedMarkdown = children.whereType<TextNode>().map((e) => e.content).join();
  }
}

class CodeBlockNode extends SBlockNode {
  final String fence;
  final String? language;
  final List<String> lines = [];
  CodeBlockNode({required this.fence, this.language, super.status, super.key});

  @override
  void updateMarkdown() {
    final buffer = StringBuffer();
    buffer.writeln('$fence${language ?? ""}');
    for (final line in lines) {
      buffer.writeln(line);
    }
    if (status == NodeStatus.closed) {
      buffer.write(fence);
    }
    cachedMarkdown = buffer.toString();
  }
}

class HeadingNode extends SBlockNode {
  final int level;
  final List<SInlineNode> children = [];
  HeadingNode({required this.level, super.status, super.key});

  @override
  void updateMarkdown() {
    cachedMarkdown = '${"#" * level} ${children.whereType<TextNode>().map((e) => e.content).join()}';
  }
}

class QuoteNode extends SBlockNode {
  final List<SBlockNode> children = [];
  QuoteNode({super.status, super.key});

  @override
  void updateMarkdown() {
    cachedMarkdown = '> 引用内容正在生成...';
  }
}

abstract class SInlineNode extends SNode {
  SInlineNode({super.status});
}

class TextNode extends SInlineNode {
  final String content;
  TextNode(this.content, {super.status});
}

class SpanNode extends SInlineNode {
  final String marker;
  final List<SInlineNode> children = [];
  SpanNode({required this.marker, super.status});
}

class InlineCodeNode extends SInlineNode {
  final String content;
  InlineCodeNode(this.content, {super.status});
}
