import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../services/api_service.dart';
import '../providers/user_provider.dart';
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
  bool _hasAutoFilled = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_hasAutoFilled) {
      _autoFillFromUser();
    }
  }

  void _autoFillFromUser() {
    final userProvider = context.read<UserProvider>();
    if (userProvider.hasUser) {
      final user = userProvider.user!;
      setState(() {
        _weight = user.initialWeightKg;
        _height = user.heightCm;
        _age = user.age;
        _gender = user.gender;
        _hasAutoFilled = true;
      });
    }
  }

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

  Future<void> _saveToProfile() async {
    if (_result == null) return;
    final bmr = (_result!['bmr'] as num).toDouble();
    final userProvider = context.read<UserProvider>();
    if (!userProvider.hasUser) return;

    final updatedUser = userProvider.user!.copyWith(
      bmr: bmr,
      dailyCalorieGoal: bmr * 1.2, // 默认久坐活动水平
    );

    try {
      await userProvider.updateUser(updatedUser);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('已保存到个人资料 ✅'), backgroundColor: AppColors.success),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('保存失败: $e'), backgroundColor: AppColors.danger),
      );
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
              const Text(
                '计算您的基础代谢率和日消耗量',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 32),
              _buildGenderSelection(),
              const SizedBox(height: 24),
              _buildInputCard('体重 (kg)', _weight, 30, 200,
                  (val) => setState(() => _weight = val)),
              const SizedBox(height: 16),
              _buildInputCard('身高 (cm)', _height, 100, 220,
                  (val) => setState(() => _height = val)),
              const SizedBox(height: 16),
              _buildInputCard('年龄', _age.toDouble(), 10, 100,
                  (val) => setState(() => _age = val.toInt())),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isCalculating ? null : _calculate,
                child: _isCalculating
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                            color: Colors.white, strokeWidth: 2))
                    : const Text('立即计算'),
              ),
              const SizedBox(height: 32),
              if (_result != null) _buildResultView(),
              const SizedBox(height: 40),
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

  Widget _buildInputCard(String label, double value, double min, double max,
      ValueChanged<double> onChanged) {
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
                style: const TextStyle(
                    color: AppColors.primary,
                    fontWeight: FontWeight.bold,
                    fontSize: 18),
              ),
            ],
          ),
          Slider(
            value: value.clamp(min, max),
            min: min,
            max: max,
            activeColor: AppColors.primary,
            inactiveColor: AppColors.primary.withValues(alpha: 0.1),
            onChanged: onChanged,
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildResultView() {
    final tdee = _result!['tdee'] as Map<String, dynamic>;
    final bmrValue = (_result!['bmr'] as num).toDouble();
    final userProvider = context.watch<UserProvider>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text('您的 BMR', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(width: 8),
            Tooltip(
              message: 'BMR（基础代谢率）是您在完全静卧状态下维持生命所需的最低热量',
              child: Icon(Icons.help_outline,
                  size: 18, color: AppColors.textSecondary.withValues(alpha: 0.6)),
            ),
          ],
        ),
        const SizedBox(height: 12),
        GlassCard(
          color: AppColors.primary.withValues(alpha: 0.1),
          child: Center(
            child: Text(
              '${bmrValue.toStringAsFixed(0)} kcal',
              style: const TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary),
            ),
          ),
        ),
        if (userProvider.hasUser) ...[
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: _saveToProfile,
              icon: const Icon(Icons.save_alt, size: 18),
              label: const Text('保存到个人资料'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.primary,
                side: const BorderSide(color: AppColors.primary),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
        const SizedBox(height: 24),
        Row(
          children: [
            Text('不同活动强度的 TDEE',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(width: 8),
            Tooltip(
              message: 'TDEE（每日总能量消耗）= BMR × 活动因子，是每天实际消耗的总热量',
              child: Icon(Icons.help_outline,
                  size: 18, color: AppColors.textSecondary.withValues(alpha: 0.6)),
            ),
          ],
        ),
        const SizedBox(height: 12),
        _buildTdeeItem('久坐 (办公室工作)', tdee['sedentary']),
        _buildTdeeItem('轻度活动 (每周1-3次)', tdee['light']),
        _buildTdeeItem('中度活动 (每周3-5次)', tdee['moderate']),
        _buildTdeeItem('活跃 (每周6-7次)', tdee['active']),
        _buildTdeeItem('非常活跃 (高强度)', tdee['very_active']),
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
            Expanded(
                child: Text(label, style: const TextStyle(fontSize: 13))),
            Text(
              '${(value as num).toStringAsFixed(0)} kcal',
              style: const TextStyle(
                  fontWeight: FontWeight.bold, color: AppColors.secondary),
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
          color: isSelected
              ? activeColor.withValues(alpha: 0.1)
              : AppColors.bgCard.withValues(alpha: 0.4),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color:
                isSelected ? activeColor : Colors.white.withValues(alpha: 0.05),
            width: 2,
          ),
        ),
        child: Column(
          children: [
            Icon(icon,
                size: 32,
                color: isSelected ? activeColor : AppColors.textSecondary),
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
