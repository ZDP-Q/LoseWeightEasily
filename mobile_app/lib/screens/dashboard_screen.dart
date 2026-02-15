import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';
import '../providers/weight_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';
import 'main_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  /// 跳转到指定 Tab（通过 MainScreen 的回调）
  void _navigateToTab(BuildContext context, int tabIndex) {
    context.findAncestorStateOfType<MainScreenState>()?.switchTab(tabIndex);
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
              _buildHeader(context),
              const SizedBox(height: 28),
              _buildWeightProgressCard(context),
              const SizedBox(height: 20),
              _buildCalorieCard(context),
              const SizedBox(height: 24),
              _buildQuickActions(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final userProvider = context.watch<UserProvider>();
    final name = userProvider.displayName;

    final hour = DateTime.now().hour;
    String greeting;
    if (hour < 6) {
      greeting = '夜深了';
    } else if (hour < 12) {
      greeting = '早上好';
    } else if (hour < 18) {
      greeting = '下午好';
    } else {
      greeting = '晚上好';
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '$greeting, $name',
                style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      fontSize: 24,
                    ),
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                userProvider.hasUser ? '今天也是自律的一天 💪' : '设置个人资料，开启减重之旅',
                style: const TextStyle(color: AppColors.textSecondary),
              ),
            ],
          ),
        ),
      ],
    ).animate().fadeIn().slideX();
  }

  Widget _buildWeightProgressCard(BuildContext context) {
    final userProvider = context.watch<UserProvider>();
    final weightProvider = context.watch<WeightProvider>();

    if (!userProvider.hasUser) {
      return _buildSetupCard(context);
    }

    final user = userProvider.user!;
    final currentWeight = weightProvider.latestWeight ?? user.initialWeightKg;
    final targetWeight = user.targetWeightKg;
    final initialWeight = user.initialWeightKg;

    // 计算减重进度
    final totalToLose = initialWeight - targetWeight;
    final lost = initialWeight - currentWeight;
    final progress = totalToLose > 0 ? (lost / totalToLose).clamp(0.0, 1.0) : 0.0;

    final weightChange = weightProvider.weightChange(initialWeight);
    final changeText = weightChange != null
        ? (weightChange <= 0
            ? '${weightChange.toStringAsFixed(1)} kg'
            : '+${weightChange.toStringAsFixed(1)} kg')
        : '--';
    final changeColor = (weightChange ?? 0) <= 0 ? AppColors.secondary : AppColors.danger;

    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('减重进度', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: changeColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  changeText,
                  style: TextStyle(
                    color: changeColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: AppColors.primary.withValues(alpha: 0.1),
              valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
              minHeight: 12,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${initialWeight.toStringAsFixed(1)} kg',
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              Text(
                '目标 ${targetWeight.toStringAsFixed(1)} kg',
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStat('当前体重', '${currentWeight.toStringAsFixed(1)} kg',
                  AppColors.primary),
              _buildStat('目标体重', '${targetWeight.toStringAsFixed(1)} kg',
                  AppColors.secondary),
              _buildStat(
                '已减',
                '${lost.toStringAsFixed(1)} kg',
                lost > 0 ? AppColors.secondary : AppColors.textSecondary,
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(delay: 200.ms).scale();
  }

  Widget _buildSetupCard(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(24),
      color: AppColors.primary.withValues(alpha: 0.08),
      child: Column(
        children: [
          const Icon(FontAwesomeIcons.userGear, color: AppColors.primary, size: 40),
          const SizedBox(height: 16),
          const Text(
            '欢迎使用 LoseWeightEasily',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
          ),
          const SizedBox(height: 8),
          const Text(
            '请先设置个人资料，以获取精准的减重建议',
            style: TextStyle(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _navigateToTab(context, 4),
              icon: const Icon(Icons.arrow_forward),
              label: const Text('去设置'),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 200.ms).scale();
  }

  Widget _buildCalorieCard(BuildContext context) {
    final userProvider = context.watch<UserProvider>();
    if (!userProvider.hasUser) return const SizedBox.shrink();

    final bmr = userProvider.bmr;
    final tdee = userProvider.dailyCalorieGoal;

    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('代谢概览',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              Icon(FontAwesomeIcons.fire, size: 18, color: Colors.orange.shade300),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildMetricColumn(
                '基础代谢 (BMR)',
                bmr != null ? '${bmr.toStringAsFixed(0)} kcal' : '未计算',
                Colors.blue,
              ),
              Container(width: 1, height: 40, color: AppColors.border.withValues(alpha: 0.3)),
              _buildMetricColumn(
                '每日目标 (TDEE)',
                tdee != null ? '${tdee.toStringAsFixed(0)} kcal' : '未设置',
                Colors.orange,
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildMetricColumn(String label, String value, Color color) {
    return Column(
      children: [
        Text(label,
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        const SizedBox(height: 6),
        Text(value,
            style: TextStyle(
                fontSize: 20, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }

  Widget _buildStat(String label, String value, Color color) {
    return Column(
      children: [
        Text(label,
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        const SizedBox(height: 4),
        Text(value,
            style: TextStyle(fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      childAspectRatio: 1.4,
      children: [
        _buildActionCard(context, '记体重', FontAwesomeIcons.weightScale,
            AppColors.primary, () => _navigateToTab(context, 2)),
        _buildActionCard(context, '查食物', FontAwesomeIcons.magnifyingGlass,
            AppColors.secondary, () => _navigateToTab(context, 1)),
        _buildActionCard(context, '开食谱', FontAwesomeIcons.utensils,
            Colors.orange, () => _navigateToTab(context, 3)),
        _buildActionCard(context, '个人资料', FontAwesomeIcons.user,
            Colors.blue, () => _navigateToTab(context, 4)),
      ],
    ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.2, end: 0);
  }

  Widget _buildActionCard(BuildContext context, String title, IconData icon,
      Color color, VoidCallback onTap) {
    return GlassCard(
      padding: EdgeInsets.zero,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
