import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../services/api_service.dart';
import '../models/user.dart';
import '../providers/user_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';
import 'bmr_screen.dart';

class UserScreen extends StatefulWidget {
  const UserScreen({super.key});

  @override
  State<UserScreen> createState() => _UserScreenState();
}

class _UserScreenState extends State<UserScreen> {
  bool _isEditing = false;
  bool _isSaving = false;

  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _ageController = TextEditingController();
  final _heightController = TextEditingController();
  final _initialWeightController = TextEditingController();
  final _targetWeightController = TextEditingController();
  final _calorieGoalController = TextEditingController();
  String _gender = 'male';

  @override
  void initState() {
    super.initState();
    _syncFormFromProvider();
  }

  void _syncFormFromProvider() {
    final provider = context.read<UserProvider>();
    if (provider.hasUser) {
      final user = provider.user!;
      _nameController.text = user.name;
      _ageController.text = user.age.toString();
      _heightController.text = user.heightCm.toString();
      _initialWeightController.text = user.initialWeightKg.toString();
      _targetWeightController.text = user.targetWeightKg.toString();
      _calorieGoalController.text = user.dailyCalorieGoal?.toString() ?? '';
      _gender = user.gender;
    }
  }

  Future<void> _saveUser() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    final weight = double.parse(_initialWeightController.text);
    final height = double.parse(_heightController.text);
    final age = int.parse(_ageController.text);

    // 在 await 之前捕获引用
    final api = context.read<ApiService>();
    final userProvider = context.read<UserProvider>();

    // 调用后端计算 BMR，而非前端手动计算
    double? bmr;
    try {
      final result = await api.calculateBmr(weight, height, age, _gender);
      bmr = (result['bmr'] as num).toDouble();
    } catch (_) {
      // BMR 计算失败时仍允许保存，只是 BMR 为 null

    }

    final newUser = UserProfile(
      name: _nameController.text.trim(),
      age: age,
      gender: _gender,
      heightCm: height,
      initialWeightKg: weight,
      targetWeightKg: double.parse(_targetWeightController.text),
      bmr: bmr,
      dailyCalorieGoal: _calorieGoalController.text.isNotEmpty
          ? double.parse(_calorieGoalController.text)
          : (bmr != null ? bmr * 1.2 : null),
    );

