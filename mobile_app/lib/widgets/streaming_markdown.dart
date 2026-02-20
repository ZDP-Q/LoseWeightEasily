import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../utils/streaming_markdown_parser.dart';

/// 流式 Markdown 渲染组件
///
/// 工程化解决 LLM 流式输出的 Markdown 渲染问题：
/// 1. **节流渲染**：合并高频 setState，保证最高 ~30fps 的渲染频率
/// 2. **FSM 解析**：使用 [StreamingMarkdownParser] 安全闭合不完整的 Markdown
/// 3. **光标动画**：流式输出时在文本末尾显示闪烁光标
/// 4. **RepaintBoundary**：隔离重绘范围，减少不必要的重绘
class StreamingMarkdownWidget extends StatefulWidget {
  /// 当前累积的完整文本
  final String text;

  /// 是否正在流式接收
  final bool isStreaming;

  /// Markdown 样式表
  final MarkdownStyleSheet? styleSheet;

  /// 是否可选择文本
  final bool selectable;

  /// 链接点击回调
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
  final StreamingMarkdownParser _parser = StreamingMarkdownParser();

  // 节流控制
  Timer? _throttleTimer;
  String _renderedText = '';
  String _pendingText = '';
  bool _hasPendingUpdate = false;

  // 光标动画
  late AnimationController _cursorController;
  late Animation<double> _cursorOpacity;

  /// 节流间隔：33ms ≈ 30fps，在流畅度与性能间取平衡
  static const _throttleInterval = Duration(milliseconds: 33);

  @override
  void initState() {
    super.initState();
    _renderedText = _parseText(widget.text, widget.isStreaming);

    _cursorController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _cursorOpacity = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _cursorController, curve: Curves.easeInOut),
    );
    if (widget.isStreaming) {
      _cursorController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(covariant StreamingMarkdownWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    // 流式状态变化
    if (widget.isStreaming != oldWidget.isStreaming) {
      if (widget.isStreaming) {
        _cursorController.repeat(reverse: true);
      } else {
        _cursorController.stop();
        _cursorController.value = 0.0;
        // 流结束时立即渲染最终文本
        _flushPending();
        setState(() {
          _renderedText = _parseText(widget.text, false);
        });
      }
    }

    // 文本变化 — 节流处理
    if (widget.text != oldWidget.text) {
      if (widget.isStreaming) {
        _scheduleThrottledUpdate();
      } else {
        // 非流式直接更新
        setState(() {
          _renderedText = _parseText(widget.text, widget.isStreaming);
        });
      }
    }
  }

  void _scheduleThrottledUpdate() {
    _pendingText = widget.text;
    _hasPendingUpdate = true;

    // 如果已有定时器在运行，等待它触发
    if (_throttleTimer?.isActive ?? false) return;

    // 立即渲染第一帧
    _flushPending();

    // 启动节流定时器
    _throttleTimer = Timer(_throttleInterval, () {
      if (_hasPendingUpdate && mounted) {
        _flushPending();
      }
    });
  }

  void _flushPending() {
    if (!_hasPendingUpdate) return;
    _hasPendingUpdate = false;
    final parsed = _parseText(_pendingText, widget.isStreaming);
    if (parsed != _renderedText) {
      setState(() {
        _renderedText = parsed;
      });
    }
  }

  String _parseText(String text, bool isStreaming) {
    if (text.isEmpty || text == '...') return text;
    return _parser.parse(text, isStreaming: isStreaming);
  }

  @override
  void dispose() {
    _throttleTimer?.cancel();
    _cursorController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          MarkdownBody(
            // 使用文本内容的哈希长度作为 key，避免不必要的全量重建
            // 仅在渲染文本实际变化时才触发 rebuild
            key: ValueKey<int>(_renderedText.hashCode),
            data: _renderedText,
            selectable: widget.selectable,
            styleSheet: widget.styleSheet,
            onTapLink: widget.onTapLink,
            fitContent: true,
            softLineBreak: true,
          ),
          if (widget.isStreaming) _buildStreamingIndicator(),
        ],
      ),
    );
  }

  Widget _buildStreamingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: AnimatedBuilder(
        animation: _cursorOpacity,
        builder: (context, child) {
          return Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 8,
                height: 16,
                decoration: BoxDecoration(
                  color: (widget.styleSheet?.p?.color ?? Theme.of(context).textTheme.bodyMedium?.color ?? Colors.black)
                      .withValues(alpha: _cursorOpacity.value * 0.6),
                  borderRadius: BorderRadius.circular(1),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
