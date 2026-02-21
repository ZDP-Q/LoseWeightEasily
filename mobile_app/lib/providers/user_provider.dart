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

  String get displayName => _user?.name ?? '新用户';
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
      _user = await _api.getUser();
    } catch (e) {
      _error = '加载用户信息失败: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> createUser(UserProfile profile) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      _user = await _api.createUser(profile);
    } catch (e) {
      _error = '创建用户失败: $e';
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateUser(UserProfile profile) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      _user = await _api.updateUser(profile);
    } catch (e) {
      _error = '更新用户失败: $e';
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
