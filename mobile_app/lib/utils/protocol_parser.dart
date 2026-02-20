import 'dart:convert';
import '../models/message_segment.dart';

/// 协议解析器
/// 
/// 负责将包含自定义协议 `<component type="...">...</component>` 的字符串
/// 拆分为 [MessageSegment] 列表，支持流式解析。
class ProtocolParser {
  static const String _startTag = '<component';
  static const String _endTag = '</component>';

  /// 将包含组件协议的文本拆分为多个段落
  static List<MessageSegment> parse(String text, {bool isOverallStreaming = false}) {
    if (text.isEmpty) return [];

    final List<MessageSegment> segments = [];
    int lastIndex = 0;
    
    // 查找第一个组件开始标签
    int startIdx = text.indexOf(_startTag, lastIndex);
    
    while (startIdx != -1) {
      // 在标签之前的文本作为 Markdown 段
      if (startIdx > lastIndex) {
        segments.add(MessageSegment(
          type: SegmentType.markdown,
          text: text.substring(lastIndex, startIdx),
        ));
      }

      // 查找组件类型
      // <component type="meal_plan">
      final typeMatch = RegExp(r'type="([^"]*)"').firstMatch(text.substring(startIdx));
      final componentType = typeMatch?.group(1) ?? 'unknown';
      
      // 查找标签结尾 >
      final closeBracketIdx = text.indexOf('>', startIdx);
      if (closeBracketIdx == -1) {
        // 组件标签本身都没写完
        segments.add(MessageSegment(
          type: SegmentType.markdown,
          text: text.substring(startIdx),
        ));
        lastIndex = text.length;
        break;
      }

      // 查找组件结束标签
      int endIdx = text.indexOf(_endTag, closeBracketIdx + 1);
      
      if (endIdx == -1) {
        // 组件内容还在流式生成中
        final content = text.substring(closeBracketIdx + 1);
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
        final content = text.substring(closeBracketIdx + 1, endIdx);
        segments.add(MessageSegment(
          type: SegmentType.component,
          text: content,
          componentType: componentType,
          data: _tryParseJson(content),
          isStreaming: false,
        ));
        lastIndex = endIdx + _endTag.length;
      }

      // 继续查找下一个组件
      startIdx = text.indexOf(_startTag, lastIndex);
    }

    // 剩余文本作为最后一个 Markdown 段
    if (lastIndex < text.length) {
      segments.add(MessageSegment(
        type: SegmentType.markdown,
        text: text.substring(lastIndex),
      ));
    }

    return segments;
  }

  static Map<String, dynamic>? _tryParseJson(String content) {
    if (content.isEmpty) return null;
    try {
      // 清除可能的前导/后导空白
      String clean = content.trim();
      
      // 处理 LLM 可能会在标签内又包裹一层 Markdown 代码块的情况
      if (clean.startsWith('```json')) {
        clean = clean.replaceFirst('```json', '');
        if (clean.endsWith('```')) {
          clean = clean.substring(0, clean.length - 3);
        }
      } else if (clean.startsWith('```')) {
        clean = clean.replaceFirst('```', '');
        if (clean.endsWith('```')) {
          clean = clean.substring(0, clean.length - 3);
        }
      }
      
      clean = clean.trim();
      if (!clean.startsWith('{')) return null;
      
      // 如果 JSON 不完整，简单地尝试闭合它（仅用于流式显示占位数据，不建议生产环境依赖）
      String jsonStr = clean;
      if (!clean.endsWith('}')) {
        // 统计括号，简单尝试闭合
        int openBraces = 0;
        int closeBraces = 0;
        for (int i = 0; i < clean.length; i++) {
          if (clean[i] == '{') openBraces++;
          if (clean[i] == '}') closeBraces++;
        }
        if (openBraces > closeBraces) {
          jsonStr = clean + ('}' * (openBraces - closeBraces));
        }
      }
      
      return jsonDecode(jsonStr) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }
}
