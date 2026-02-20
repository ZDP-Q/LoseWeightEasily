import 'package:markdown/markdown.dart' as md;

/// 方舟协议语法拦截器 (兼容 Markdown 7.x)
/// 
/// 识别 ```json:type ... ``` 并在 AST 中生成 ark_component 节点
class ArkProtocolSyntax extends md.BlockSyntax {
  @override
  RegExp get pattern => RegExp(r'^```json:(\w+)');

  const ArkProtocolSyntax();

  @override
  md.Node? parse(md.BlockParser parser) {
    final match = pattern.firstMatch(parser.current.content)!;
    final type = match.group(1)!;
    final childLines = <String>[];
    
    parser.advance();
    
    // 收集代码块内容，直到遇到 ```
    while (!parser.isDone) {
      if (parser.current.content.startsWith('```')) {
        parser.advance();
        break;
      }
      childLines.add(parser.current.content);
      parser.advance();
    }

    // 创建一个自定义节点
    return md.Element('ark_component', [
      md.Text(childLines.join('\n'))
    ])..attributes['type'] = type;
  }
}
