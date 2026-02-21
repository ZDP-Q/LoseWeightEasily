import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../utils/streaming_renderer/ast.dart';

/// 渲染岛 (V4 - 彻底消除 ANR 版)
/// 
/// 核心：
/// 1. MarkdownBody 仅在内容真正变化时才被创建。
/// 2. 光标分离 (Cursor Separation)：闪烁光标不再导致 Markdown 重新解析。
class RenderIsland extends StatefulWidget {
  final SBlockNode node;
  final bool isStreaming;
  final Animation<double>? cursorAnimation; 
  final bool selectable;
  final MarkdownStyleSheet? styleSheet;
  final MarkdownTapLinkCallback? onTapLink;

  const RenderIsland({
    super.key,
    required this.node,
    this.isStreaming = false,
    this.cursorAnimation,
    this.selectable = true,
    this.styleSheet,
    this.onTapLink,
  });

  @override
  State<RenderIsland> createState() => _RenderIslandState();
}

class _RenderIslandState extends State<RenderIsland> {
  Widget? _cachedMarkdownBody;
  String? _lastMarkdown;

  @override
  void didUpdateWidget(covariant RenderIsland oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // 如果节点内容没有变化，不要重新创建 MarkdownBody
    final currentMarkdown = widget.node.cachedMarkdown;
    if (currentMarkdown != _lastMarkdown) {
      _lastMarkdown = currentMarkdown;
      _cachedMarkdownBody = _buildMarkdownBody(currentMarkdown);
    }
  }

  @override
  Widget build(BuildContext context) {
    final body = _cachedMarkdownBody ??= _buildMarkdownBody(widget.node.cachedMarkdown);

    if (widget.node.status == NodeStatus.closed || !widget.isStreaming) {
      return body;
    }

    // 对于流式输出块，采用 Wrap 或 Stack 处理光标，避免触发 Markdown 解析
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        body,
        // 光标是一个独立的 Widget，它的闪烁不会触发 body 的重新 build
        _CursorWidget(animation: widget.cursorAnimation),
      ],
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

class _CursorWidget extends StatelessWidget {
  final Animation<double>? animation;
  const _CursorWidget({this.animation});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: animation ?? kAlwaysCompleteAnimation,
      builder: (context, _) {
        final opacity = (animation?.value ?? 0) > 0.5 ? 1.0 : 0.0;
        return Opacity(
          opacity: opacity,
          child: const Padding(
            padding: EdgeInsets.only(top: 4.0),
            child: Text("▊", style: TextStyle(fontSize: 14, color: Colors.blueAccent)),
          ),
        );
      },
    );
  }
}