    try {
      if (!userProvider.hasUser) {
        await userProvider.createUser(newUser);
      } else {
        await userProvider.updateUser(newUser);
      }
      if (!mounted) return;
      setState(() => _isEditing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('保存成功 ✅'), backgroundColor: AppColors.success),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text('保存失败: $e'), backgroundColor: AppColors.danger),
      );
    } finally {
      setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<UserProvider>();

    if (provider.isLoading && !provider.hasUser) {
      return const Scaffold(
          body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '个人资料',
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          fontSize: 28,
                        ),
                  ),
                  if (provider.hasUser)
                    IconButton(
                      icon: Icon(
                          _isEditing ? Icons.close : Icons.edit,
                          color: AppColors.primary),
                      onPressed: () {
                        if (!_isEditing) _syncFormFromProvider();
                        setState(() => _isEditing = !_isEditing);
                      },
                    ),
                ],
              ),
              const SizedBox(height: 24),
              if (!provider.hasUser || _isEditing)
                _buildForm()
              else
                _buildProfileView(provider),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileView(UserProvider provider) {
    final user = provider.user!;

    return Column(
      children: [
        Center(
          child: Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.primary, width: 2),
            ),
            child: const CircleAvatar(
              radius: 50,
              backgroundColor: Colors.transparent,
              child:
                  Icon(Icons.person, size: 60, color: AppColors.primary),
            ),
          ),
        ).animate().scale(delay: 200.ms),
        const SizedBox(height: 24),
        Center(
          child: Text(
            user.name,
            style:
                const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 32),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.5,
          children: [
            _buildInfoCard(
                '基础代谢 (BMR)',
                user.bmr != null
                    ? '${user.bmr!.toStringAsFixed(0)} kcal'
                    : '未计算',
                FontAwesomeIcons.bolt),
            _buildInfoCard('性别', user.gender == 'male' ? '男' : '女',
                FontAwesomeIcons.venusMars),
            _buildInfoCard('身高', '${user.heightCm} cm',
                FontAwesomeIcons.arrowsUpDown),
            _buildInfoCard('目标体重', '${user.targetWeightKg} kg',
                FontAwesomeIcons.bullseye),
          ],
        ),
        const SizedBox(height: 24),
        GlassCard(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              const Icon(FontAwesomeIcons.fire,
                  color: Colors.orange, size: 30),
              const SizedBox(width: 20),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('每日目标热量 (TDEE)',
                      style: TextStyle(color: AppColors.textSecondary)),
                  Text(
                    user.dailyCalorieGoal != null
                        ? '${user.dailyCalorieGoal!.toStringAsFixed(0)} kcal'
                        : '未设置',
                    style: const TextStyle(
                        fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ],
          ),
        ).animate().fadeIn(delay: 400.ms).slideX(),
        const SizedBox(height: 24),

        // 快速入口：计算代谢
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const BmrScreen()),
              );
            },
            icon: const Icon(FontAwesomeIcons.calculator, size: 16),
            label: const Text('重新计算代谢'),
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.primary,
              side: const BorderSide(color: AppColors.primary),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14)),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInfoCard(String label, String value, IconData icon) {
    return GlassCard(
      padding: const EdgeInsets.all(12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20, color: AppColors.primary),
          const SizedBox(height: 8),
          Text(label,
              style: const TextStyle(
                  fontSize: 12, color: AppColors.textSecondary)),
          const SizedBox(height: 4),
          Text(value,
              style: const TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold)),
        ],
      ),
    ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2, end: 0);
  }

  Widget _buildForm() {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          _buildTextField(_nameController, '姓名', Icons.person),
          const SizedBox(height: 16),
          _buildTextField(_ageController, '年龄', Icons.calendar_today,
              isNumber: true),
          const SizedBox(height: 16),
          _buildGenderDropdown(),
          const SizedBox(height: 16),
          _buildTextField(_heightController, '身高 (cm)', Icons.height,
              isNumber: true),
          const SizedBox(height: 16),
          _buildTextField(
              _initialWeightController, '初始体重 (kg)', Icons.monitor_weight,
              isNumber: true),
          const SizedBox(height: 16),
          _buildTextField(_targetWeightController, '目标体重 (kg)', Icons.flag,
              isNumber: true),
          const SizedBox(height: 16),
          _buildTextField(_calorieGoalController,
              '自定义每日热量目标 (可选)', Icons.local_fire_department,
              isNumber: true, isRequired: false),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isSaving ? null : _saveUser,
              child: _isSaving
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : const Text('保存并计算代谢'),
            ),
          ),
        ],
      ),
    ).animate().fadeIn();
  }

  Widget _buildTextField(
      TextEditingController controller, String label, IconData icon,
      {bool isNumber = false, bool isRequired = true}) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, size: 20),
        filled: true,
        fillColor: AppColors.bgCard.withValues(alpha: 0.4),
        border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide.none),
      ),
      keyboardType:
          isNumber ? TextInputType.number : TextInputType.text,
      validator: (value) {
        if (isRequired && (value == null || value.isEmpty)) {
          return '请输入$label';
        }
        if (isNumber &&
            value != null &&
            value.isNotEmpty &&
            double.tryParse(value) == null) {
          return '请输入有效的数字';
        }
        return null;
      },
    );
  }

  Widget _buildGenderDropdown() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.bgCard.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(15),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _gender,
          isExpanded: true,
          icon: const Icon(Icons.arrow_drop_down),
          items: const [
            DropdownMenuItem(value: 'male', child: Text('男')),
            DropdownMenuItem(value: 'female', child: Text('女')),
          ],
          onChanged: (val) => setState(() => _gender = val!),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _ageController.dispose();
    _heightController.dispose();
    _initialWeightController.dispose();
    _targetWeightController.dispose();
    _calorieGoalController.dispose();
    super.dispose();
  }
}
