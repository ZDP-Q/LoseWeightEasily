import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../models/weight_record.dart';
import '../providers/weight_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class WeightScreen extends StatelessWidget {
  const WeightScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<WeightProvider>();

    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '体重趋势',
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          fontSize: 28,
                        ),
                  ),
                  IconButton.filled(
                    onPressed: () => _showAddDialog(context),
                    icon: const Icon(Icons.add),
                  ),
                ],
              ),
            ),
            Expanded(
              child: provider.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : provider.error != null && !provider.hasRecords
                      ? _buildErrorState(context, provider)
                      : !provider.hasRecords
                          ? _buildEmptyState(context)
                          : _buildContent(context, provider),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context, WeightProvider provider) {
    return RefreshIndicator(
      onRefresh: provider.loadHistory,
      child: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        children: [
          if (provider.records.length >= 2) ...[
            _buildChart(context, provider.records),
            const SizedBox(height: 24),
          ],
          if (provider.latestRecord != null) ...[
            _buildLatestCard(context, provider.latestRecord!),
            const SizedBox(height: 16),
          ],
          Text(
            '历史记录',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 18),
          ),
          const SizedBox(height: 12),
          ...List.generate(provider.records.length, (index) {
            return _buildRecordItem(context, provider.records[index], index);
          }),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildChart(BuildContext context, List<WeightRecord> records) {
    // 取最近 30 条、按时间正序排列
    final sorted = records.length > 30 ? records.sublist(0, 30) : records;
    final chartData = sorted.reversed.toList();

    if (chartData.length < 2) return const SizedBox.shrink();

    final weights = chartData.map((r) => r.weightKg).toList();
    final minW = weights.reduce((a, b) => a < b ? a : b) - 1;
    final maxW = weights.reduce((a, b) => a > b ? a : b) + 1;

    return GlassCard(
      padding: const EdgeInsets.fromLTRB(8, 24, 24, 12),
      child: SizedBox(
        height: 200,
        child: LineChart(
          LineChartData(
            minY: minW,
            maxY: maxW,
            gridData: FlGridData(
              show: true,
              drawVerticalLine: false,
              horizontalInterval: ((maxW - minW) / 4).ceilToDouble().clamp(1, 100),
              getDrawingHorizontalLine: (_) => FlLine(
                color: AppColors.border.withValues(alpha: 0.2),
                strokeWidth: 1,
              ),
            ),
            titlesData: FlTitlesData(
              topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 32,
                  interval: (chartData.length / 4).ceilToDouble().clamp(1, 100),
                  getTitlesWidget: (value, meta) {
                    final idx = value.toInt();
                    if (idx < 0 || idx >= chartData.length) {
                      return const SizedBox.shrink();
                    }
                    return Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        DateFormat('M/d').format(chartData[idx].recordedAt),
                        style: const TextStyle(
                            fontSize: 10, color: AppColors.textSecondary),
                      ),
                    );
                  },
                ),
              ),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 42,
                  interval: ((maxW - minW) / 4).ceilToDouble().clamp(1, 100),
                  getTitlesWidget: (value, meta) => Text(
                    value.toStringAsFixed(1),
                    style: const TextStyle(
                        fontSize: 10, color: AppColors.textSecondary),
                  ),
                ),
              ),
            ),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: List.generate(chartData.length,
                    (i) => FlSpot(i.toDouble(), chartData[i].weightKg)),
                isCurved: true,
                curveSmoothness: 0.3,
                preventCurveOverShooting: true,
                color: AppColors.primary,
                barWidth: 3,
                isStrokeCapRound: true,
                dotData: FlDotData(
                  show: true,
                  getDotPainter: (spot, percent, barData, index) =>
                      FlDotCirclePainter(
                    radius: 3,
                    color: AppColors.primary,
                    strokeWidth: 1.5,
                    strokeColor: Colors.white,
                  ),
                ),
                belowBarData: BarAreaData(
                  show: true,
                  color: AppColors.primary.withValues(alpha: 0.08),
                ),
              ),
            ],
            lineTouchData: LineTouchData(
              touchTooltipData: LineTouchTooltipData(
                getTooltipItems: (spots) => spots.map((spot) {
                  final record = chartData[spot.x.toInt()];
                  return LineTooltipItem(
                    '${DateFormat('M月d日').format(record.recordedAt)}\n${record.weightKg.toStringAsFixed(1)} kg',
                    const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ),
      ),
    ).animate().fadeIn(delay: 200.ms);
  }

  Widget _buildLatestCard(BuildContext context, WeightRecord record) {
    return GlassCard(
      color: AppColors.primary.withValues(alpha: 0.1),
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            height: 48,
            width: 48,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Icon(FontAwesomeIcons.weightScale,
                color: AppColors.primary, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('最新体重',
                    style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                const SizedBox(height: 2),
                Text(
                  '${record.weightKg.toStringAsFixed(1)} kg',
                  style: const TextStyle(
                      fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.primary),
                ),
              ],
            ),
          ),
          Text(
            DateFormat('M月d日').format(record.recordedAt),
            style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
          ),
        ],
      ),
    ).animate().fadeIn();
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(FontAwesomeIcons.weightScale,
              size: 64,
              color: AppColors.textSecondary.withValues(alpha: 0.2)),
          const SizedBox(height: 16),
          const Text('尚无体重记录',
              style: TextStyle(color: AppColors.textSecondary, fontSize: 18)),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: () => _showAddDialog(context),
            icon: const Icon(Icons.add, size: 18),
            label: const Text('记录第一次'),
            style: ElevatedButton.styleFrom(
              minimumSize: const Size(200, 48),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, WeightProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(FontAwesomeIcons.circleExclamation,
              size: 48, color: AppColors.danger.withValues(alpha: 0.5)),
          const SizedBox(height: 16),
          Text(provider.error ?? '加载失败',
              style: const TextStyle(color: AppColors.textSecondary)),
          const SizedBox(height: 12),
          TextButton.icon(
            onPressed: provider.loadHistory,
            icon: const Icon(Icons.refresh),
            label: const Text('重试'),
          ),
        ],
      ),
    );
  }

  Widget _buildRecordItem(BuildContext context, WeightRecord record, int index) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: GlassCard(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(DateFormat('yyyy-MM-dd').format(record.recordedAt),
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                if (record.notes?.isNotEmpty == true)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(record.notes!,
                        style: const TextStyle(
                            fontSize: 12, color: AppColors.textSecondary)),
                  ),
              ],
            ),
            Text(
              '${record.weightKg.toStringAsFixed(1)} kg',
              style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: (index * 50).ms).slideX();
  }

  void _showAddDialog(BuildContext context) {
    final weightController = TextEditingController();
    final notesController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('记录今日体重'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: weightController,
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                suffixText: 'kg',
                hintText: '请输入体重',
                labelText: '体重',
              ),
              autofocus: true,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: notesController,
              decoration: const InputDecoration(
                hintText: '今天状态如何？（可选）',
                labelText: '备注',
              ),
              maxLines: 2,
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () async {
              final val = double.tryParse(weightController.text);
              if (val == null || val <= 0 || val > 500) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('请输入有效的体重（0-500 kg）'),
                    backgroundColor: AppColors.danger,
                  ),
                );
                return;
              }
              Navigator.pop(ctx);
              try {
                await context.read<WeightProvider>().addRecord(
                      val,
                      notes: notesController.text.trim().isNotEmpty
                          ? notesController.text.trim()
                          : null,
                    );
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('体重记录成功 🎉'),
                    backgroundColor: AppColors.success,
                  ),
                );
              } catch (e) {
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('记录失败: $e'),
                    backgroundColor: AppColors.danger,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
                minimumSize: const Size(80, 40)),
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }
}
