import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../utils/bmr_calculator.dart';
import '../widgets/glass_card.dart';
import '../providers/user_provider.dart';

class XiaoSongScreen extends StatefulWidget {
  const XiaoSongScreen({super.key});

  @override
  State<XiaoSongScreen> createState() => _XiaoSongScreenState();
}

class _XiaoSongScreenState extends State<XiaoSongScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  final ImagePicker _picker = ImagePicker();

  bool _isIngredientMode = false;
  final List<String> _selectedIngredients = [];

  @override
  void initState() {
    super.initState();
    _addSystemMessage('''你好！我是你的减重助手小松。你可以通过以下方式与我互动：

1. 🥗 **发食材**：输入食材列表（如：鸡蛋, 西红柿），我为你开食谱。
2. 📸 **拍食物**：点击相机图标拍照，我帮你估算卡路里。
3. 💬 **问建议**：直接提问关于减重的问题。
4. ⚖️ **算TDEE**：我会根据你的个人资料自动计算建议摄入量。''');
  }

  void _toggleIngredientMode() {
    setState(() {
      _isIngredientMode = !_isIngredientMode;
      if (_isIngredientMode) {
        _selectedIngredients.clear();
        // 如果输入框有内容，可以尝试自动拆分并加入
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

  void _addSystemMessage(String text) {
    if (_messages.isNotEmpty && !_messages.last.isUser && _messages.last.isStreaming) {
      // 如果上一条是正在流式输出的消息，则追加内容（虽然这里addSystemMessage是整块的）
       setState(() {
         _messages.last = ChatMessage(text: '${_messages.last.text}\n\n$text', isUser: false);
       });
    } else {
      setState(() {
        _messages.add(ChatMessage(text: text, isUser: false));
      });
    }
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

  Future<void> _handleSend({String? textOverride}) async {
    final text = textOverride ?? _controller.text.trim();
    if (text.isEmpty) return;

    if (textOverride == null) {
      _controller.clear();
    }
    _addUserMessage(text);
    
    // 立即显示“思考中”状态
    setState(() {
      _messages.add(ChatMessage(text: '...', isUser: false, isStreaming: true));
    });
    _scrollToBottom();

    try {
      final apiService = context.read<ApiService>();
      
      // 移除武断的前端分流，统一交给流式聊天处理。
      // 后端的 LoseWeightAgent 会自动识别意图（是查热量、聊天还是生成食谱）。
      await _streamChat(apiService, text, _messages.length - 1);
      
    } catch (e) {
      setState(() {
        _messages.last = ChatMessage(text: '抱歉，出错了: $e', isUser: false, isStreaming: false);
      });
    }
  }

  Future<void> _streamChat(ApiService apiService, String message, int messageIndex) async {
    // 清空占位内容准备流式输入
    setState(() {
      _messages[messageIndex] = ChatMessage(text: '', isUser: false, isStreaming: true);
    });

    try {
      final stream = apiService.chatWithCoachStream(message);
      await for (final event in stream) {
        if (!mounted) break;

        if (event.type == 'text') {
          setState(() {
            final currentMsg = _messages[messageIndex];
            _messages[messageIndex] = ChatMessage(
              text: currentMsg.text + (event.text ?? ''),
              isUser: false,
              isStreaming: true,
            );
          });
          _scrollToBottom();
        } else if (event.type == 'action_result') {
          _handleActionResult(event.data);
        } else if (event.type == 'done') {
           setState(() {
             _messages[messageIndex] = ChatMessage(
               text: _messages[messageIndex].text, 
               isUser: false, 
               isStreaming: false
             );
           });
           break; // 明确退出循环
        }
      }
    } catch (e) {
      if (mounted) {
         setState(() {
            _messages[messageIndex] = ChatMessage(
              text: '${_messages[messageIndex].text}\n\n[连接中断: $e]',
              isUser: false,
              isStreaming: false,
            );
         });
      }
    } finally {
      // 确保万一没有 done 事件，最后也能关闭状态
      if (mounted && _messages[messageIndex].isStreaming) {
         setState(() {
           _messages[messageIndex] = ChatMessage(
             text: _messages[messageIndex].text,
             isUser: false,
             isStreaming: false
           );
         });
      }
    }
  }

  void _handleActionResult(Map<String, dynamic>? result) {
    if (result == null) return;
    
    final success = result['success'] == true;
    final message = result['message'] as String? ?? (success ? '操作成功' : '操作失败');
    
    // 在UI上展示 Toast 或 Snack bar，或者追加到消息中
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: success ? Colors.green : Colors.red,
        behavior: SnackBarBehavior.floating,
        margin: EdgeInsets.only(bottom: 80, left: 16, right: 16),
      ),
    );

    // 如果是特定的动作，可以有额外的 UI 响应，例如刷新页面（如果需要）
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
    final XFile? image = await _picker.pickImage(
      source: source,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 85,
    );
    if (!mounted || image == null) return;

    _addSystemMessage('📷 正在分析食物图片...');

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
    }
  }

  void _showWeightInputDialog() {
     showDialog(
       context: context,
       builder: (context) {
         final controller = TextEditingController();
         return AlertDialog(
           title: const Text('记录体重'),
           content: TextField(
             controller: controller,
             keyboardType: TextInputType.number,
             decoration: const InputDecoration(labelText: '体重 (kg)', suffixText: 'kg'),
             autofocus: true,
           ),
           actions: [
             TextButton(onPressed: () => Navigator.pop(context), child: const Text('取消')),
             TextButton(
               onPressed: () {
                 final weight = controller.text.trim();
                 if (weight.isNotEmpty) {
                   Navigator.pop(context);
                   _handleSend(textOverride: '记录体重 $weight kg');
                 }
               },
               child: const Text('记录'),
             ),
           ],
         );
       },
     );
  }

  void _showFoodQueryDialog() {
     showDialog(
       context: context,
       builder: (context) {
         final controller = TextEditingController();
         return AlertDialog(
           title: const Text('询问热量'),
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
               child: const Text('询问'),
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
          _buildInputArea(),
        ],
      ),
    );
  }

  void _showTdeeCalculator() {
    setState(() {
      _messages.add(ChatMessage(text: 'TDEE 计算器', isUser: false, isTdeeCard: true));
    });
    _scrollToBottom();
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
          // 快捷功能区 - 改为单排水平滚动
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            child: Row(
              children: [
                _buildQuickAction('⚖️ 算TDEE', _showTdeeCalculator),
                const SizedBox(width: 8),
                _buildQuickAction(
                  _isIngredientMode ? '✨ 退出模式' : '🥗 报食材', 
                  _toggleIngredientMode
                ),
                const SizedBox(width: 8),
                _buildQuickAction('记录体重', () => _showWeightInputDialog()),
                const SizedBox(width: 8),
                _buildQuickAction('询问热量', () => _showFoodQueryDialog()),
              ],
            ),
          ),
          const SizedBox(height: 12),
          
          // 食材输入卡片
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
                        const Text('🥗 待报食材', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
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
                              color: AppColors.primary, // 明确使用主色调文字
                              fontWeight: FontWeight.w500
                            )
                          ),
                          onDeleted: () => _removeIngredient(e.key),
                          deleteIcon: const Icon(
                            Icons.close, 
                            size: 14, 
                            color: AppColors.primary // 明确图标颜色
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

          // 输入行 - 拍照按钮在左，发送在右
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
    if (msg.isTdeeCard) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: InteractiveTdeeCard(
          onCalculated: () {
            _addSystemMessage('太棒了！你的 TDEE 已更新。这将帮助我更精准地为你规划每日饮食。你想现在就开始规划今天的食谱吗？');
          },
        ),
      );
    }

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
        child: Column(
           crossAxisAlignment: CrossAxisAlignment.start,
           children: [
             MarkdownBody(
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
              ),
            ),
            if (msg.isStreaming)
               const Padding(
                 padding: EdgeInsets.only(top: 8.0),
                 child: SizedBox(width: 12, height: 12, child: CircularProgressIndicator(strokeWidth: 2)),
               )
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

class ChatMessage {
  final String text;
  final bool isUser;
  final bool isStreaming;
  final bool isTdeeCard;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.isStreaming = false,
    this.isTdeeCard = false,
  });
}

