/// Markdown 结构化纠偏与流式补全工具类
class MarkdownUtil {
  // 基础正则：识别 <think> 标签
  static final thinkRegExp = RegExp(r'<think>[\s\S]*?(?:</think>|$)', caseSensitive: false, multiLine: true);
  static final thinkCloseRegExp = RegExp(r'</think>', caseSensitive: false);
  
  // 符号统一：中点/各种圆点转标准列表符，保持缩进
  static final listDotRegExp = RegExp(r'^([ \t]*)[·•◦▪▫]\s*', multiLine: true);

  // 1. 语法修正：确保符号和文字之间有空格
  static final headerSpaceRegExp = RegExp(r'^([ \t]*)(#+)([^\s#\n])', multiLine: true);
  // 修正列表：-Item -> - Item (修复 -**标题** 无法识别的问题)
  static final listSpaceRegExp = RegExp(r'^([ \t]*)([-*+]|\d+\.)(?=[^\s\-\+\.\d|])', multiLine: true);

  // 2. 表格纠偏：修复 AI 常见的表格语法错误
  static final malformedTableRowRegExp = RegExp(r'^([ \t]*)([-*+])([ \t]*\|)', multiLine: true);
  static final missingLeadingPipeRegExp = RegExp(r'^([ \t]*)(?![ \t]*[-*+|>#])([^|\n]+\|[^|\n]+\|[ \t]*$)', multiLine: true);

  // 3. 结构纠偏：确保块之间有空行，并处理自动缩进层级
  static final headerGapRegExp = RegExp(r'([^|\n])\n( *)(#+ )', multiLine: true); 
  static final listGapRegExp = RegExp(r'^((?!(?: *[-*+]| *\d+\.| *\|)).+)\n( *)((?:[-*+]|\d+\.)\s+)', multiLine: true); 
  static final tableGapRegExp = RegExp(r'^((?!(?: *\|| *[-*+]| *\d+\.)).+)\n( *)(\|)', multiLine: true);
  static final hrGapRegExp = RegExp(r'([^|\n])\n( *)([-*_]{3,})\s*$', multiLine: true);

  // 层级纠偏：识别以冒号结尾的列表项作为“分类标题”，并缩进其后的普通子项
  static final listCategoryRegExp = RegExp(r'^(\s*[-*+]\s+.*[:：]\s*)\n((?:\s*[-*+]\s+(?!.*[:：]).*(?:\n|$))+)', multiLine: true);

  /// 核心格式化逻辑
  static String format(String raw, {bool isStreaming = false}) {
    if (raw.isEmpty) return raw;

    // A. 过滤思考过程
    String text = raw.replaceAll(thinkRegExp, '');
    text = text.replaceAll(thinkCloseRegExp, '');

    // B. 表格语法修复 (优先级最高，防止被识别为列表)
    text = text.replaceAllMapped(malformedTableRowRegExp, (m) => '${m.group(1)}| ${m.group(2)} ${m.group(3)}');
    text = text.replaceAllMapped(missingLeadingPipeRegExp, (m) => '${m.group(1)}| ${m.group(2)}');

    // C. 符号预处理与语法补全 (补空格)
    text = text.replaceAllMapped(listDotRegExp, (m) => '${m.group(1)}- ');
    text = text.replaceAllMapped(headerSpaceRegExp, (m) => '${m.group(1)}${m.group(2)} ${m.group(3)}');
    text = text.replaceAllMapped(listSpaceRegExp, (m) => '${m.group(1)}${m.group(2)} ');

    // D. 层级自动纠偏：实现“分类: \n  - 子项”的自动缩进视觉
    text = text.replaceAllMapped(listCategoryRegExp, (m) {
      final parent = m.group(1);
      final children = m.group(2)!.split('\n').map((line) {
        if (line.trim().isEmpty) return line;
        // 如果已经有缩进了就不再缩进，否则增加 2 个空格
        return line.startsWith('  ') ? line : '  $line';
      }).join('\n');
      return '$parent\n$children';
    });

    // E. 结构补全 (补空行)
    text = text.replaceAllMapped(headerGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');
    text = text.replaceAllMapped(listGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');
    text = text.replaceAllMapped(tableGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');
    text = text.replaceAllMapped(hrGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');

    // F. 流式补全
    if (isStreaming) {
      text = _applyStreamingFixes(text);
    }

    return text.replaceAll('\r\n', '\n');
  }

  static String _applyStreamingFixes(String text) {
    // 1. 闭合代码块
    final codeFenceCount = '```'.allMatches(text).length;
    if (codeFenceCount.isOdd) {
      text = '$text\n```';
    }

    // 2. 闭合链接
    int lastBracket = text.lastIndexOf('[');
    int lastCloseBracket = text.lastIndexOf(']');
    if (lastBracket > lastCloseBracket) {
      text = '$text]';
    }

    // 3. 光标处理
    if (text.endsWith('\n') || text.endsWith(' ')) {
      return '$text▊';
    }
    return '$text ▊';
  }
}
