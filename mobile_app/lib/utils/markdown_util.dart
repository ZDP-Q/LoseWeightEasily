/// Markdown 结构化纠偏与流式补全工具类
class MarkdownUtil {
  // 基础正则：识别 <think> 标签
  static final thinkRegExp = RegExp(r'<think>[\s\S]*?(?:</think>|$)', caseSensitive: false, multiLine: true);
  static final thinkCloseRegExp = RegExp(r'</think>', caseSensitive: false);
  
  // 符号统一：中点/各种圆点转标准列表符，保持缩进
  static final listDotRegExp = RegExp(r'^([ \t]*)[·•◦▪▫]\s*', multiLine: true);

  // 1. 语法修正：确保符号和文字之间有空格（兼容 0-3 个空格的缩进）
  // 修正标题：#Title -> # Title
  static final headerSpaceRegExp = RegExp(r'^([ \t]*)(#+)([^\s#\n])', multiLine: true);
  // 修正列表：-Item -> - Item 或 1.Item -> 1. Item (使用前瞻防止误伤 -1 或 1.2)
  static final listSpaceRegExp = RegExp(r'^([ \t]*)([-*+]|\d+\.)(?=[^\s\-\*\+\.\d])', multiLine: true);

  // 2. 结构纠偏：确保块之间有空行，但避开列表项之间（关键：解决无序列表渲染断裂）
  // 逻辑：匹配 [非列表且非表格且非空行的行] + \n + [列表行]
  static final headerGapRegExp = RegExp(r'([^|\n])\n( *)(#+ )', multiLine: true); 
  static final listGapRegExp = RegExp(r'^((?!(?: *[-*+]| *\d+\.| *\|)).+)\n( *)((?:[-*+]|\d+\.)\s+)', multiLine: true); 
  static final hrGapRegExp = RegExp(r'([^|\n])\n( *)([-*_]{3,})\s*$', multiLine: true);

  /// 核心格式化逻辑
  static String format(String raw, {bool isStreaming = false}) {
    if (raw.isEmpty) return raw;

    // A. 过滤思考过程
    String text = raw.replaceAll(thinkRegExp, '');
    text = text.replaceAll(thinkCloseRegExp, '');

    // B. 符号预处理
    text = text.replaceAllMapped(listDotRegExp, (m) => '${m.group(1)}- ');

    // C. 语法补全 (补空格)
    text = text.replaceAllMapped(headerSpaceRegExp, (m) => '${m.group(1)}${m.group(2)} ${m.group(3)}');
    text = text.replaceAllMapped(listSpaceRegExp, (m) => '${m.group(1)}${m.group(2)} ');

    // D. 结构补全 (补空行)
    text = text.replaceAllMapped(headerGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');
    text = text.replaceAllMapped(listGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');
    text = text.replaceAllMapped(hrGapRegExp, (m) => '${m.group(1)}\n\n${m.group(2)}${m.group(3)}');

    // E. 流式补全
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
