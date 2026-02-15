import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class MealPlanScreen extends StatefulWidget {
  const MealPlanScreen({super.key});

  @override
  State<MealPlanScreen> createState() => _MealPlanScreenState();
}

class _MealPlanScreenState extends State<MealPlanScreen> {
  final _ingredientsController = TextEditingController();
  final _prefsController = TextEditingController();
  String? _plan;
  bool _isLoading = false;

  void _generate() async {
    final ingredients = _ingredientsController.text.split(RegExp(r'[,，\s]+')).where((s) => s.isNotEmpty).toList();
    if (ingredients.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('请至少输入一种食材')));
      return;
    }

    setState(() {
      _isLoading = true;
      _plan = null;
    });

    try {
      final api = context.read<ApiService>();
      final result = await api.generateMealPlan(
        ingredients: ingredients,
        preferences: _prefsController.text,
      );
      if (!mounted) return;
      setState(() => _plan = result['plan']);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('生成失败: $e'), backgroundColor: AppColors.danger));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),
              Text(
                'AI 食谱规划',
                style: Theme.of(context).textTheme.displaySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  fontSize: 28,
                ),
              ),
              const SizedBox(height: 8),
              Text('让 AI 为您定制今日健康饮食', style: TextStyle(color: AppColors.textSecondary)),
              const SizedBox(height: 32),
              _buildInputSection(),
              const SizedBox(height: 32),
              if (_isLoading) _buildLoadingState(),
              if (_plan != null) _buildPlanDisplay(),
              const SizedBox(height: 100),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputSection() {
    return Column(
      children: [
        GlassCard(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('现有食材', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              TextField(
                controller: _ingredientsController,
                maxLines: 2,
                decoration: const InputDecoration(
                  hintText: '输入食材，用逗号或空格分隔...',
                  prefixIcon: Icon(FontAwesomeIcons.basketShopping, size: 18),
                ),
              ),
              const SizedBox(height: 20),
              const Text('个人偏好 (可选)', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              TextField(
                controller: _prefsController,
                decoration: const InputDecoration(
                  hintText: '例如: 低碳水, 15分钟搞定, 辣味...',
                  prefixIcon: Icon(FontAwesomeIcons.heartPulse, size: 18),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _generate,
          icon: const Icon(FontAwesomeIcons.wandMagicSparkles, size: 18),
          label: const Text('生成我的减重食谱'),
        ),
      ],
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        children: [
          const SizedBox(height: 40),
          const CircularProgressIndicator(color: AppColors.primary),
          const SizedBox(height: 24),
          Text(
            '大厨正在为您设计食谱...',
            style: TextStyle(color: AppColors.textSecondary, fontStyle: FontStyle.italic),
          ),
        ],
      ),
    ).animate().fadeIn();
  }

  Widget _buildPlanDisplay() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('为您推荐的计划', style: Theme.of(context).textTheme.titleLarge),
            IconButton(
              icon: const Icon(Icons.share_outlined, size: 20),
              onPressed: () {},
            ),
          ],
        ),
        const SizedBox(height: 16),
        GlassCard(
          padding: const EdgeInsets.all(24),
          color: AppColors.bgMain.withOpacity(0.8),
          child: MarkdownBody(
            data: _plan!,
            styleSheet: MarkdownStyleSheet(
              p: const TextStyle(color: AppColors.textPrimary, fontSize: 15, height: 1.5),
              h3: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 18, height: 2),
              listBullet: const TextStyle(color: AppColors.secondary),
            ),
          ),
        ),
      ],
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }
}
