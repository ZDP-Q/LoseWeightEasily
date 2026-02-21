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

class _StreamingMarkdownWidgetState extends State<StreamingMarkdownWidget>
    with SingleTickerProviderStateMixin {
  Timer? _throttleTimer;
  late AnimationController _cursorController;
  late Animation<double> _cursorOpacity;

  static const Duration _throttleInterval = Duration(milliseconds: 80);

  String _pendingText = '';
  String _displayText = '';

  @override
  void initState() {
    super.initState();
    _pendingText = widget.text;
    _cursorController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _cursorOpacity = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _cursorController, curve: Curves.easeInOut),
    );
    if (widget.isStreaming) _cursorController.repeat(reverse: true);

    _displayText = _normalize(widget.text);
  }

  @override
  void didUpdateWidget(covariant StreamingMarkdownWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // 流状态切换
    if (widget.isStreaming != oldWidget.isStreaming) {
      if (widget.isStreaming) {
        _cursorController.repeat(reverse: true);
      } else {
        _cursorController.stop();
        _cursorController.value = 0.0;
      }
    }

    if (widget.text != oldWidget.text) {
      _pendingText = widget.text;
      if (!widget.isStreaming) {
        setState(() {
          _displayText = _normalize(_pendingText);
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
        _displayText = _normalize(_pendingText);
      });
    });
  }

  String _normalize(String text) {
    // 1. 过滤掉 <think>...</think> 标签及其内容
    final thinkRegExp = RegExp(r'<think>[\s\S]*?(?:</think>|$)', caseSensitive: false, multiLine: true);
    String filtered = text.replaceAll(thinkRegExp, '');
    filtered = filtered.replaceAll(RegExp(r'</think>', caseSensitive: false), '');
    
    // 2. 修复 Markdown 标题：确保 # 后有空格 (全局检测，不依赖行首)
    // 匹配井号序列后紧跟非空格、非换行、非井号字符的情况，插入空格
    filtered = filtered.replaceAllMapped(
      RegExp(r'(#+)([^\s#\n])'),
      (match) => '${match.group(1)} ${match.group(2)}',
    );
    
    // 3. 修复标题上方的空行 (极致修复版)
    // 匹配任何非换行符紧跟标题，或者单个换行符紧跟标题的情况
    // 这涵盖了 "文本###" 以及 "文本\n###"
    filtered = filtered.replaceAllMapped(
      RegExp(r'([^\n])\n?((?: {0,3})#+ +)'),
      (match) => '${match.group(1)}\n\n${match.group(2)}',
    );

    // 4. 修复 Markdown 列表符号后的空格
    filtered = filtered.replaceAllMapped(
      RegExp(r'^(\s*[-*+·])([^\s\-\*\+\s\n])', multiLine: true),
      (match) => '${match.group(1)} ${match.group(2)}',
    );
    
    // 5. 统一列表符号并补齐上方空行
    filtered = filtered.replaceAllMapped(
      RegExp(r'([^\n])\n?(\s*[-*+]\s+)', multiLine: true),
      (match) {
        final content = match.group(1)!;
        final listStart = match.group(2)!;
        // 如果上一行不是列表项且不是空行，补两个换行
        if (!RegExp(r'^\s*[-*+]\s+').hasMatch(content)) {
          return '$content\n\n$listStart';
        }
        return '$content\n$listStart';
      },
    );
    
    return filtered.replaceAll('\r\n', '\n');
  }

  String _repairStreamingMarkdown(String markdown) {
    if (markdown.isEmpty) return markdown;
    var text = markdown;

    // 针对流式标题的特殊补全：如果最后一行以 # 结尾但没有内容，补全一个空格以触发标题渲染
    if (RegExp(r'\n(?: {0,3})#+$').hasMatch(text) || text.startsWith('#')) {
       if (text.endsWith('#')) {
         text = '$text ';
       }
    }

    // 2. 修复行内代码 (Inline Code)
    final backtickCount = '`'.allMatches(text).length;
    if (backtickCount.isOdd && !text.endsWith('```')) {
      text = '$text`';
    }

    // 3. 修复链接和图片 [text](url
    // 先找最后一个 '['
    int lastBracket = text.lastIndexOf('[');
    int lastCloseBracket = text.lastIndexOf(']');
    if (lastBracket > lastCloseBracket) {
      // 正在写 [text
      text = '$text]';
    }

    // 再处理链接部分 (url
    int lastParen = text.lastIndexOf('(');
    int lastCloseParen = text.lastIndexOf(')');
    if (lastParen > lastCloseParen) {
      // 检查 '(' 前面是不是刚闭合的 ']'
      String beforeParen = text.substring(0, lastParen).trimRight();
      if (beforeParen.endsWith(']')) {
         text = '$text)';
      }
    }

    // 4. 修复加粗和斜体 (Bold & Italic)
    // 简单的计数补全，处理 ** 和 __
    text = _closeTag(text, '**');
    text = _closeTag(text, '__');
    
    // 处理单星号 * (稍微复杂点，因为它可能是列表)
    // 如果 * 后面紧跟空格，通常是列表，不需要补全
    final starCount = '*'.allMatches(text).length;
    if (starCount.isOdd) {
      int lastStar = text.lastIndexOf('*');
      // 如果不是行首的列表符，则尝试闭合
      bool isList = lastStar == 0 || text[lastStar - 1] == '\n';
      if (!isList) {
        text = '$text*';
      }
    }

    return text;
  }

  String _closeTag(String text, String tag) {
    int count = 0;
    int pos = text.indexOf(tag);
    while (pos != -1) {
      count++;
      pos = text.indexOf(tag, pos + tag.length);
    }
    if (count.isOdd) {
      return '$text$tag';
    }
    return text;
  }

  @override
  void dispose() {
    _throttleTimer?.cancel();
    _cursorController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final content = widget.isStreaming
        ? _repairStreamingMarkdown(_displayText)
        : _displayText;

    final children = <Widget>[_buildMarkdownBody(content)];

    if (widget.isStreaming) {
      children.add(
        AnimatedBuilder(
          animation: _cursorOpacity,
          builder: (context, _) {
            final visible = _cursorOpacity.value > 0.5;
            return Opacity(
              opacity: visible ? 1 : 0,
              child: const Padding(
                padding: EdgeInsets.only(top: 4.0),
                child: Text('▊', style: TextStyle(fontSize: 14, color: Colors.blueAccent)),
              ),
            );
          },
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: children,
    );
  }

  Widget _buildMarkdownBody(String data) {
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
