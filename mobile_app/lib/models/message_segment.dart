enum SegmentType {
  markdown,
  component,
}

class MessageSegment {
  final SegmentType type;
  final String text;
  final String? componentType;
  final Map<String, dynamic>? data;
  final bool isStreaming; // 用于标识该组件是否还在流式生成中

  const MessageSegment({
    required this.type,
    required this.text,
    this.componentType,
    this.data,
    this.isStreaming = false,
  });

  @override
  String toString() => 'MessageSegment(type: $type, text: ${text.substring(0, text.length > 20 ? 20 : text.length)}, component: $componentType)';
}
