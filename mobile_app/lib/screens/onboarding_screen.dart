import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/auth_provider.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  int _currentStep = 0;
  
  // Controllers for text input
  final TextEditingController _ageController = TextEditingController(text: '25');
  final TextEditingController _heightController = TextEditingController(text: '170');
  final TextEditingController _weightController = TextEditingController(text: '70');
  final TextEditingController _targetWeightController = TextEditingController(text: '65');

  // Data to collect
  String _gender = 'male';
  String _activityLevel = 'sedentary';

  final List<Map<String, String>> _activities = [
    {'value': 'sedentary', 'label': '久坐', 'desc': '极少锻炼（办公室人群）'},
    {'value': 'light', 'label': '轻度', 'desc': '每周锻炼 1-3 次'},
    {'value': 'moderate', 'label': '中度', 'desc': '每周锻炼 3-5 次'},
    {'value': 'active', 'label': '活跃', 'desc': '每天锻炼或重体力劳动'},
  ];

  bool _isSubmitting = false;

  @override
  void dispose() {
    _ageController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    _targetWeightController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => _isSubmitting = true);
    try {
      final int age = int.tryParse(_ageController.text) ?? 25;
      final double height = double.tryParse(_heightController.text) ?? 170.0;
      final double weight = double.tryParse(_weightController.text) ?? 70.0;
      final double targetWeight = double.tryParse(_targetWeightController.text) ?? 65.0;

      await ApiService().updateProfile(
        age: age,
        gender: _gender,
        height: height,
        initialWeight: weight,
        targetWeight: targetWeight,
        activityLevel: _activityLevel,
      );
      
      if (!mounted) return;
      
      // 显示成功
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('资料初始化成功！小松已为您制定目标。')),
      );
      
      // 关键修复：通知 AuthProvider 刷新用户信息，RootNavigator 会自动切换到 MainScreen
      final auth = Provider.of<AuthProvider>(context, listen: false);
      await auth.checkAuth();
      
      if (mounted) {
        if (!auth.needsOnboarding) {
          // 成功刷新且不再需要引导，RootNavigator 会自动处理。
          // 不再手动调用 pushReplacementNamed('/home')，避免路由未定义的错误。
        } else {
          // 如果 checkAuth 依然觉得需要引导（可能后端没存上），
          // 我们这里弹窗提示并报错。
          throw Exception('资料已提交但状态未刷新，请重新尝试。');
        }
      }
      
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('初始化失败: $e')),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('完善身体资料'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Colors.black,
      ),
      body: Column(
        children: [
          LinearProgressIndicator(
            value: (_currentStep + 1) / 4,
            backgroundColor: Colors.grey.shade200,
            color: Colors.green,
          ),
          Expanded(
            child: GestureDetector(
              onTap: () => FocusScope.of(context).unfocus(),
              child: _buildStepContent(),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (_currentStep > 0)
                  TextButton(
                    onPressed: () => setState(() => _currentStep--),
                    child: const Text('上一步'),
                  )
                else
                  const SizedBox(),
                
                SizedBox(
                  width: 120,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _isSubmitting ? null : () {
                      if (_currentStep < 3) {
                        setState(() => _currentStep++);
                      } else {
                        _submit();
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: _isSubmitting 
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : Text(_currentStep < 3 ? '下一步' : '开启计划'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepContent() {
    switch (_currentStep) {
      case 0: return _buildGenderAndAge();
      case 1: return _buildHeightWeight();
      case 2: return _buildActivityLevel();
      case 3: return _buildTarget();
      default: return const SizedBox();
    }
  }

  Widget _buildGenderAndAge() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('您的性别是？', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          Row(
            children: [
              _genderCard('male', Icons.male, '男性'),
              const SizedBox(width: 16),
              _genderCard('female', Icons.female, '女性'),
            ],
          ),
          const SizedBox(height: 48),
          const Text('您的年龄？', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          _inputField(_ageController, '年龄', '岁', 2),
        ],
      ).animate().fadeIn(duration: 400.ms).slideX(begin: 0.1, end: 0),
    );
  }

  Widget _genderCard(String value, IconData icon, String label) {
    bool isSelected = _gender == value;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _gender = value),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 24),
          decoration: BoxDecoration(
            color: isSelected ? Colors.green.shade50 : Colors.white,
            border: Border.all(color: isSelected ? Colors.green : Colors.grey.shade300, width: 2),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: [
              Icon(icon, size: 48, color: isSelected ? Colors.green : Colors.grey),
              const SizedBox(height: 8),
              Text(label, style: TextStyle(fontWeight: FontWeight.bold, color: isSelected ? Colors.green : Colors.black54)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeightWeight() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('身型数据', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 32),
          const Text('身高 (cm)', style: TextStyle(fontSize: 16, color: Colors.grey)),
          const SizedBox(height: 8),
          _inputField(_heightController, '身高', 'cm', 3, isDecimal: true),
          const SizedBox(height: 32),
          const Text('当前体重 (kg)', style: TextStyle(fontSize: 16, color: Colors.grey)),
          const SizedBox(height: 8),
          _inputField(_weightController, '体重', 'kg', 3, isDecimal: true),
        ],
      ).animate().fadeIn().slideX(begin: 0.1),
    );
  }

  Widget _inputField(TextEditingController controller, String hint, String unit, int maxLength, {bool isDecimal = false}) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              keyboardType: TextInputType.numberWithOptions(decimal: isDecimal),
              inputFormatters: [
                if (!isDecimal) FilteringTextInputFormatter.digitsOnly,
                if (isDecimal) FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*')),
                LengthLimitingTextInputFormatter(5),
              ],
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.green),
              decoration: InputDecoration(
                hintText: hint,
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ),
          Text(unit, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildActivityLevel() {
    return ListView.separated(
      padding: const EdgeInsets.all(24),
      itemCount: _activities.length,
      separatorBuilder: (_, _) => const SizedBox(height: 16),
      itemBuilder: (context, index) {
        final activity = _activities[index];
        bool isSelected = _activityLevel == activity['value'];
        return InkWell(
          onTap: () => setState(() => _activityLevel = activity['value']!),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              border: Border.all(color: isSelected ? Colors.green : Colors.grey.shade300, width: 2),
              borderRadius: BorderRadius.circular(12),
              color: isSelected ? Colors.green.shade50 : null,
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(activity['label']!, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      Text(activity['desc']!, style: TextStyle(color: Colors.grey.shade600)),
                    ],
                  ),
                ),
                if (isSelected) const Icon(Icons.check_circle, color: Colors.green),
              ],
            ),
          ),
        );
      },
    ).animate().fadeIn().slideX(begin: 0.1);
  }

  Widget _buildTarget() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.flag, size: 80, color: Colors.green),
            const SizedBox(height: 24),
            const Text('设定目标体重', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 48),
            _inputField(_targetWeightController, '目标', 'kg', 3, isDecimal: true),
            const SizedBox(height: 32),
            ListenableBuilder(
              listenable: _targetWeightController,
              builder: (context, _) {
                final weight = double.tryParse(_weightController.text) ?? 0;
                final target = double.tryParse(_targetWeightController.text) ?? 0;
                final diff = weight - target;
                return Text(
                  '预计减重: ${diff.toStringAsFixed(1)} kg',
                  style: TextStyle(
                    color: diff > 0 ? Colors.orange : Colors.grey,
                    fontWeight: FontWeight.bold, 
                    fontSize: 18
                  ),
                );
              },
            ),
          ],
        ).animate().fadeIn().scale(),
      ),
    );
  }
}
