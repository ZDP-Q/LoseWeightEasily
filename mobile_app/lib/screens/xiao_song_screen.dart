import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';

class XiaoSongScreen extends StatefulWidget {
  const XiaoSongScreen({super.key});

  @override
  State<XiaoSongScreen> createState() => _XiaoSongScreenState();
}

class _XiaoSongScreenState extends State<XiaoSongScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _addSystemMessage('''你好！我是你的减重助手小松。你可以通过以下方式与我互动：

1. 🥗 **发食材**：输入食材列表（如：鸡蛋, 西红柿），我为你开食谱。
2. 📸 **拍食物**：点击相机图标拍照，我帮你估算卡路里。
3. 💬 **问建议**：直接提问关于减重的问题。
4. ⚖️ **算TDEE**：我会根据你的个人资料自动计算建议摄入量。''');
  }

  void _addSystemMessage(String text) {
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: false));
    });
    _scrollToBottom();
  }

  void _addUserMessage(String text) {
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _handleSend() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    _controller.clear();
    _addUserMessage(text);
    
    setState(() => _isLoading = true);

    try {
      final apiService = context.read<ApiService>();
      
      if (text.contains(',') || text.contains('，') || (text.length < 10 && (text.contains('菜') || text.contains('肉')))) {
        final plan = await apiService.generateMealPlan(ingredients: text.split(RegExp(r'[,，\s]+')));
        _addSystemMessage(_formatMealPlan(plan));
      } else {
        final reply = await apiService.chatWithCoach(text);
        _addSystemMessage(reply);
      }
    } catch (e) {
      _addSystemMessage('抱歉，出错了: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  String _formatMealPlan(Map<String, dynamic> plan) {
    final summary = plan['daily_summary'];
    final meals = plan['meals'] as Map<String, dynamic>;
    final tips = List<String>.from(plan['tips'] ?? []);

    StringBuffer sb = StringBuffer();
    sb.writeln('📋 **今日定制食谱**');
    sb.writeln('🎯 目标热量: ${summary['target_calories']} kcal');
    sb.writeln('---\n');
    
    meals.forEach((key, value) {
      String mealName = key == 'breakfast' ? '早餐' : key == 'lunch' ? '午餐' : '晚餐';
      sb.writeln('**$mealName**: ${value['name']} (${value['calories']} kcal)');
      sb.writeln('🍳 做法: ${value['instructions']}\n');
    });

    if (tips.isNotEmpty) {
      sb.writeln('💡 **小贴士**:');
      for (var tip in tips) {
        sb.writeln('- $tip');
      }
    }
    return sb.toString();
  }

  Future<void> _pickImage(ImageSource source) async {
    final XFile? image = await _picker.pickImage(source: source);
    if (!mounted || image == null) return;

    _addSystemMessage('📷 正在分析食物图片...');
    setState(() => _isLoading = true);

    try {
      final apiService = context.read<ApiService>();
      final bytes = await File(image.path).readAsBytes();
      final result = await apiService.recognizeFood(bytes);
      
      if (!mounted) return;
      
      final confidence = (result['raw_data'][0]['confidence'] as num) * 100;
      
      _addSystemMessage('''✅ 识别结果：
食物：${result['final_food_name']}
预估热量：${result['final_estimated_calories']} kcal
置信度：${confidence.toStringAsFixed(1)}%''');
    } catch (e) {
      _addSystemMessage('图片识别失败: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            CircleAvatar(
              backgroundColor: AppColors.primary,
              child: Icon(FontAwesomeIcons.tree, size: 18, color: Colors.white),
            ),
            SizedBox(width: 12),
            Text('小松 AI 助手'),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return _buildMessageBubble(msg);
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8.0),
              child: LinearProgressIndicator(minHeight: 2),
            ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage msg) {
    return Align(
      alignment: msg.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: msg.isUser 
              ? AppColors.primary 
              : Theme.of(context).cardColor,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(msg.isUser ? 16 : 0),
            bottomRight: Radius.circular(msg.isUser ? 0 : 16),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 5,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: MarkdownBody(
          data: msg.text,
          styleSheet: MarkdownStyleSheet(
            p: TextStyle(
              color: msg.isUser ? Colors.white : null,
              fontSize: 15,
              height: 1.5,
            ),
            strong: TextStyle(
              color: msg.isUser ? Colors.white : AppColors.primary,
              fontWeight: FontWeight.bold,
            ),
            h1: TextStyle(color: msg.isUser ? Colors.white : AppColors.primary),
            h2: TextStyle(color: msg.isUser ? Colors.white : AppColors.primary),
            h3: TextStyle(color: msg.isUser ? Colors.white : AppColors.primary),
            listBullet: TextStyle(color: msg.isUser ? Colors.white : AppColors.primary),
            code: TextStyle(
              backgroundColor: msg.isUser ? Colors.white12 : Colors.grey.withValues(alpha: 0.1),
              fontFamily: 'monospace',
              fontSize: 14,
            ),
            codeblockDecoration: BoxDecoration(
              color: msg.isUser ? Colors.white10 : Colors.grey.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(8),
            ),
            blockquoteDecoration: BoxDecoration(
              color: msg.isUser ? Colors.white12 : AppColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            blockquotePadding: const EdgeInsets.all(8),
            horizontalRuleDecoration: BoxDecoration(
              border: Border(
                top: BorderSide(
                  width: 1,
                  color: msg.isUser ? Colors.white24 : AppColors.border.withValues(alpha: 0.3),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        border: Border(top: BorderSide(color: AppColors.border.withValues(alpha: 0.2))),
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(FontAwesomeIcons.camera, size: 20, color: AppColors.textSecondary),
            onPressed: () => _pickImage(ImageSource.camera),
          ),
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: '输入食材或提问...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                fillColor: AppColors.border.withValues(alpha: 0.1),
                filled: true,
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              ),
              onSubmitted: (_) => _handleSend(),
            ),
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: AppColors.primary,
            child: IconButton(
              icon: const Icon(Icons.send, color: Colors.white, size: 20),
              onPressed: _handleSend,
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  ChatMessage({required this.text, required this.isUser});
}
