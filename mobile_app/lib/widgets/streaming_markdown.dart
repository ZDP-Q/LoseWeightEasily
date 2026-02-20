import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../utils/streaming_markdown_parser.dart';
import '../utils/protocol_parser.dart';
import '../models/message_segment.dart';
import '../widgets/protocol_component.dart';

/// 修正后的 Ark Protocol 渲染器
/// 
/// 核心改进：
/// 1. **Key 稳定性**：使用 segment 索引作为 Key，不再使用文本 hashCode。
/// 2. **语法隔离**：将代码块与 Markdown 渲染完全隔离，互不干扰。
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

  static const _throttleInterval = Duration(milliseconds: 16); // 提升到 60fps

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
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _cursorOpacity,
        builder: (context, _) {
          final String cursor = widget.isStreaming 
              ? (_cursorOpacity.value > 0.5 ? "▊" : "") 
              : "";
          
          final segments = ProtocolParser.parse(_pendingText, isOverallStreaming: widget.isStreaming);

          return Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: segments.asMap().entries.map((entry) {
              final index = entry.key;
              final segment = entry.value;
              final isLast = index == segments.length - 1;

              if (segment.type == SegmentType.component) {
                // 关键点：使用基于 index 的固定 Key，防止闪烁
                return ProtocolComponent(
                  key: ValueKey('comp_$index'),
                  type: segment.componentType ?? 'unknown',
                  data: segment.data,
                  isStreaming: segment.isStreaming,
                );
              } else {
                final displayText = isLast
                    ? _markdownParser.parse(segment.text, isStreaming: widget.isStreaming, cursor: cursor)
                    : _markdownParser.parse(segment.text, isStreaming: false);

                if (displayText.trim().isEmpty && !isLast) return const SizedBox.shrink();

                return MarkdownBody(
                  key: ValueKey('md_$index'), // 固定 Key，不再使用 hashCode
                  data: displayText,
                  selectable: widget.selectable,
                  styleSheet: widget.styleSheet,
                  onTapLink: widget.onTapLink,
                  fitContent: true,
                  softLineBreak: true,
                );
              }
            }).toList(),
          );
        },
      ),
    );
  }
}
