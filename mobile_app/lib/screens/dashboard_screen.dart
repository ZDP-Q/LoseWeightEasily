import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/navigation_provider.dart';
import '../providers/user_provider.dart';
import '../providers/weight_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(context),
              const SizedBox(height: 24),
              _buildSummaryCards(context),
              const SizedBox(height: 24),
              _buildWeightChart(context),
              const SizedBox(height: 24),
              _buildAICoachEntry(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final userProvider = context.watch<UserProvider>();
    return Row(
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '你好, ${userProvider.displayName}',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const Text('今天也是元气满满的一天 🌟', 
                style: TextStyle(color: AppColors.textSecondary)),
          ],
        ),
        const Spacer(),
        const CircleAvatar(
          radius: 24,
          backgroundColor: AppColors.primary,
          child: Icon(Icons.person, color: Colors.white),
        ),
      ],
    ).animate().fadeIn().slideX();
  }

  Widget _buildSummaryCards(BuildContext context) {
    final weightProvider = context.watch<WeightProvider>();
    final userProvider = context.watch<UserProvider>();
    final currentWeight = weightProvider.latestWeight ?? (userProvider.user?.initialWeightKg ?? 0);
    final goal = userProvider.dailyCalorieGoal ?? 0;

    return Row(
      children: [
        Expanded(
          child: _buildInfoCard(
            '当前体重',
            currentWeight.toStringAsFixed(1),
            'kg',
            FontAwesomeIcons.weightScale,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildInfoCard(
            '目标摄入',
            goal.toStringAsFixed(0),
            'kcal',
            FontAwesomeIcons.fire,
            Colors.orange,
          ),
        ),
      ],
    ).animate().fadeIn(delay: 200.ms).scale();
  }

  Widget _buildInfoCard(String title, String value, String unit, IconData icon, Color color) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: color),
          const SizedBox(height: 12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              const SizedBox(width: 4),
              Text(unit, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
            ],
          ),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildWeightChart(BuildContext context) {
    final weightProvider = context.watch<WeightProvider>();
    final history = weightProvider.records;

    if (history.isEmpty) {
      return const GlassCard(
        height: 200,
        child: Center(child: Text('暂无体重数据')),
      );
    }

    // 转换为图表点
    final spots = history.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), e.value.weightKg);
    }).toList();

    return GlassCard(
      padding: const EdgeInsets.fromLTRB(16, 24, 24, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('体重曲线', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          SizedBox(
            height: 180,
            child: LineChart(
              LineChartData(
                gridData: const FlGridData(show: false),
                titlesData: const FlTitlesData(show: false),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    color: AppColors.primary,
                    barWidth: 4,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.primary.withValues(alpha: 0.1),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 400.ms);
  }

  Widget _buildAICoachEntry(BuildContext context) {
    return GlassCard(
      padding: EdgeInsets.zero,
      color: AppColors.primary.withValues(alpha: 0.1),
      child: InkWell(
        onTap: () => context.read<NavigationProvider>().switchTab(1),
        borderRadius: BorderRadius.circular(24),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              const CircleAvatar(
                backgroundColor: AppColors.primary,
                child: Icon(FontAwesomeIcons.tree, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('对话小松 AI', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    Text('为你开食谱、识别热量或答疑解惑', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios, size: 16, color: AppColors.textSecondary.withValues(alpha: 0.5)),
            ],
          ),
        ),
      ),
    ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.2, end: 0);
  }
}
