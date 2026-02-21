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
      final raw = _normalize(_pendingText);
      final repaired = widget.isStreaming ? _repairStreamingMarkdown(raw) : raw;
      setState(() {
        _displayText = repaired;
      });
    });
  }

  String _normalize(String text) {
    return text.replaceAll('\r\n', '\n');
  }

  String _repairStreamingMarkdown(String markdown) {
    var text = markdown;

    final fenceRe = RegExp(r'(^|\n)(`{3,}|~{3,})[^\n]*', multiLine: true);
    final matches = fenceRe.allMatches(text).toList();
    if (matches.length.isOdd && matches.isNotEmpty) {
      final raw = matches.last.group(2) ?? '```';
      final closeFence = raw.startsWith('~') ? '~~~' : '```';
      text = '$text\n$closeFence';
    }

    final backtickCount = '`'.allMatches(text).length;
    if (backtickCount.isOdd) {
      text = '$text`';
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
