/// Streaming Markdown Parser - 有限状态机解析器
///
/// 解决 LLM 流式输出 Markdown 渲染的核心问题：
/// 1. 未闭合的行内格式（粗体、斜体、行内代码、删除线）
/// 2. 未闭合的代码块
/// 3. 不完整的表格结构
/// 4. 不完整的链接/图片语法
/// 5. 块级元素间缺少空行
library;

/// 解析器状态枚举
enum _BlockState {
  normal,
  fencedCode,
  table,
}

/// 行内格式标记
class _InlineMarker {
  final String marker;
  final int position;

  const _InlineMarker(this.marker, this.position);
}

/// 流式 Markdown 解析器
///
/// 使用有限状态机追踪块级和行内两层 Markdown 结构，
/// 在任意截断点生成可安全渲染的 Markdown 文本。
class StreamingMarkdownParser {
  // ------------------------------------------------------------------ 公共 API

  /// 将流式接收到的不完整 Markdown 文本转换为可安全渲染的版本。
  ///
  /// [raw]        当前累积的完整文本
  /// [isStreaming] 是否仍在接收数据
  /// [cursor]      可选的光标字符串，将根据语法状态注入到合适位置
  String parse(String raw, {bool isStreaming = true, String? cursor}) {
    if (raw.isEmpty) return raw + (cursor ?? '');

    // Step 0: 基础清理
    var text = _cleanInvisible(raw);
    
    // 如果有光标，先临时注入到末尾，后面修复逻辑会处理它
    if (cursor != null && isStreaming) {
      text = '$text$cursor';
    }

    // Step 1: 块级状态机 — 修复代码块、表格
    text = _fixBlocks(text, isStreaming: isStreaming);

    // Step 2: 块级隔离 — 确保块级元素前有空行
    text = _ensureBlockGaps(text);

    // Step 3: 行内修复 — 对最后一段修复未闭合的行内标记
    if (isStreaming) {
      text = _fixInlineMarkers(text);
      text = _fixPartialSyntax(text);
    }

    return text;
  }

  // ------------------------------------------------------------ Step 0: 清理

  /// 移除零宽字符，保留正常空白
  String _cleanInvisible(String text) {
    return text.replaceAll(RegExp(r'[\u200B-\u200D\uFEFF]'), '');
  }

  // ------------------------------------------------- Step 1: 块级空行隔离

  static final _blockPrefixRe = RegExp(
    r'^(\s*)(#{1,6}\s'       // 标题
    r'|[-*+]\s'              // 无序列表
    r'|\d+\.\s'              // 有序列表
    r'|>\s'                  // 引用
    r'|```'                  // 代码块
    r'|\|'                   // 表格
    r'|---+\s*$'             // 分隔线
    r')',
    multiLine: true,
  );

  String _ensureBlockGaps(String text) {
    final lines = text.split('\n');
    if (lines.length <= 1) return text;

    final result = <String>[lines[0]];
    for (var i = 1; i < lines.length; i++) {
      final prev = lines[i - 1];
      final curr = lines[i];
      // 如果当前行是块级起始，且上一行非空且上一行不是同类块
      if (_blockPrefixRe.hasMatch(curr) &&
          prev.trim().isNotEmpty &&
          !prev.trim().startsWith('```') &&
          result.last.trim().isNotEmpty) {
        // 检查是否已经有空行
        if (result.isNotEmpty && result.last.trim().isNotEmpty) {
          // 不要在连续列表项/表格行之间添加空行
          if (!_isContinuousBlock(prev, curr)) {
            result.add('');
          }
        }
      }
      result.add(curr);
    }
    return result.join('\n');
  }

  /// 判断两行是否属于连续的同类块（如连续列表项、连续表格行）
  bool _isContinuousBlock(String prev, String curr) {
    final p = prev.trimLeft();
    final c = curr.trimLeft();

    // 连续无序列表
    if (RegExp(r'^[-*+]\s').hasMatch(p) && RegExp(r'^[-*+]\s').hasMatch(c)) {
      return true;
    }
    // 连续有序列表
    if (RegExp(r'^\d+\.\s').hasMatch(p) && RegExp(r'^\d+\.\s').hasMatch(c)) {
      return true;
    }
    // 连续表格行
    if (p.startsWith('|') && c.startsWith('|')) return true;
    // 连续引用
    if (p.startsWith('>') && c.startsWith('>')) return true;
    return false;
  }

  // -------------------------------------------------- Step 2: 块级状态机

