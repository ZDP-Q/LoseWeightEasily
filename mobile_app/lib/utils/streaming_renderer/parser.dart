import 'ast.dart';
import 'lexer.dart';

/// 增量 AST 构建器 (V3 - 彻底性能优化版)
class IncrementalASTBuilder {
  final List<SBlockNode> _blocks = [];
  SBlockNode? _currentBlock;
  bool _isNewLine = true;
  int _consecutiveNewlines = 0;

  // 状态机变量
  String _codeFence = '';
  int _pendingBackticks = 0;

  List<SBlockNode> get blocks => _blocks;

  void clear() {
    _blocks.clear();
    _currentBlock = null;
    _isNewLine = true;
    _consecutiveNewlines = 0;
    _codeFence = '';
    _pendingBackticks = 0;
  }

  void consume(List<Token> tokens) {
    for (final token in tokens) {
      _processToken(token);
    }
    
    // 关键：在这一批 Token 处理完毕后，仅刷新当前活跃块的内容缓存
    if (_currentBlock != null) {
      _currentBlock!.updateMarkdown();
    }
  }

  void _processToken(Token token) {
    if (token.type == TokenType.newline) {
      _consecutiveNewlines++;
      _isNewLine = true;
      
      if (_currentBlock is CodeBlockNode) {
        final node = _currentBlock as CodeBlockNode;
        node.lines.add('');
        node.updateMarkdown(); // 代码块内的每一行都要实时更新缓存
        return;
      }
      
      if (_consecutiveNewlines >= 2) {
        if (_currentBlock != null) {
          _currentBlock!.status = NodeStatus.closed;
          _currentBlock!.updateMarkdown(); // 关闭前最后一次更新
          _currentBlock = null;
        }
      }
      return;
    }

    if (token.type != TokenType.space) {
      _consecutiveNewlines = 0;
    }

    if (_currentBlock is CodeBlockNode) {
      _handleInCodeBlock(token);
      return;
    }

    if (_isNewLine && token.type != TokenType.space) {
      if (_tryStartNewBlock(token)) {
        _isNewLine = false;
        return;
      }
    }

    _isNewLine = false;
    _ensureParagraph();
    _handleInline(token);
  }

  void _handleInCodeBlock(Token token) {
    final node = _currentBlock as CodeBlockNode;
    if (token.type == TokenType.backtick || token.type == TokenType.tilde) {
      _pendingBackticks++;
      if (_pendingBackticks >= 3 && token.content == node.fence[0]) {
        node.status = NodeStatus.closed;
        node.updateMarkdown();
        _currentBlock = null;
        _pendingBackticks = 0;
        return;
      }
    } else {
      _pendingBackticks = 0;
    }

    if (node.lines.isEmpty) node.lines.add('');
    node.lines[node.lines.length - 1] += token.content;
  }

  bool _tryStartNewBlock(Token token) {
    if (token.type == TokenType.backtick || token.type == TokenType.tilde) {
      _codeFence += token.content;
      if (_codeFence.length >= 3) {
        final node = CodeBlockNode(
          fence: _codeFence,
          status: NodeStatus.open,
          key: 'code_${DateTime.now().microsecondsSinceEpoch}',
        );
        _addBlock(node);
        _codeFence = '';
        return true;
      }
      return false;
    }
    _codeFence = '';

    if (token.type == TokenType.hash) {
      _addBlock(HeadingNode(
        level: 1,
        status: NodeStatus.open,
        key: 'h_${DateTime.now().microsecondsSinceEpoch}',
      ));
      return true;
    }
    return false;
  }

  void _ensureParagraph() {
    if (_currentBlock == null) {
      _addBlock(ParagraphNode(
        status: NodeStatus.open,
        key: 'p_${DateTime.now().microsecondsSinceEpoch}',
      ));
    }
  }

  void _addBlock(SBlockNode node) {
    if (_currentBlock != null) {
      _currentBlock!.status = NodeStatus.closed;
      _currentBlock!.updateMarkdown();
    }
    _blocks.add(node);
    _currentBlock = node;
  }

  void _handleInline(Token token) {
    final block = _currentBlock;
    if (block is ParagraphNode) {
      _appendText(block.children, token.content);
    } else if (block is HeadingNode) {
      _appendText(block.children, token.content);
    }
  }

  void _appendText(List<SInlineNode> children, String text) {
    if (children.isNotEmpty && children.last is TextNode) {
      final last = children.last as TextNode;
      children[children.length - 1] = TextNode(last.content + text);
    } else {
      children.add(TextNode(text));
    }
  }

  void finalize() {
    for (final block in _blocks) {
      block.status = NodeStatus.closed;
      block.updateMarkdown();
    }
    _currentBlock = null;
  }
}
