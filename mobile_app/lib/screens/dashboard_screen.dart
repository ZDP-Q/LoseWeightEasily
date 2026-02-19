import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../providers/navigation_provider.dart';
import '../providers/user_provider.dart';
import '../providers/weight_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<NavigationProvider>().onHomeRefreshed = _refreshData;
    });
    _refreshData();
  }

  @override
  void dispose() {
    // 这里的 context 访问可能不安全，但在 Provider 结构中通常可行。
    // 更好的做法是在 MainScreen 或通过其他方式管理回调。
    super.dispose();
  }

  Future<void> _refreshData() async {
    if (!mounted) return;
    context.read<UserProvider>().loadUser();
    context.read<WeightProvider>().loadHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _refreshData,
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
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
    // 反转历史记录，使其按时间顺序从左到右显示
    final history = weightProvider.records.reversed.toList();

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

    // 计算 Y 轴范围
    double minY = history.map((e) => e.weightKg).reduce((a, b) => a < b ? a : b) - 2;
    double maxY = history.map((e) => e.weightKg).reduce((a, b) => a > b ? a : b) + 2;
    if (minY < 0) minY = 0;

    return GlassCard(
      padding: const EdgeInsets.fromLTRB(16, 24, 24, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('体重曲线', style: TextStyle(fontWeight: FontWeight.bold)),
              Text('单位: kg', style: TextStyle(fontSize: 10, color: AppColors.textSecondary.withValues(alpha: 0.5))),
            ],
          ),
          const SizedBox(height: 24),
          SizedBox(
            height: 180,
            child: LineChart(
              LineChartData(
                minY: minY,
                maxY: maxY,
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (value) => FlLine(
                    color: AppColors.border.withValues(alpha: 0.1),
                    strokeWidth: 1,
                  ),
                ),
                titlesData: FlTitlesData(
                  show: true,
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 22,
                      interval: (history.length / 5).clamp(1, 10).toDouble(),
                      getTitlesWidget: (value, meta) {
                        int index = value.toInt();
                        if (index >= 0 && index < history.length) {
                          return Padding(
                            padding: const EdgeInsets.only(top: 8.0),
                            child: Text(
                              DateFormat('MM/dd').format(history[index].recordedAt),
                              style: const TextStyle(fontSize: 9, color: AppColors.textSecondary),
                            ),
                          );
                        }
                        return const SizedBox();
                      },
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 32,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          value.toStringAsFixed(0),
                          style: const TextStyle(fontSize: 9, color: AppColors.textSecondary),
                        );
                      },
                    ),
                  ),
                ),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    curveSmoothness: 0.3,
                    color: AppColors.primary,
                    barWidth: 3,
                    isStrokeCapRound: true,
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, barData, index) => FlDotCirclePainter(
                        radius: 3,
                        color: Colors.white,
                        strokeWidth: 2,
                        strokeColor: AppColors.primary,
                      ),
                    ),
                    belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          AppColors.primary.withValues(alpha: 0.2),
                          AppColors.primary.withValues(alpha: 0.0),
                        ],
                      ),
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
