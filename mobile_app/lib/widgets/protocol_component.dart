import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

/// 协议组件渲染器
/// 
/// 负责根据 [type] 和 [data] 渲染对应的 Flutter 原生组件。
class ProtocolComponent extends StatelessWidget {
  final String type;
  final Map<String, dynamic>? data;
  final bool isStreaming;

  const ProtocolComponent({
    super.key,
    required this.type,
    this.data,
    this.isStreaming = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isStreaming && data == null) {
      return _buildLoading(context, '小松正在努力计算中...');
    }

    if (data == null) {
      return _buildError(context, '组件数据加载失败');
    }

    switch (type) {
      case 'meal_plan':
        return _buildMealPlan(context, data!);
      case 'food_recognition':
        return _buildFoodRecognition(context, data!);
      default:
        return _buildUnknown(context, type);
    }
  }

  Widget _buildLoading(BuildContext context, String message) {
    return GlassCard(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(16),
      color: AppColors.primary.withValues(alpha: 0.05),
      child: Row(
        children: [
          const SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
          ),
          const SizedBox(width: 16),
          Text(message, style: const TextStyle(color: AppColors.primary, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildError(BuildContext context, String message) {
    return GlassCard(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(16),
      color: Colors.red.withValues(alpha: 0.05),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 20),
          const SizedBox(width: 12),
          Text(message, style: const TextStyle(color: Colors.red, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildUnknown(BuildContext context, String type) {
    return _buildError(context, '暂不支持的组件类型: $type');
  }

  // --- 具体的组件渲染逻辑 ---

  Widget _buildMealPlan(BuildContext context, Map<String, dynamic> data) {
    final title = data['title'] ?? '今日食谱';
    final totalCalories = data['total_calories'] ?? 0;
    final meals = (data['meals'] as List?) ?? [];

    return GlassCard(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(16),
      color: AppColors.primary.withValues(alpha: 0.03),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('🥗 $title', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.primary)),
              Text('$totalCalories kcal', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.primary)),
            ],
          ),
          const Divider(height: 24),
          ...meals.map((meal) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                children: [
                  Container(
                    width: 48,
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      meal['time'] ?? '', 
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.primary),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(meal['name'] ?? '', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                        if (meal['calories'] != null)
                          Text('${meal['calories']} kcal', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildFoodRecognition(BuildContext context, Map<String, dynamic> data) {
    final foodName = data['food_name'] ?? '未知食物';
    final calories = data['calories'] ?? 0;
    final nutrients = data['nutrients'] as Map?;

    return GlassCard(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(16),
      color: Colors.orange.withValues(alpha: 0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(FontAwesomeIcons.magnifyingGlassChart, color: Colors.orange, size: 18),
              const SizedBox(width: 8),
              const Text('识别结果', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.orange)),
              const Spacer(),
              if (isStreaming)
                const SizedBox(width: 12, height: 12, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.orange)),
            ],
          ),
          const SizedBox(height: 12),
          Text(foodName, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text('估算热量: $calories kcal', style: const TextStyle(fontSize: 15, color: Colors.orange, fontWeight: FontWeight.bold)),
          if (nutrients != null) ...[
             const SizedBox(height: 12),
             Wrap(
               spacing: 12,
               children: nutrients.entries.map((e) => _buildNutrientChip(e.key, e.value.toString())).toList(),
             ),
          ],
        ],
      ),
    );
  }

  Widget _buildNutrientChip(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
        Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
      ],
    );
  }
}
