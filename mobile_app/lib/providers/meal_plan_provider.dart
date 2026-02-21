import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class MealPlanProvider extends ChangeNotifier {
  final ApiService _api;

  bool _isLoading = false;
  String? _error;
  Map<String, dynamic>? _mealPlan;
  List<String> _ingredients = [];
  String _preferences = '';
  String _restrictions = '';

  MealPlanProvider(this._api);

  bool get isLoading => _isLoading;
  String? get error => _error;
  Map<String, dynamic>? get mealPlan => _mealPlan;
  List<String> get ingredients => _ingredients;
  String get preferences => _preferences;
  String get restrictions => _restrictions;
  bool get hasPlan => _mealPlan != null;

  void updateInputs({
    List<String>? ingredients,
    String? preferences,
    String? restrictions,
  }) {
    if (ingredients != null) _ingredients = ingredients;
    if (preferences != null) _preferences = preferences;
    if (restrictions != null) _restrictions = restrictions;
    notifyListeners();
  }

  void addIngredient(String ingredient) {
    if (ingredient.trim().isEmpty) return;
    if (!_ingredients.contains(ingredient.trim())) {
      _ingredients.add(ingredient.trim());
      notifyListeners();
    }
  }

  void removeIngredient(String ingredient) {
    _ingredients.remove(ingredient);
    notifyListeners();
  }

  void reset() {
    _ingredients = [];
    _preferences = '';
    _restrictions = '';
    _mealPlan = null;
    _error = null;
    notifyListeners();
  }

  Future<void> generatePlan({double? calorieGoal}) async {
    if (_ingredients.isEmpty) {
      _error = '请至少添加一种食材';
      notifyListeners();
      return;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // 检查是否有查询意图（例如只有一个“食材”且包含疑问词）
      final isQuestion = _ingredients.length == 1 && 
          (const ['多少', '热量', '卡路里', 'kcal', '是什么', '怎么', '如何'].any((kw) => _ingredients.first.contains(kw)));

      if (isQuestion) {
        // 如果是问题，调用聊天接口
        final reply = await _api.chatWithCoach(_ingredients.first);
        _mealPlan = {
          'plan': '### 🔍 咨询结果\n\n$reply\n\n*提示：如果您想生成食谱，请清除当前输入并仅填入食材名称（如：鸡胸肉、西兰花）。*'
        };
      } else {
        // 否则，正常生成食谱
        final result = await _api.generateMealPlan(
          ingredients: _ingredients,
          preferences: _preferences,
          restrictions: _restrictions,
          calorieGoal: calorieGoal,
        );

        // 将结构化的结果转换为 Markdown 格式
        final StringBuffer md = StringBuffer();
        md.writeln('### 📅 今日减脂餐计划');
        md.writeln('\n**每日目标**: ${result['daily_summary']['target_calories']} kcal');
        md.writeln('| 蛋白质 | 碳水 | 脂肪 |');
        md.writeln('| :--- | :--- | :--- |');
        md.writeln('| ${result['daily_summary']['total_protein']} | ${result['daily_summary']['total_carbs']} | ${result['daily_summary']['total_fat']} |\n');

        md.writeln('#### 🍽️ 三餐安排');
        final meals = result['meals'] as Map<String, dynamic>;
        meals.forEach((key, meal) {
          final mealName = key == 'breakfast' ? '早餐' : key == 'lunch' ? '午餐' : '晚餐';
          md.writeln('\n**$mealName: ${meal['name']}** (${meal['calories']} kcal)');
          md.writeln('- **食材**: ${ (meal['ingredients_used'] as List).join('、') }');
          md.writeln('- **做法**: ${meal['instructions']}');
        });

        if (result['tips'] != null && (result['tips'] as List).isNotEmpty) {
          md.writeln('\n#### 💡 营养建议');
          for (var tip in (result['tips'] as List)) {
            md.writeln('- $tip');
          }
        }

        _mealPlan = {'plan': md.toString()};
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
