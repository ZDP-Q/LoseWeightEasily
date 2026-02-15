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

  void clearInputs() {
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
      final result = await _api.generateMealPlan(
        ingredients: _ingredients,
        preferences: _preferences,
        restrictions: _restrictions,
        calorieGoal: calorieGoal,
      );
      _mealPlan = result;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
