import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/chat_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';
import '../widgets/streaming_markdown.dart';

class XiaoSongScreen extends StatefulWidget {
  const XiaoSongScreen({super.key});

  @override
  State<XiaoSongScreen> createState() => _XiaoSongScreenState();
}

class _XiaoSongScreenState extends State<XiaoSongScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ImagePicker _picker = ImagePicker();

  bool _isIngredientMode = false;
  final List<String> _selectedIngredients = [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final chatProvider = context.read<ChatProvider>();
      if (chatProvider.messages.isEmpty) {
        chatProvider.loadHistory().then((_) {
          if (chatProvider.messages.isEmpty) {
            chatProvider.addSystemMessage('''你好！我是你的减重助手小松。你可以通过以下方式与我互动：

1. 🥗 **添加食材**：输入食材列表（如：鸡蛋, 西红柿），我为你开食谱。
2. 📸 **拍食物**：点击相机图标拍照，我帮你估算卡路里。
3. 💬 **问建议**：直接提问关于减重的问题。''');
          }
          _scrollToBottom(isInitial: true);
        });
      } else {
        _scrollToBottom(isInitial: true);
      }
    });
  }

  void _toggleIngredientMode() {
    setState(() {
      _isIngredientMode = !_isIngredientMode;
      if (_isIngredientMode) {
        _selectedIngredients.clear();
        if (_controller.text.isNotEmpty) {
          final items = _controller.text.split(RegExp(r'[,，\s]+'));
          _selectedIngredients.addAll(items.where((i) => i.isNotEmpty));
          _controller.clear();
        }
      }
    });
  }

  void _addIngredient(String name) {
    if (name.trim().isEmpty) return;
    setState(() {
      _selectedIngredients.add(name.trim());
    });
    _controller.clear();
  }

  void _removeIngredient(int index) {
    setState(() {
      _selectedIngredients.removeAt(index);
    });
  }

  void _submitIngredients() {
    if (_selectedIngredients.isEmpty) {
      if (_controller.text.trim().isNotEmpty) {
        _addIngredient(_controller.text);
      } else {
        return;
      }
    }
    
    final text = _selectedIngredients.join(', ');
    _handleSend(textOverride: text);
    setState(() {
      _isIngredientMode = false;
      _selectedIngredients.clear();
    });
  }

  void _scrollToBottom({bool isInitial = false}) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        if (isInitial) {
          _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
          // 再次确认高度，防止首帧加载未完成
          Future.delayed(const Duration(milliseconds: 50), () {
            if (_scrollController.hasClients) {
              _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
            }
          });
        } else {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      }
    });
  }

  Future<void> _handleSend({String? textOverride}) async {
    final text = textOverride ?? _controller.text.trim();
    if (text.isEmpty) return;

    if (textOverride == null) {
      _controller.clear();
    }
    
    final chatProvider = context.read<ChatProvider>();
    chatProvider.addUserMessage(text);
    _scrollToBottom();
    
    chatProvider.addSystemMessage('...');
    chatProvider.setStreaming(chatProvider.messages.length - 1, true);
    _scrollToBottom();

    try {
      final apiService = context.read<ApiService>();
      await _streamChat(apiService, chatProvider, text, chatProvider.messages.length - 1);
    } catch (e) {
      chatProvider.updateLastMessage('抱歉，出错了: $e', isStreaming: false);
    }
  }

  Future<void> _streamChat(ApiService apiService, ChatProvider chatProvider, String message, int messageIndex) async {
    chatProvider.updateLastMessage('', isStreaming: true);

    try {
      final stream = apiService.chatWithCoachStream(message);
      await for (final event in stream) {
        if (!mounted) break;

        if (event.type == 'text') {
          chatProvider.appendToLastMessage(event.text ?? '', isStreaming: true);
          _scrollToBottom();
        } else if (event.type == 'action_result') {
          _handleActionResult(event.data);
        } else if (event.type == 'done') {
           chatProvider.setStreaming(messageIndex, false);
           break;
        }
      }
    } catch (e) {
      if (mounted) {
         chatProvider.appendToLastMessage('\n\n[连接中断: $e]', isStreaming: false);
      }
    } finally {
      if (mounted) {
         chatProvider.setStreaming(messageIndex, false);
      }
    }
  }

  void _handleActionResult(Map<String, dynamic>? result) {
    if (result == null) return;
    
    final success = result['success'] == true;
    final message = result['message'] as String? ?? (success ? '操作成功' : '操作失败');
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: success ? Colors.green : Colors.red,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.only(bottom: 80, left: 16, right: 16),
      ),
    );
  }

  Future<void> _pickImage(ImageSource source) async {
    final XFile? image = await _picker.pickImage(
      source: source,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 85,
    );
    if (!mounted || image == null) return;

    final chatProvider = context.read<ChatProvider>();
    chatProvider.addSystemMessage('📷 正在分析食物图片...');
    _scrollToBottom();

    try {
      final apiService = context.read<ApiService>();
      final bytes = await File(image.path).readAsBytes();
      final result = await apiService.recognizeFood(bytes);
      
      if (!mounted) return;
      
      final confidence = (result['raw_data'][0]['confidence'] as num) * 100;
      
      chatProvider.addSystemMessage('''✅ 识别结果：
食物：${result['final_food_name']}
预估热量：${result['final_estimated_calories']} kcal
置信度：${confidence.toStringAsFixed(1)}%''');
      _scrollToBottom();
    } catch (e) {
      chatProvider.addSystemMessage('图片识别失败: $e');
    }
  }

  void _showFoodQueryDialog() {
     showDialog(
       context: context,
       builder: (context) {
         final controller = TextEditingController();
         return AlertDialog(
           title: const Text('热量查询'),
           content: TextField(
             controller: controller,
             decoration: const InputDecoration(labelText: '食物名称', hintText: '如：一个苹果'),
             autofocus: true,
           ),
           actions: [
             TextButton(onPressed: () => Navigator.pop(context), child: const Text('取消')),
             TextButton(
               onPressed: () {
                 final food = controller.text.trim();
                 if (food.isNotEmpty) {
                   Navigator.pop(context);
                   _handleSend(textOverride: '$food 的热量是多少？');
                 }
               },
               child: const Text('查询'),
             ),
           ],
         );
       },
     );
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
            child: Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                if (chatProvider.isLoading && chatProvider.messages.isEmpty) {
                   return const Center(child: CircularProgressIndicator());
                }
                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: chatProvider.messages.length,
                  itemBuilder: (context, index) {
                    final msg = chatProvider.messages[index];
                    return _buildMessageBubble(msg);
                  },
                );
              },
            ),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        border: Border(top: BorderSide(color: AppColors.border.withValues(alpha: 0.2))),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            child: Row(
              children: [
                _buildQuickAction(
                  _isIngredientMode ? '✨ 退出模式' : '🥗 添加食材', 
                  _toggleIngredientMode
                ),
                const SizedBox(width: 8),
                _buildQuickAction('热量查询', () => _showFoodQueryDialog()),
              ],
            ),
          ),
          const SizedBox(height: 12),
          
          if (_isIngredientMode)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: GlassCard(
                color: AppColors.primary.withValues(alpha: 0.05),
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('🥗 已选食材', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
                        if (_selectedIngredients.isNotEmpty)
                          TextButton(
                            onPressed: _submitIngredients,
                            child: const Text('生成食谱', style: TextStyle(fontWeight: FontWeight.bold)),
                          ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (_selectedIngredients.isEmpty)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        child: Text('在下方输入框添加食材，点击右侧按钮加入列表', 
                          style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                      )
                    else
                      Wrap(
                        spacing: 8,
                        runSpacing: 4,
                        children: _selectedIngredients.asMap().entries.map((e) => Chip(
                          label: Text(
                            e.value, 
                            style: const TextStyle(
                              fontSize: 12, 
                              color: AppColors.primary,
                              fontWeight: FontWeight.w500
                            )
                          ),
                          onDeleted: () => _removeIngredient(e.key),
                          deleteIcon: const Icon(
                            Icons.close, 
                            size: 14, 
                            color: AppColors.primary
                          ),
                          backgroundColor: Colors.white,
                          elevation: 0,
                          side: BorderSide(color: AppColors.primary.withValues(alpha: 0.2)),
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
                          labelPadding: const EdgeInsets.symmetric(horizontal: 4),
                        )).toList(),
                      ),
                  ],
                ),
              ),
            ),

          Row(
            children: [
              _buildIconButton(
                icon: FontAwesomeIcons.camera,
                onTap: () => _pickImage(ImageSource.camera),
                color: AppColors.primary,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _controller,
                  decoration: InputDecoration(
                    hintText: _isIngredientMode ? '输入食材名称...' : '输入食材或提问...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(28),
                      borderSide: BorderSide.none,
                    ),
                    fillColor: AppColors.border.withValues(alpha: 0.1),
                    filled: true,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  ),
                  onSubmitted: (_) => _isIngredientMode ? _addIngredient(_controller.text) : _handleSend(),
                ),
              ),
              const SizedBox(width: 12),
              _buildIconButton(
                icon: _isIngredientMode ? Icons.add : Icons.send,
                onTap: () => _isIngredientMode ? _addIngredient(_controller.text) : _handleSend(),
                color: AppColors.primary,
                isFilled: true,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildIconButton({required IconData icon, required VoidCallback onTap, required Color color, bool isFilled = false}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: isFilled ? color : color.withValues(alpha: 0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(
          icon,
          color: isFilled ? Colors.white : color,
          size: 20,
        ),
      ),
    );
  }



  Widget _buildMessageBubble(ChatMessage msg) {
    final isUser = msg.isUser;
    
    return Align(
      key: ValueKey('msg_${msg.id}'),
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.88),
        decoration: BoxDecoration(
          color: isUser ? AppColors.primary : Theme.of(context).cardColor,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(20),
            topRight: const Radius.circular(20),
            bottomLeft: Radius.circular(isUser ? 20 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 20),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: StreamingMarkdownWidget(
                key: ValueKey('md_${msg.id}'),
                text: msg.text,
                isStreaming: !isUser && msg.isStreaming,
                selectable: true,
                styleSheet: MarkdownStyleSheet(
                  p: TextStyle(
                    color: isUser ? Colors.white : AppColors.textPrimary,
                    fontSize: 15.5,
                    height: 1.6,
                  ),
                  strong: TextStyle(
                    color: isUser ? Colors.white : AppColors.primary,
                    fontWeight: FontWeight.bold,
                  ),
                  h1: TextStyle(color: isUser ? Colors.white : AppColors.primary, fontSize: 19, fontWeight: FontWeight.bold),
                  h2: TextStyle(color: isUser ? Colors.white : AppColors.primary, fontSize: 17, fontWeight: FontWeight.bold),
                  h3: TextStyle(color: isUser ? Colors.white : AppColors.primary, fontSize: 16, fontWeight: FontWeight.bold),
                  listBullet: TextStyle(color: isUser ? Colors.white : AppColors.primary, fontSize: 15),
                  listIndent: 22,
                  blockquoteDecoration: BoxDecoration(
                    color: isUser ? Colors.white12 : AppColors.primary.withValues(alpha: 0.05),
                    border: Border(left: BorderSide(color: isUser ? Colors.white38 : AppColors.primary, width: 4)),
                  ),
                  code: TextStyle(
                    backgroundColor: isUser ? Colors.black12 : AppColors.primary.withValues(alpha: 0.08),
                    color: isUser ? Colors.white : AppColors.primary,
                    fontFamily: 'monospace',
                    fontSize: 13.5,
                  ),
                  codeblockDecoration: BoxDecoration(
                    color: isUser ? Colors.black26 : Colors.grey.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  tableBorder: TableBorder.all(
                    color: isUser ? Colors.white30 : AppColors.border.withValues(alpha: 0.3),
                    width: 1,
                  ),
                  tableBody: TextStyle(color: isUser ? Colors.white : AppColors.textPrimary, fontSize: 13),
                  tableHead: TextStyle(color: isUser ? Colors.white : AppColors.textPrimary, fontWeight: FontWeight.bold),
                  tableCellsPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickAction(String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: AppColors.primary.withValues(alpha: 0.05),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.primary.withValues(alpha: 0.1)),
        ),
        child: Text(
          label,
          style: const TextStyle(fontSize: 13, color: AppColors.primary, fontWeight: FontWeight.w500),
        ),
      ),
    );
  }
}
