import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class BmrScreen extends StatefulWidget {
  const BmrScreen({super.key});

  @override
  State<BmrScreen> createState() => _BmrScreenState();
}

class _BmrScreenState extends State<BmrScreen> {
  double _weight = 70;
  double _height = 175;
  int _age = 25;
  String _gender = 'male';
  Map<String, dynamic>? _result;
  bool _isCalculating = false;

  void _calculate() async {
    setState(() => _isCalculating = true);
    try {
      final api = context.read<ApiService>();
      final result = await api.calculateBmr(_weight, _height, _age, _gender);
      if (!mounted) return;
      setState(() => _result = result);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('计算失败: $e'), backgroundColor: AppColors.danger),
      );
    } finally {
      setState(() => _isCalculating = false);
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
                '健康指标',
                style: Theme.of(context).textTheme.displaySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  fontSize: 28,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '计算您的基础代谢率和日消耗量',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 32),
              _buildGenderSelection(),
              const SizedBox(height: 24),
              _buildInputCard('体重 (kg)', _weight, 30, 150, (val) => setState(() => _weight = val)),
              const SizedBox(height: 16),
              _buildInputCard('身高 (cm)', _height, 100, 220, (val) => setState(() => _height = val)),
              const SizedBox(height: 16),
              _buildInputCard('年龄', _age.toDouble(), 10, 100, (val) => setState(() => _age = val.toInt())),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isCalculating ? null : _calculate,
                child: _isCalculating 
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('立即计算'),
              ),
              const SizedBox(height: 32),
              if (_result != null) _buildResultView(),
              const SizedBox(height: 100),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGenderSelection() {
    return Row(
      children: [
        Expanded(
          child: _GenderCard(
            label: '男性',
            icon: FontAwesomeIcons.mars,
            isSelected: _gender == 'male',
            onTap: () => setState(() => _gender = 'male'),
            activeColor: Colors.blue,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _GenderCard(
            label: '女性',
            icon: FontAwesomeIcons.venus,
            isSelected: _gender == 'female',
            onTap: () => setState(() => _gender = 'female'),
            activeColor: Colors.pink,
          ),
        ),
      ],
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildInputCard(String label, double value, double min, double max, ValueChanged<double> onChanged) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
              Text(
                value.toStringAsFixed(label.contains('年龄') ? 0 : 1),
                style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 18),
              ),
            ],
          ),
          Slider(
            value: value,
            min: min,
            max: max,
            activeColor: AppColors.primary,
            inactiveColor: AppColors.primary.withOpacity(0.1),
            onChanged: onChanged,
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildResultView() {
    final tdee = _result!['tdee'] as Map<String, dynamic>;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('您的 BMR', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        GlassCard(
          color: AppColors.primary.withOpacity(0.1),
          child: Center(
            child: Text(
              '${(_result!['bmr'] as double).toStringAsFixed(0)} kcal',
              style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppColors.primary),
            ),
          ),
        ),
        const SizedBox(height: 24),
        Text('不同活动强度的 TDEE', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        _buildTdeeItem('久坐 (办公室工作)', tdee['sedentary']),
        _buildTdeeItem('轻度活动 (每周运动1-3次)', tdee['light']),
        _buildTdeeItem('中度活动 (每周运动3-5次)', tdee['moderate']),
        _buildTdeeItem('活跃 (每周运动6-7次)', tdee['active']),
        _buildTdeeItem('非常活跃 (高强度运动/体力劳动)', tdee['very_active']),
      ],
    ).animate().fadeIn();
  }

  Widget _buildTdeeItem(String label, dynamic value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: GlassCard(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(child: Text(label, style: const TextStyle(fontSize: 13))),
            Text(
              '${(value as double).toStringAsFixed(0)} kcal',
              style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.secondary),
            ),
          ],
        ),
      ),
    );
  }
}

class _GenderCard extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;
  final Color activeColor;

  const _GenderCard({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
    required this.activeColor,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.symmetric(vertical: 20),
        decoration: BoxDecoration(
          color: isSelected ? activeColor.withOpacity(0.1) : AppColors.bgCard.withOpacity(0.4),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? activeColor : Colors.white.withOpacity(0.05),
            width: 2,
          ),
        ),
        child: Column(
          children: [
            Icon(icon, size: 32, color: isSelected ? activeColor : AppColors.textSecondary),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? activeColor : AppColors.textSecondary,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
