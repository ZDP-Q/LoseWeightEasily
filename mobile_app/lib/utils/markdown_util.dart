/// Markdown 结构化纠偏与流式补全工具类
class MarkdownUtil {
  static final thinkRegExp = RegExp(r'<think>[\s\S]*?(?:</think>|$)', caseSensitive: false, multiLine: true);
  static final thinkCloseRegExp = RegExp(r'</think>', caseSensitive: false);
  static final listDotRegExp = RegExp(r'^([ \t]*)[·•◦▪▫]\s*', multiLine: true);
  static final malformedTableRowRegExp = RegExp(r'^([ \t]*)([-*+])([ \t]*\|)', multiLine: true);
  static final missingLeadingPipeRegExp = RegExp(r'^([ \t]*)(?![ \t]*[-*+|>#])([^|\n]+\|[^|\n]+\|[ \t]*$)', multiLine: true);

  // 块间距修正（保留用于最终纠偏）
  static final headerGapRegExp = RegExp(r'([^|\n])\n( *)(#+ )', multiLine: true); 
  static final tableGapRegExp = RegExp(r'^((?!(?: *\|| *[-*+]| *\d+\.)).+)\n( *)(\|)', multiLine: true);
  static final hrGapRegExp = RegExp(r'([^|\n])\n( *)([-*_]{3,})\s*$', multiLine: true);

  /// 核心格式化逻辑 (V4.0 状态机版)
  static String format(String raw, {bool isStreaming = false}) {
    if (raw.isEmpty) return raw;

    // A. 基础过滤
    String text = raw.replaceAll(thinkRegExp, '');
    text = text.replaceAll(thinkCloseRegExp, '');

    // B. 表格预修复
    text = text.replaceAllMapped(malformedTableRowRegExp, (m) => '${m.group(1)}| ${m.group(2)} ${m.group(3)}');
    text = text.replaceAllMapped(missingLeadingPipeRegExp, (m) => '${m.group(1)}| ${m.group(2)}');

    // C. 逐行处理 (核心纠偏逻辑)
    final lines = text.split('\n');
    final processedLines = <String>[];
    bool inSubList = false;

    for (int i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (line.trim().isEmpty) {
        processedLines.add(line);
        continue;
      }

      // 1. 列表符补空格与保护 ** (彻底解决 *下一步行动 变斜体问题)
      final listMatch = RegExp(r'^([ \t]*)([-*+]|\d+\.)').firstMatch(line);
      if (listMatch != null) {
        final indent = listMatch.group(1)!;
        final symbol = listMatch.group(2)!;
        final afterSymbolIndex = listMatch.end;
        
        if (afterSymbolIndex < line.length) {
          final nextChar = line[afterSymbolIndex];
          // 只有当符号后面不是空格，且不是相同的符号（如 **）时，才补空格
          if (nextChar != ' ' && nextChar != symbol[0]) {
            line = '$indent$symbol ${line.substring(afterSymbolIndex)}';
          }
        }
      }

      // 2. 清理分类标题末尾杂质 (彻底解决 下一步行动: * 顽疾)
      // 逻辑：如果这一行是列表项且包含冒号，则切除冒号后孤立的 * 或 _
      if (RegExp(r'^\s*(?:[-*+]|\d+\.)\s+').hasMatch(line) && line.contains(RegExp(r'[:：]'))) {
        line = line.replaceFirstMapped(RegExp(r'([:：][*_]*)\s+[*_]\s*$'), (m) => m.group(1)!);
      }

      // 3. 自动缩进逻辑 (实现视觉层级)
      final isCategory = RegExp(r'^\s*(?:[-*+]|\d+\.)\s+.*[:：]\s*$').hasMatch(line);
      final isListItem = RegExp(r'^\s*(?:[-*+]|\d+\.)\s+').hasMatch(line);

      if (isListItem) {
        if (inSubList && !isCategory) {
          // 对子项进行自动缩进（无论有序无序）
          line = '  ${line.trimLeft()}';
        }
        if (isCategory) inSubList = true; // 开启子列表模式
      } else {
        // 遇到非列表的非空文本，关闭子列表模式
        inSubList = false;
      }

      processedLines.add(line);
    }

    text = processedLines.join('\n');

    // D. 结构补全 (补空行)
    text = text.replaceAllMapped(headerGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');
    text = text.replaceAllMapped(tableGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');
    text = text.replaceAllMapped(hrGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');

    // E. 流式补全
    if (isStreaming) {
      text = _applyStreamingFixes(text);
    }

    return text.replaceAll('\r\n', '\n');
  }

  static String _applyStreamingFixes(String text) {
    final codeFenceCount = '```'.allMatches(text).length;
    if (codeFenceCount.isOdd) text = '$text\n```';
    
    int lastBracket = text.lastIndexOf('[');
    int lastCloseBracket = text.lastIndexOf(']');
    if (lastBracket > lastCloseBracket) text = '$text]';

    if (text.endsWith('\n') || text.endsWith(' ')) return '$text▊';
    return '$text ▊';
  }
}
