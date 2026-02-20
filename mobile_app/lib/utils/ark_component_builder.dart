import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:markdown/markdown.dart' as md;
import '../widgets/protocol_component.dart';

/// 方舟协议元素构造器
/// 
/// 将 AST 中的 ark_component 节点映射为 Flutter 原生 UI
class ArkComponentBuilder extends MarkdownElementBuilder {
  final bool isStreaming;

  ArkComponentBuilder({this.isStreaming = false});

  @override
  Widget? visitElementAfter(md.Element element, TextStyle? preferredStyle) {
    final String type = element.attributes['type'] ?? 'unknown';
    final String rawContent = element.textContent;
    
    // 尝试解析 JSON
    Map<String, dynamic>? data;
    try {
      String jsonStr = rawContent.trim();
      // 自动补全流式传输中的 JSON 括号
      int open = 0, close = 0;
      for (int i = 0; i < jsonStr.length; i++) {
        if (jsonStr[i] == '{') open++;
        if (jsonStr[i] == '}') close++;
      }
      if (open > close) jsonStr += '}' * (open - close);
      data = jsonDecode(jsonStr);
    } catch (_) {
      // 解析失败则由 ProtocolComponent 处理 (如显示 Loading)
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: ProtocolComponent(
        type: type,
        data: data,
        isStreaming: isStreaming,
      ),
    );
  }
}
