import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/api_service.dart';

class UserProvider extends ChangeNotifier {
  final ApiService _api;

  UserProfile? _user;
  bool _isLoading = false;
  String? _error;

  UserProvider(this._api);

  UserProfile? get user => _user;
  bool get isLoading => _isLoading;
  bool get hasUser => _user != null;
  String? get error => _error;

  void reset() {
    _user = null;
    _isLoading = false;
    _error = null;
    notifyListeners();
  }

  String get displayName => _user?.username ?? '新用户';
  double? get bmr => _user?.bmr;
  double? get tdee => _user?.tdee;
  double? get dailyCalorieGoal => _user?.dailyCalorieGoal;
  double? get targetWeight => _user?.targetWeightKg;
  double? get initialWeight => _user?.initialWeightKg;

  Future<void> loadUser() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      _user = await _api.getMe();
    } catch (e) {
      _error = '加载用户信息失败: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateProfile({
    int? age,
    String? gender,
    double? height,
    double? initialWeight,
    double? targetWeight,
    String? activityLevel,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      _user = await _api.updateProfile(
        age: age,
        gender: gender,
        height: height,
        initialWeight: initialWeight,
        targetWeight: targetWeight,
        activityLevel: activityLevel,
      );
    } catch (e) {
      _error = '更新个人资料失败: $e';
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
