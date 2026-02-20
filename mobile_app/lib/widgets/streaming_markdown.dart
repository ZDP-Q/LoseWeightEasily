import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:markdown/markdown.dart' as md;
import '../utils/streaming_markdown_parser.dart';
import '../utils/ark_protocol_syntax.dart';
import '../utils/ark_component_builder.dart';

/// 终极版 StreamingMarkdownWidget
/// 
/// 核心改进：
/// 1. **不再物理分块**：将整个文本传递给一个 MarkdownBody，彻底解决格式上下文丢失（全剧加粗）问题。
/// 2. **语法树扩展**：使用 ArkProtocolSyntax 在 AST 层面拦截自定义协议。
/// 3. **局部构建**：使用 ArkComponentBuilder 渲染原生卡片。
/// 4. **零抖动**：去除 Column 嵌套和不稳定的 Key，利用 MarkdownBody 自身的 diff 机制。
class StreamingMarkdownWidget extends StatefulWidget {
  final String text;
  final bool isStreaming;
  final MarkdownStyleSheet? styleSheet;
  final bool selectable;
  final MarkdownTapLinkCallback? onTapLink;

  const StreamingMarkdownWidget({
    super.key,
    required this.text,
    this.isStreaming = false,
    this.styleSheet,
    this.selectable = true,
    this.onTapLink,
  });

  @override
  State<StreamingMarkdownWidget> createState() =>
      _StreamingMarkdownWidgetState();
}

class _StreamingMarkdownWidgetState extends State<StreamingMarkdownWidget>
    with SingleTickerProviderStateMixin {
  final StreamingMarkdownParser _markdownParser = StreamingMarkdownParser();
  Timer? _throttleTimer;
  String _pendingText = '';
  bool _hasPendingUpdate = false;

  late AnimationController _cursorController;
  late Animation<double> _cursorOpacity;

  static const _throttleInterval = Duration(milliseconds: 32); // 保持流畅

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
  }

  @override
  void didUpdateWidget(covariant StreamingMarkdownWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isStreaming != oldWidget.isStreaming) {
      if (widget.isStreaming) {
        _cursorController.repeat(reverse: true);
      } else {
        _cursorController.stop();
        _cursorController.value = 0.0;
        _flushPending();
      }
    }

    if (widget.text != oldWidget.text) {
      if (widget.isStreaming) {
        _scheduleThrottledUpdate();
      } else {
        setState(() {
          _pendingText = widget.text;
          _hasPendingUpdate = false;
        });
      }
    }
  }

  void _scheduleThrottledUpdate() {
    _pendingText = widget.text;
    _hasPendingUpdate = true;
    if (_throttleTimer?.isActive ?? false) return;
    _flushPending();
    _throttleTimer = Timer(_throttleInterval, () {
      if (_hasPendingUpdate && mounted) _flushPending();
    });
  }

  void _flushPending() {
    if (!_hasPendingUpdate && !widget.isStreaming) return;
    setState(() { _hasPendingUpdate = false; });
  }

  @override
  void dispose() {
    _throttleTimer?.cancel();
    _cursorController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _cursorOpacity,
      builder: (context, _) {
        final String cursor = widget.isStreaming 
            ? (_cursorOpacity.value > 0.5 ? "▊" : "") 
            : "";
        
        final String displayText = _markdownParser.parse(
          _pendingText, 
          isStreaming: widget.isStreaming, 
          cursor: cursor
        );

        return MarkdownBody(
          data: displayText,
          selectable: widget.selectable,
          styleSheet: widget.styleSheet,
          onTapLink: widget.onTapLink,
          fitContent: true,
          softLineBreak: true,
          // 关键：注册自定义语法拦截器
          blockSyntaxes: const [
            ArkProtocolSyntax(),
          ],
          // 关键：注册元素构造器渲染原生卡片
          builders: {
            'ark_component': ArkComponentBuilder(isStreaming: widget.isStreaming),
          },
        );
      },
    );
  }
}
