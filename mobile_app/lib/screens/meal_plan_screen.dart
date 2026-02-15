import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class MealPlanScreen extends StatefulWidget {
  const MealPlanScreen({super.key});

  @override
  State<MealPlanScreen> createState() => _MealPlanScreenState();
}

class _MealPlanScreenState extends State<MealPlanScreen> {
  final List<String> _ingredients = [];
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;
  Map<String, dynamic>? _mealPlan;

  void _generate() async {
    if (_ingredients.isEmpty) return;
    setState(() => _isLoading = true);
    try {
      final api = context.read<ApiService>();
      final plan = await api.generateMealPlan(ingredients: _ingredients);
      if (!mounted) return;
      setState(() => _mealPlan = plan);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('生成失败: $e'), backgroundColor: AppColors.danger),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
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
              const SizedBox(height: 32),
              _buildIngredientInput(),
              const SizedBox(height: 24),
              _buildIngredientChips(),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isLoading || _ingredients.isEmpty ? null : _generate,
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('生成食谱计划'),
              ),
              const SizedBox(height: 32),
              if (_mealPlan != null) _buildMealPlanView(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIngredientInput() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _controller,
            decoration: InputDecoration(
              hintText: '输入食材（如：鸡胸肉、西兰花）',
              filled: true,
              fillColor: AppColors.bgCard.withValues(alpha: 0.4),
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15), borderSide: BorderSide.none),
            ),
            onSubmitted: (val) => _addIngredient(),
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

  void _addIngredient() {
    if (_controller.text.trim().isNotEmpty) {
      setState(() {
        _ingredients.add(_controller.text.trim());
        _controller.clear();
      });
    }
  }

  Widget _buildIngredientChips() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: _ingredients
          .map((ing) => Chip(
                label: Text(ing),
                onDeleted: () => setState(() => _ingredients.remove(ing)),
                backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                side: BorderSide.none,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ))
          .toList(),
    ).animate().fadeIn();
  }

  Widget _buildMealPlanView() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('您的专属食谱',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        GlassCard(
          padding: const EdgeInsets.all(20),
          child: Text(_mealPlan!['plan'] ?? '无法生成食谱，请稍后再试'),
        ),
      ],
    ).animate().fadeIn().slideY(begin: 0.2, end: 0);
  }
}