  String _fixBlocks(String text, {required bool isStreaming}) {
    final lines = text.split('\n');
    final output = <String>[];

    var state = _BlockState.normal;
    String codeFence = '';      // 记录開启代码块的栅栏标记 (``` 或 ~~~)
    int tableColumns = 0;
    bool hasTableSeparator = false;
    int tableHeaderIndex = -1;

    for (var i = 0; i < lines.length; i++) {
      final line = lines[i];
      final trimmed = line.trim();

      switch (state) {
        case _BlockState.normal:
          if (_isCodeFenceOpen(trimmed)) {
            state = _BlockState.fencedCode;
            codeFence = trimmed.startsWith('~~~') ? '~~~' : '```';
            output.add(line);
          } else if (_isTableRow(trimmed)) {
            bool isReallyTable = false;
            if (trimmed.startsWith('|') || trimmed.endsWith('|')) {
              isReallyTable = true;
            } else if (i + 1 < lines.length) {
              if (_isTableSeparator(lines[i + 1].trim())) {
                isReallyTable = true;
              }
            }

            if (isReallyTable) {
              state = _BlockState.table;
              tableColumns = _countTableColumns(trimmed);
              hasTableSeparator = false;
              tableHeaderIndex = output.length;
              output.add(_normalizeTableRow(trimmed, tableColumns));
            } else {
              output.add(line);
            }
          } else {
            output.add(line);
          }
          break;

        case _BlockState.fencedCode:
          if (_isCodeFenceClose(trimmed, codeFence)) {
            state = _BlockState.normal;
          }
          output.add(line);
          break;

        case _BlockState.table:
          if (_isTableSeparator(trimmed)) {
            hasTableSeparator = true;
            output.add(_normalizeTableSeparator(tableColumns));
          } else if (_isTableRow(trimmed)) {
            // 如果还没有分隔线，而这是第二行非分隔表格行，插入分隔线
            if (!hasTableSeparator && output.length > tableHeaderIndex) {
              output.add(_normalizeTableSeparator(tableColumns));
              hasTableSeparator = true;
            }
            output.add(_normalizeTableRow(trimmed, tableColumns));
          } else {
            // 表格结束
            if (!hasTableSeparator && tableHeaderIndex >= 0) {
              // 只有一行表格头，补一个分隔行
              output.insert(
                tableHeaderIndex + 1,
                _normalizeTableSeparator(tableColumns),
              );
            }
            state = _BlockState.normal;
            tableColumns = 0;
            output.add(line);
          }
          break;
      }
    }

    // 流式模式下闭合未完成的块
    if (isStreaming) {
      if (state == _BlockState.fencedCode) {
        output.add(codeFence);
      }
      if (state == _BlockState.table) {
        if (!hasTableSeparator && tableHeaderIndex >= 0) {
          output.insert(
            tableHeaderIndex + 1,
            _normalizeTableSeparator(tableColumns),
          );
        }
        // 确保最后一行表格行闭合
        if (output.isNotEmpty) {
          final lastLine = output.last.trim();
          if (lastLine.contains('|') && !lastLine.endsWith('|')) {
            output[output.length - 1] = '${output.last}|';
          }
        }
      }
    }

    return output.join('\n');
  }

  bool _isCodeFenceOpen(String trimmed) {
    return RegExp(r'^(`{3,}|~{3,})').hasMatch(trimmed) &&
        !RegExp(r'^(`{3,}|~{3,})\s*$').hasMatch(trimmed) ||
        RegExp(r'^(`{3,}|~{3,})\s*$').hasMatch(trimmed);
  }

  bool _isCodeFenceClose(String trimmed, String fence) {
    if (fence == '```') return RegExp(r'^`{3,}\s*$').hasMatch(trimmed);
    if (fence == '~~~') return RegExp(r'^~{3,}\s*$').hasMatch(trimmed);
    return false;
  }

  bool _isTableRow(String trimmed) {
    return trimmed.contains('|') && !trimmed.startsWith('```');
  }

  bool _isTableSeparator(String trimmed) {
    return RegExp(r'^\|?[\s:]*-{1,}[\s:]*(\|[\s:]*-{1,}[\s:]*)*\|?\s*$')
        .hasMatch(trimmed);
  }

  int _countTableColumns(String row) {
    var r = row.trim();
    if (!r.startsWith('|')) r = '|$r';
    if (!r.endsWith('|')) r = '$r|';
    final cells = r.split('|').length - 2;
    return cells < 1 ? 1 : cells;
  }

