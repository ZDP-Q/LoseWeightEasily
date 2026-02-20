import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

/// 认证状态提供者
/// 
/// 管理用户的 API Key 持久化存储，并控制登录状态
class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  static const String _tokenKey = 'auth_token';
  
  String? _token;
  bool _isLoading = true;

  AuthProvider(this._apiService) {
    _loadToken();
  }

  String? get token => _token;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;

  /// 从本地存储加载 Token
  Future<void> _loadToken() async {
    _isLoading = true;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString(_tokenKey);
      if (_token != null) {
        _apiService.setToken(_token);
      }
    } catch (e) {
      debugPrint('加载 Token 失败: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 登录/更新 Token
  Future<bool> login(String token) async {
    if (token.isEmpty) return false;

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey, token);
      
      _token = token;
      _apiService.setToken(token);
      
      // 验证 Token 是否有效 (尝试获取用户信息)
      final user = await _apiService.getUser();
      if (user == null) {
        // 如果用户不存在，跳转到创建流程（此逻辑由 UI 处理）
        notifyListeners();
        return true;
      }
      
      notifyListeners();
      return true;
    } catch (e) {
      debugPrint('登录验证失败: $e');
      // 如果报错是因为 401/403，则认为登录失败
      return false;
    }
  }

  /// 退出登录
  Future<void> logout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_tokenKey);
      
      _token = null;
      _apiService.setToken(null);
      notifyListeners();
    } catch (e) {
      debugPrint('退出登录失败: $e');
    }
  }
}
