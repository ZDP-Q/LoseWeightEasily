import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../utils/markdown_util.dart';

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
  String _processedData = '';

  @override
  void initState() {
    super.initState();
    _pendingText = widget.text;
    _displayText = widget.text;
    _processedData = MarkdownUtil.format(_displayText, isStreaming: widget.isStreaming);
  }

  @override
  void didUpdateWidget(covariant StreamingMarkdownWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.text != oldWidget.text || widget.isStreaming != oldWidget.isStreaming) {
      _pendingText = widget.text;
      if (!widget.isStreaming) {
        setState(() {
          _displayText = _pendingText;
          _processedData = MarkdownUtil.format(_displayText, isStreaming: false);
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
        _processedData = MarkdownUtil.format(_displayText, isStreaming: widget.isStreaming);
      });
    });
  }

  @override
  void dispose() {
    _throttleTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MarkdownBody(
      data: _processedData,
      selectable: widget.selectable,
      styleSheet: widget.styleSheet,
      onTapLink: widget.onTapLink,
      fitContent: true,
      softLineBreak: true,
    );
  }
}