  String _normalizeTableRow(String row, int expectedColumns) {
    var r = row.trim();
    if (!r.startsWith('|')) r = '|$r';
    if (!r.endsWith('|')) r = '$r|';
    // 补齐缺少的列
    final currentCols = r.split('|').length - 2;
    if (currentCols < expectedColumns) {
      for (var i = currentCols; i < expectedColumns; i++) {
        r = '$r   |';
      }
    }
    return r;
  }

  String _normalizeTableSeparator(int columns) {
    final cells = List.generate(columns, (_) => '---');
    return '| ${cells.join(' | ')} |';
  }

  // ------------------------------------------------- Step 3: 行内修复

  /// 已知的行内标记对（按长度递减排列以贪婪匹配）
  static const _inlineMarkers = ['***', '**', '*', '~~', '`'];

  /// 在文本末尾添加缺失的闭合标记
  String _fixInlineMarkers(String text) {
    final lines = text.split('\n');
    if (lines.isEmpty) return text;

    // 只处理最后一个段落（从最后一个空行之后开始）
    int lastBlankIndex = -1;
    for (var i = lines.length - 1; i >= 0; i--) {
      if (lines[i].trim().isEmpty) {
        lastBlankIndex = i;
        break;
      }
    }

    final startIndex = lastBlankIndex + 1;
    if (startIndex >= lines.length) return text;

    // 拼接最后一段
    final lastParagraph = lines.sublist(startIndex).join('\n');
    final fixed = _closeInlineMarkers(lastParagraph);

    if (fixed == lastParagraph) return text;

    final prefix = lines.sublist(0, startIndex).join('\n');
    return prefix.isEmpty ? fixed : '$prefix\n$fixed';
  }

  /// 对给定文本，追踪行内标记的开/闭状态，在尾部补全未闭合的标记
  String _closeInlineMarkers(String text) {
    final opened = <_InlineMarker>[];
    var i = 0;

    // 跳过代码块标记行
    if (text.trimLeft().startsWith('```')) return text;

    while (i < text.length) {
      // 跳过转义
      if (text[i] == '\\' && i + 1 < text.length) {
        i += 2;
        continue;
      }

      // 检查行内代码（特殊处理：` 内部不解析其他标记）
      if (text[i] == '`') {
        if (opened.isNotEmpty && opened.last.marker == '`') {
          opened.removeLast();
          i++;
          continue;
        }
        opened.add(_InlineMarker('`', i));
        i++;
        continue;
      }

      // 如果在行内代码中，跳过其他标记
      if (opened.isNotEmpty && opened.last.marker == '`') {
        i++;
        continue;
      }

      // 检查多字符标记
      bool matched = false;
      for (final marker in _inlineMarkers) {
        if (marker == '`') continue; // 已处理
        if (i + marker.length <= text.length &&
            text.substring(i, i + marker.length) == marker) {
          if (opened.isNotEmpty && opened.last.marker == marker) {
            opened.removeLast();
          } else {
            opened.add(_InlineMarker(marker, i));
          }
          i += marker.length;
          matched = true;
          break;
        }
      }
      if (!matched) i++;
    }

    // 反向闭合所有打开的标记
    if (opened.isEmpty) return text;

    final suffix = StringBuffer();
    for (var j = opened.length - 1; j >= 0; j--) {
      suffix.write(opened[j].marker);
    }
    return '$text${suffix.toString()}';
  }

  /// 修复部分完成的链接/图片语法
  String _fixPartialSyntax(String text) {
    // 处理不完整的链接 [text]( 或 [text](url
    // 只检查最后 200 个字符以提高性能
    final checkLen = text.length < 200 ? text.length : 200;
    final tail = text.substring(text.length - checkLen);

    // 不完整的图片/链接: ![alt](url 或 [text](url  — 缺少右括号
    final openBracket = RegExp(r'\[([^\]]*)\]\(([^)]*?)$');
    if (openBracket.hasMatch(tail)) {
      return '$text)';
    }

    // 只有 [ 开头但没有 ]
    final onlyOpen = RegExp(r'\[([^\]]*)$');
    if (onlyOpen.hasMatch(tail)) {
      // 检查是否前面有 ! (图片)
      final match = onlyOpen.firstMatch(tail)!;
      final content = match.group(1) ?? '';
      // 如果内容很短且在行尾，可能是正在输入的链接 — 闭合它
      if (content.length < 100) {
        return '$text]';
      }
    }

    return text;
  }
}
