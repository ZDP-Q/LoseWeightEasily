import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../providers/meal_plan_provider.dart';
import '../providers/user_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class MealPlanScreen extends StatefulWidget {
  const MealPlanScreen({super.key});

  @override
  State<MealPlanScreen> createState() => _MealPlanScreenState();
}

class _MealPlanScreenState extends State<MealPlanScreen> {
  final TextEditingController _ingredientController = TextEditingController();
  final TextEditingController _preferencesController = TextEditingController();
  final TextEditingController _restrictionsController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // 恢复之前的输入状态（如果有）
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<MealPlanProvider>();
      _preferencesController.text = provider.preferences;
      _restrictionsController.text = provider.restrictions;
    });
  }

  @override
  void dispose() {
    _ingredientController.dispose();
    _preferencesController.dispose();
    _restrictionsController.dispose();
    super.dispose();
  }

  void _generate() async {
    final provider = context.read<MealPlanProvider>();
    final userProvider = context.read<UserProvider>();
    
    // 更新 provider 中的输入状态
    provider.updateInputs(
      preferences: _preferencesController.text.trim(),
      restrictions: _restrictionsController.text.trim(),
    );

    // 调用生成
    await provider.generatePlan(calorieGoal: userProvider.dailyCalorieGoal);
    
    if (!mounted) return;
    if (provider.error != null) {
       ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text('生成失败: ${provider.error}'), backgroundColor: AppColors.danger),
      );
    }
  }

  void _addIngredient() {
    if (_ingredientController.text.trim().isNotEmpty) {
      context.read<MealPlanProvider>().addIngredient(_ingredientController.text.trim());
      _ingredientController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Consumer<MealPlanProvider>(
            builder: (context, provider, child) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'AI 智能食谱',
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          fontSize: 28,
                        ),
                  ),
                  const SizedBox(height: 8),
                  const Text('输入您现有的食材，AI 为您定制减肥餐',
                      style: TextStyle(color: AppColors.textSecondary)),
                  const SizedBox(height: 28),

                  // 食材输入
                  _buildSectionTitle('食材'),
                  const SizedBox(height: 12),
                  _buildIngredientInput(),
                  const SizedBox(height: 12),
                  _buildIngredientChips(provider),

                  // 偏好和限制
                  const SizedBox(height: 24),
                  _buildSectionTitle('偏好（可选）'),
                  const SizedBox(height: 8),
                  _buildTextInput(
                    _preferencesController,
                    '如：高蛋白、低碳水、清淡口味',
                  ),
                  const SizedBox(height: 16),
                  _buildSectionTitle('饮食限制（可选）'),
                  const SizedBox(height: 8),
                  _buildTextInput(
                    _restrictionsController,
                    '如：不吃辣、素食、无麸质',
                  ),

                  // 用户画像提示
                  _buildCalorieHint(),

                  const SizedBox(height: 28),
                  ElevatedButton(
                    onPressed:
                        provider.isLoading || provider.ingredients.isEmpty ? null : _generate,
                    child: provider.isLoading
                        ? Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                      color: Colors.white, strokeWidth: 2)),
                              const SizedBox(width: 12),
                              Text(
                                'AI 正在为您定制食谱...',
                                style: TextStyle(
                                    color: Colors.white.withValues(alpha: 0.8)),
                              ),
                            ],
                          )
                        : const Text('生成食谱计划'),
                  ),
                  const SizedBox(height: 32),
                  if (provider.hasPlan) _buildMealPlanView(provider),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 15,
          color: AppColors.textPrimary),
    );
  }

  Widget _buildIngredientInput() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _ingredientController,
            decoration: InputDecoration(
              hintText: '输入食材（如：鸡胸肉、西兰花）',
              filled: true,
              fillColor: AppColors.bgCard.withValues(alpha: 0.4),
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                  borderSide: BorderSide.none),
            ),
            onSubmitted: (_) => _addIngredient(),
          ),
        ),
        const SizedBox(width: 12),
        IconButton.filled(
          onPressed: _addIngredient,
          icon: const Icon(Icons.add),
          style: IconButton.styleFrom(backgroundColor: AppColors.primary),
        ),
      ],
    );
  }

  Widget _buildTextInput(TextEditingController controller, String hint) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(
        hintText: hint,
        filled: true,
        fillColor: AppColors.bgCard.withValues(alpha: 0.4),
        border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide.none),
      ),
    );
  }

  Widget _buildIngredientChips(MealPlanProvider provider) {
    if (provider.ingredients.isEmpty) return const SizedBox.shrink();
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: provider.ingredients
          .map((ing) => Chip(
                label: Text(ing),
                onDeleted: () =>
                    provider.removeIngredient(ing),
                backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                side: BorderSide.none,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
              ))
          .toList(),
    ).animate().fadeIn();
  }

  Widget _buildCalorieHint() {
    final userProvider = context.watch<UserProvider>();
    final goal = userProvider.dailyCalorieGoal;
    if (goal == null) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Row(
        children: [
          Icon(Icons.info_outline,
              size: 16, color: AppColors.textSecondary.withValues(alpha: 0.7)),
          const SizedBox(width: 8),
          Text(
            '将基于您的每日目标 ${goal.toStringAsFixed(0)} kcal 生成',
            style: const TextStyle(
                fontSize: 12, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildMealPlanView(MealPlanProvider provider) {
    final planContent = provider.mealPlan!['plan'] as String? ?? '无法生成食谱，请稍后再试';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('您的专属食谱',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        GlassCard(
          padding: const EdgeInsets.all(20),
          child: MarkdownBody(
            data: planContent,
            styleSheet: MarkdownStyleSheet(
              p: const TextStyle(
                  color: AppColors.textPrimary, fontSize: 14, height: 1.6),
              h1: const TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 22,
                  fontWeight: FontWeight.bold),
              h2: const TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold),
              h3: const TextStyle(
                  color: AppColors.primary,
                  fontSize: 16,
                  fontWeight: FontWeight.bold),
              strong: const TextStyle(
                  color: AppColors.secondary, fontWeight: FontWeight.bold),
              listBullet: const TextStyle(color: AppColors.textSecondary),
              blockquoteDecoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.05),
                border: Border(
                  left: BorderSide(
                      color: AppColors.primary.withValues(alpha: 0.5),
                      width: 3),
                ),
              ),
            ),
          ),
        ),
      ],
    ).animate().fadeIn().slideY(begin: 0.2, end: 0);
  }
}
