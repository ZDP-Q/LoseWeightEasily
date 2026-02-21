/// 词法分析 Token 类型
enum TokenType {
  text,      // 普通文本
  newline,   // \n
  star,      // *
  backtick,  // `
  dash,      // -
  gt,        // > (引用)
  hash,      // # (标题)
  pipe,      // | (表格)
  bracket,   // [ ] (链接)
  paren,     // ( )
  exclaim,   // !
  plus,      // +
  dot,       // .
  space,     // 空格
  tilde,     // ~ (删除线 / 代码块)
}

/// 解析产生的 Token
class Token {
  final TokenType type;
  final String content;

  Token(this.type, this.content);

  @override
  String toString() => 'Token(${type.name}, "$content")';
}

/// 状态保留的 Lexer
class StreamingLexer {
  // 维护待处理的文本（如果 chunk 刚好切断了多字符标记）
  String _buffer = '';

  /// 输入一段新的内容，返回新增的 Token 列表
  List<Token> push(String chunk) {
    _buffer += chunk;
    final tokens = <Token>[];
    int pos = 0;

    while (pos < _buffer.length) {
      final char = _buffer[pos];
      
      TokenType type;
      switch (char) {
        case '\n': type = TokenType.newline; break;
        case '*':  type = TokenType.star; break;
        case '`':  type = TokenType.backtick; break;
        case '-':  type = TokenType.dash; break;
        case '>':  type = TokenType.gt; break;
        case '#':  type = TokenType.hash; break;
        case '|':  type = TokenType.pipe; break;
        case '[':  
        case ']':  type = TokenType.bracket; break;
        case '(':
        case ')':  type = TokenType.paren; break;
        case '!':  type = TokenType.exclaim; break;
        case '+':  type = TokenType.plus; break;
        case '.':  type = TokenType.dot; break;
        case ' ':  type = TokenType.space; break;
        case '~':  type = TokenType.tilde; break;
        default:   type = TokenType.text; break;
      }

      if (type == TokenType.text) {
        // 合并连续文本
        final start = pos;
        while (pos < _buffer.length && _isPlainTextChar(_buffer[pos])) {
          pos++;
        }
        tokens.add(Token(TokenType.text, _buffer.substring(start, pos)));
      } else {
        tokens.add(Token(type, char));
        pos++;
      }
    }

    _buffer = ''; 
    return tokens;
  }

  bool _isPlainTextChar(String char) {
    const specials = '\n*`-<>#|[]()!+.~ ';
    return !specials.contains(char);
  }
}
