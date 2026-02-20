import 'dart:convert';
import '../models/message_segment.dart';

/// 协议解析器 (Ark Protocol)
/// 
/// 识别 Markdown 代码块形式的协议： ```json:type ... ```
class ProtocolParser {
  static const String _codeStart = '```json:';
  static const String _codeEnd = '```';

  static List<MessageSegment> parse(String text, {bool isOverallStreaming = false}) {
    if (text.isEmpty) return [];

    final List<MessageSegment> segments = [];
    int lastIndex = 0;
    
    // 查找组件开始： ```json:
    int startIdx = text.indexOf(_codeStart, lastIndex);
    
    while (startIdx != -1) {
      // 1. 提取之前的 Markdown 段
      if (startIdx > lastIndex) {
        segments.add(MessageSegment(
          type: SegmentType.markdown,
          text: text.substring(lastIndex, startIdx),
        ));
      }

      // 2. 解析类型： ```json:type
      final typeEndIdx = text.indexOf('\n', startIdx);
      if (typeEndIdx == -1) {
        // 还没换行，说明类型还没写完
        segments.add(MessageSegment(
          type: SegmentType.markdown,
          text: text.substring(startIdx),
        ));
        lastIndex = text.length;
        break;
      }

      final componentType = text.substring(startIdx + _codeStart.length, typeEndIdx).trim();
      
      // 3. 查找结束标志
      int endIdx = text.indexOf(_codeEnd, typeEndIdx + 1);
      
      if (endIdx == -1) {
        // 内容正在流式传输
        final content = text.substring(typeEndIdx + 1);
        segments.add(MessageSegment(
          type: SegmentType.component,
          text: content,
          componentType: componentType,
          data: _tryParseJson(content),
          isStreaming: isOverallStreaming,
        ));
        lastIndex = text.length;
        break;
      } else {
        // 完整的组件
        final content = text.substring(typeEndIdx + 1, endIdx);
        segments.add(MessageSegment(
          type: SegmentType.component,
          text: content,
          componentType: componentType,
          data: _tryParseJson(content),
          isStreaming: false,
        ));
        lastIndex = endIdx + _codeEnd.length;
      }

      startIdx = text.indexOf(_codeStart, lastIndex);
    }

    if (lastIndex < text.length) {
      segments.add(MessageSegment(
        type: SegmentType.markdown,
        text: text.substring(lastIndex),
      ));
    }

    return segments;
  }

  static Map<String, dynamic>? _tryParseJson(String content) {
    String clean = content.trim();
    if (clean.isEmpty || !clean.startsWith('{')) return null;
    
    try {
      // 简单的自动补齐括号逻辑
      String jsonStr = clean;
      int openBraces = 0;
      int closeBraces = 0;
      for (int i = 0; i < clean.length; i++) {
        if (clean[i] == '{') openBraces++;
        if (clean[i] == '}') closeBraces++;
      }
      if (openBraces > closeBraces) {
        jsonStr = clean + ('}' * (openBraces - closeBraces));
      }
      
      return jsonDecode(jsonStr) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }
}
