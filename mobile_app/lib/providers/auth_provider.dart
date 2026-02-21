import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/user.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  
  bool _isLoading = true;
  bool _isAuthenticated = false;
  bool _needsOnboarding = false;
  UserProfile? _user;

  AuthProvider(this._apiService) {
    _initialize();
  }

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  bool get needsOnboarding => _needsOnboarding;
  UserProfile? get user => _user;

  Future<void> _initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      // ApiService 已经在 main() 中初始化过，这里只需检查状态
      if (_apiService.isAuthenticated) {
        await checkAuth();
      }
    } catch (e) {
      debugPrint('Auth initialization error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> checkAuth() async {
    try {
      _user = await _apiService.getMe();
      _isAuthenticated = true;
      // 如果身高为空，说明资料未初始化，需要引导
      _needsOnboarding = (_user?.heightCm == null || _user?.heightCm == 0);
    } catch (e) {
      // 只有在明确是 401 未授权时才重置状态
      debugPrint('Check auth error: $e');
      if (e.toString().contains('401') || e.toString().contains('获取用户信息失败')) {
        _isAuthenticated = false;
        _user = null;
        await _apiService.logout();
      }
      // 其他错误（如网络超时）暂不登出用户，保持当前状态
    }
    notifyListeners();
  }

  Future<void> login(String username, String password) async {
    await _apiService.login(username, password);
    await checkAuth();
  }

  Future<void> register(String username, String password) async {
    await _apiService.register(username, password);
    // 注册后通常需要自动登录，或者让用户手动登录
    // 这里我们保持 register 逻辑纯粹，具体的自动登录由 Screen 层调用 login 处理
  }

  Future<void> logout() async {
    await _apiService.logout();
    _isAuthenticated = false;
    _user = null;
    notifyListeners();
  }
}
