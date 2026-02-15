import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class WeightScreen extends StatefulWidget {
  const WeightScreen({super.key});

  @override
  State<WeightScreen> createState() => _WeightScreenState();
}

class _WeightScreenState extends State<WeightScreen> {
  List<dynamic> _history = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    setState(() => _isLoading = true);
    try {
      final api = context.read<ApiService>();
      final history = await api.getWeightHistory();
      setState(() => _history = history);
    } catch (e) {
      // Handle error
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showAddWeightDialog() {
    double weight = _history.isNotEmpty ? _history.first['weight_kg'] : 70.0;
    final controller = TextEditingController(text: '');

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        decoration: const BoxDecoration(
          color: AppColors.bgDark,
          borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('记录今日体重', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 24),
              TextField(
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                autofocus: true,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                decoration: const InputDecoration(
                  hintText: '00.0',
                  suffixText: 'kg',
                ),
                onChanged: (val) => weight = double.tryParse(val) ?? weight,
              ),
              const SizedBox(height: 24),
              TextField(
                controller: controller,
                decoration: const InputDecoration(
                  hintText: '添加备注 (可选)',
                  prefixIcon: Icon(Icons.notes),
                ),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () async {
                  try {
                    final api = context.read<ApiService>();
                    await api.addWeight(weight, controller.text);
                    if (!context.mounted) return;
                    Navigator.pop(context);
                    _fetchHistory();
                  } catch (e) {
                    // Show error
                  }
                },
                child: const Text('保存记录'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _fetchHistory,
          color: AppColors.primary,
          child: CustomScrollView(
            slivers: [
              SliverPadding(
                padding: const EdgeInsets.all(24),
                sliver: SliverToBoxAdapter(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '体重记录',
                        style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          fontSize: 28,
                        ),
                      ),
                      const SizedBox(height: 24),
                      _buildChartCard(),
                      const SizedBox(height: 32),
                      Text('历史记录', style: Theme.of(context).textTheme.titleLarge),
                    ],
                  ),
                ),
              ),
              if (_isLoading)
                const SliverFillRemaining(child: Center(child: CircularProgressIndicator()))
              else if (_history.isEmpty)
                const SliverFillRemaining(child: Center(child: Text('暂无记录')))
              else
                SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  sliver: SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final entry = _history[index];
                        final date = DateTime.parse(entry['recorded_at']);
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: GlassCard(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      DateFormat('MM月dd日').format(date),
                                      style: const TextStyle(fontWeight: FontWeight.bold),
                                    ),
                                    Text(
                                      DateFormat('HH:mm').format(date),
                                      style: TextStyle(color: AppColors.textSecondary, fontSize: 12),
                                    ),
                                  ],
                                ),
                                const Spacer(),
                                if (entry['notes'] != null && entry['notes'].isNotEmpty)
                                  Icon(Icons.notes, size: 16, color: AppColors.textMuted),
                                const SizedBox(width: 16),
                                Text(
                                  '${entry['weight_kg']} kg',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.primary,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ).animate().fadeIn(delay: (index * 30).ms).slideX();
                      },
                      childCount: _history.length,
                    ),
                  ),
                ),
              const SliverToBoxAdapter(child: SizedBox(height: 100)),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddWeightDialog,
        backgroundColor: AppColors.primary,
        icon: const Icon(Icons.add),
        label: const Text('记录体重'),
      ).animate().scale(delay: 400.ms),
    );
  }

  Widget _buildChartCard() {
    if (_history.isEmpty) return const SizedBox.shrink();
    
    // Reverse history for chart (oldest to newest)
    final chartData = _history.reversed.toList();
    
    return GlassCard(
      height: 200,
      padding: const EdgeInsets.fromLTRB(10, 24, 24, 10),
      child: LineChart(
        LineChartData(
          gridData: const FlGridData(show: false),
          titlesData: const FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: chartData.asMap().entries.map((e) {
                return FlSpot(e.key.toDouble(), e.value['weight_kg'].toDouble());
              }).toList(),
              isCurved: true,
              color: AppColors.primary,
              barWidth: 4,
              isStrokeCapRound: true,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: AppColors.primary.withOpacity(0.1),
              ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn().scale();
  }
}
