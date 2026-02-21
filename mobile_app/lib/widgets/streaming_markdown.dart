import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

/// 流式 Markdown 渲染组件（语义优先版）
///
/// 算法要点：
/// 1. 单文档渲染：始终让 Markdown 在完整上下文中解析，避免标题/列表/表格断裂。
/// 2. 节流刷新：降低流式高频更新压力。
/// 3. 最小补全：仅补全未闭合代码围栏与反引号，减少流式中断裂。
class StreamingMarkdownWidget extends StatefulWidget {
  final String text;
  final bool isStreaming;
  final ScrollController? scrollController;
  final bool selectable;
  final MarkdownStyleSheet? styleSheet;
  final MarkdownTapLinkCallback? onTapLink;

  const StreamingMarkdownWidget({
    super.key,
    required this.text,
    this.isStreaming = false,
    this.scrollController,
    this.selectable = true,
    this.styleSheet,
    this.onTapLink,
  });

  @override
  State<StreamingMarkdownWidget> createState() =>
      _StreamingMarkdownWidgetState();
}

class _StreamingMarkdownWidgetState extends State<StreamingMarkdownWidget> {
  Timer? _throttleTimer;
  static const Duration _throttleInterval = Duration(milliseconds: 80);

  String _pendingText = '';
  String _displayText = '';

  @override
  void initState() {
    super.initState();
    _pendingText = widget.text;
    _displayText = widget.text;
  }

  @override
  void didUpdateWidget(covariant StreamingMarkdownWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.text != oldWidget.text) {
      _pendingText = widget.text;
      if (!widget.isStreaming) {
        setState(() {
          _displayText = _pendingText;
        });
      } else {
        _scheduleRebuild();
      }
    }
  }

  void _scheduleRebuild() {
    if (_throttleTimer?.isActive ?? false) return;
    _throttleTimer = Timer(_throttleInterval, () {
      if (!mounted) return;
      setState(() {
        _displayText = _pendingText;
      });
    });
  }

  String _processStream(String raw) {
    if (raw.isEmpty) return raw;

    // 1. 过滤思考内容 (DeepSeek/Qwen 兼容)
    final thinkRegExp = RegExp(r'<think>[\s\S]*?(?:</think>|$)', caseSensitive: false, multiLine: true);
    String text = raw.replaceAll(thinkRegExp, '');
    text = text.replaceAll(RegExp(r'</think>', caseSensitive: false), '');

    // 2. 结构化纠偏 (Structural Guarding V3.0)
    // 确保标题 # 前有双换行 (暴力纠正，前后端双保险)
    text = text.replaceAllMapped(
      RegExp(r'([^\n])\n?((?: {0,3})#+ +)'),
      (match) => '${match.group(1)}\n\n${match.group(2)}',
    );
    // 确保 # 后有空格 (防止 #Title 这种格式)
    text = text.replaceAllMapped(
      RegExp(r'(#+)([^\s#\n])'),
      (match) => '${match.group(1)} ${match.group(2)}',
    );
    // 修复列表符号 [-*+·] 后的空格
    text = text.replaceAllMapped(
      RegExp(r'^(\s*[-*+·])([^\s\-\*\+\s\n])', multiLine: true),
      (match) => '${match.group(1)} ${match.group(2)}',
    );
    // 列表上方的换行纠正 (列表与普通文本之间必须有空行)
    text = text.replaceAllMapped(
      RegExp(r'([^\n])\n?(\s*[-*+·]\s+)', multiLine: true),
      (match) {
        final content = match.group(1)!;
        final listStart = match.group(2)!;
        // 如果上一行不是列表项且不是换行符，补双换行
        if (!RegExp(r'^\s*[-*+·]\s+').hasMatch(content)) {
          return '$content\n\n$listStart';
        }
        return '$content\n$listStart';
      },
    );

    // 3. 标签自动补全 (Auto-Close Algorithm)
    // 只有在流式传输时才进行补全，避免最终状态被篡改
    if (widget.isStreaming) {
      // 代码块围栏补全
      final codeFenceCount = '```'.allMatches(text).length;
      if (codeFenceCount.isOdd) {
        text = '$text\n```';
      } else {
        // 行内代码补全
        final backtickCount = '`'.allMatches(text).length;
        if (backtickCount.isOdd) text = '$text`';
      }

      // 链接/图片 [text](url 补全
      int lastBracket = text.lastIndexOf('[');
      int lastCloseBracket = text.lastIndexOf(']');
      if (lastBracket > lastCloseBracket) text = '$text]';

      int lastParen = text.lastIndexOf('(');
      int lastCloseParen = text.lastIndexOf(')');
      if (lastParen > lastCloseParen) {
        // 如果前面刚闭合了 ]，那说明是链接地址部分
        String sub = text.substring(0, lastParen).trimRight();
        if (sub.endsWith(']')) text = '$text)';
      }

      // 加粗/斜体补全 (** 和 __)
      text = _autoClosePair(text, '**');
      text = _autoClosePair(text, '__');
      
      // 单星号斜体 (排除列表项的情况)
      final starCount = '*'.allMatches(text).length;
      if (starCount.isOdd) {
        int lastStar = text.lastIndexOf('*');
        bool isList = lastStar == 0 || text[lastStar - 1] == '\n';
        if (!isList) text = '$text*';
      }

      // 4. 视觉闪烁抑制 (Look-ahead Suppression)
      // 如果末尾正好是这些符号，先不渲染它们，等待下一个 token
      if (text.endsWith('**') || text.endsWith('__')) {
        text = text.substring(0, text.length - 2);
      } else if (text.endsWith('*') || text.endsWith('_') || text.endsWith('#') || text.endsWith('`') || text.endsWith('[')) {
        text = text.substring(0, text.length - 1);
      }
      
      // 5. 光标集成 (Inline Cursor)
      // 将光标作为文本的一部分，确保它随排版流动
      text = '$text ▊';
    }

    return text.replaceAll('\r\n', '\n');
  }

  String _autoClosePair(String text, String pair) {
    int count = 0;
    int pos = text.indexOf(pair);
    while (pos != -1) {
      count++;
      pos = text.indexOf(pair, pos + pair.length);
    }
    return count.isOdd ? '$text$pair' : text;
  }

  @override
  void dispose() {
    _throttleTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final data = _processStream(_displayText);

    return MarkdownBody(
      data: data,
      selectable: widget.selectable,
      styleSheet: widget.styleSheet,
      onTapLink: widget.onTapLink,
      fitContent: true,
      softLineBreak: true,
    );
  }
}