class InteractiveTdeeCard extends StatefulWidget {
  final VoidCallback onCalculated;
  const InteractiveTdeeCard({super.key, required this.onCalculated});

  @override
  State<InteractiveTdeeCard> createState() => _InteractiveTdeeCardState();
}

class _InteractiveTdeeCardState extends State<InteractiveTdeeCard> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _ageController = TextEditingController();
  final TextEditingController _heightController = TextEditingController();
  final TextEditingController _weightController = TextEditingController();
  
  String _gender = 'male';
  String _activityLevel = 'moderate';
  bool _isSaved = false;

  final Map<String, String> _activityOptions = {
    'sedentary': '久坐 (办公室)',
    'light': '轻度 (1-3次/周)',
    'moderate': '中度 (3-5次/周)',
    'active': '活跃 (6-7次/周)',
    'very_active': '极高强度',
  };

  @override
  void initState() {
    super.initState();
    final user = context.read<UserProvider>().user;
    if (user != null) {
      _ageController.text = user.age.toString();
      _heightController.text = user.heightCm.toStringAsFixed(1);
      _weightController.text = user.initialWeightKg.toStringAsFixed(1);
      _gender = user.gender;
    } else {
      _ageController.text = '25';
      _heightController.text = '175.0';
      _weightController.text = '70.0';
    }
  }

  @override
  void dispose() {
    _ageController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    super.dispose();
  }

  void _save() async {
    if (!_formKey.currentState!.validate()) return;

    final double weight = double.parse(_weightController.text);
    final double height = double.parse(_heightController.text);
    final int age = int.parse(_ageController.text);

    final bmr = BmrCalculator.calculateBmr(
      weight: weight,
      height: height,
      age: age,
      gender: _gender,
    );
    
    final activityMultipliers = {
      'sedentary': 1.2,
      'light': 1.375,
      'moderate': 1.55,
      'active': 1.725,
      'very_active': 1.9,
    };
    
    final tdee = bmr * activityMultipliers[_activityLevel]!;
    final userProvider = context.read<UserProvider>();
    
    if (userProvider.hasUser) {
      final updatedUser = userProvider.user!.copyWith(
        bmr: bmr,
        dailyCalorieGoal: tdee,
        gender: _gender,
        age: age,
        heightCm: height,
      );
      
      try {
        await userProvider.updateUser(updatedUser);
        setState(() => _isSaved = true);
        widget.onCalculated();
      } catch (e) {
         // Error handled by provider
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isSaved) {
      return const GlassCard(
        color: AppColors.success,
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.white),
            SizedBox(width: 12),
            Text('TDEE 设置成功！', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ],
        ),
      );
    }

    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.calculate, color: AppColors.primary, size: 20),
                SizedBox(width: 8),
                Text('TDEE 快速计算器', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              ],
            ),
            const Divider(height: 24),
            _buildRow('性别', _buildGenderToggle()),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildInputField(
                    label: '年龄',
                    controller: _ageController,
                    suffix: '岁',
                    validator: (v) {
                      final val = int.tryParse(v ?? '');
                      if (val == null || val < 10 || val > 100) return '10-100';
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildInputField(
                    label: '身高',
                    controller: _heightController,
                    suffix: 'cm',
                    validator: (v) {
                      final val = double.tryParse(v ?? '');
                      if (val == null || val < 100 || val > 250) return '100-250';
                      return null;
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInputField(
              label: '当前体重',
              controller: _weightController,
              suffix: 'kg',
              validator: (v) {
                final val = double.tryParse(v ?? '');
                if (val == null || val < 30 || val > 300) return '30-300';
                return null;
              },
            ),
            const SizedBox(height: 16),
            const Text('活动强度', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
            const SizedBox(height: 8),
            _buildActivityDropdown(),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _save,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 0,
                ),
                child: const Text('同步至个人资料并计算', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputField({
    required String label,
    required TextEditingController controller,
    required String suffix,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          validator: validator,
          decoration: InputDecoration(
            isDense: true,
            suffixText: suffix,
            filled: true,
            fillColor: AppColors.border.withValues(alpha: 0.1),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            errorStyle: const TextStyle(fontSize: 10),
          ),
        ),
      ],
    );
  }

  Widget _buildRow(String label, Widget child) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 14)),
        child,
      ],
    );
  }

  Widget _buildGenderToggle() {
    return Row(
      children: [
        _genderButton('男', 'male'),
        const SizedBox(width: 8),
        _genderButton('女', 'female'),
      ],
    );
  }

  Widget _genderButton(String label, String value) {
    bool isSelected = _gender == value;
    return GestureDetector(
      onTap: () => setState(() => _gender = value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary.withValues(alpha: 0.1) : Colors.transparent,
          border: Border.all(color: isSelected ? AppColors.primary : AppColors.border),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(label, style: TextStyle(color: isSelected ? AppColors.primary : AppColors.textSecondary, fontSize: 12)),
      ),
    );
  }

  Widget _buildActivityDropdown() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: AppColors.border.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _activityLevel,
          isExpanded: true,
          items: _activityOptions.entries.map((e) {
            return DropdownMenuItem(value: e.key, child: Text(e.value, style: const TextStyle(fontSize: 13)));
          }).toList(),
          onChanged: (v) => setState(() => _activityLevel = v!),
        ),
      ),
    );
  }
}
