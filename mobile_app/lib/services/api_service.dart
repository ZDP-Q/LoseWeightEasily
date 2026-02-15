import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/food.dart';
import '../models/user.dart';
import '../models/weight_record.dart';

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );
  static const Duration _timeout = Duration(seconds: 10);

  static const String apiKey = String.fromEnvironment('API_KEY');

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (apiKey.isNotEmpty) 'X-API-Key': apiKey,
      };

  // ---------------------------------------------------------------------------
  // Food Search
  // ---------------------------------------------------------------------------
  Future<List<FoodSearchResult>> searchFood(String query) async {
    try {
      final response = await http
          .get(
            Uri.parse('$baseUrl/search?query=${Uri.encodeComponent(query)}'),
            headers: _headers,
          )
          .timeout(_timeout);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((j) => FoodSearchResult.fromJson(j)).toList();
      }
      throw ApiException('搜索失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  // ---------------------------------------------------------------------------
  // BMR Calculation
  // ---------------------------------------------------------------------------
  Future<Map<String, dynamic>> calculateBmr(
      double weight, double height, int age, String gender) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/calculate/bmr'),
            headers: _headers,
            body: json.encode({
              'weight_kg': weight,
              'height_cm': height,
              'age': age,
              'gender': gender,
            }),
          )
          .timeout(_timeout);
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      }
      throw ApiException('计算失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  // ---------------------------------------------------------------------------
  // Weight Records
  // ---------------------------------------------------------------------------
  Future<List<WeightRecord>> getWeightHistory({int limit = 100}) async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/weight?limit=$limit'), headers: _headers)
          .timeout(_timeout);
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((j) => WeightRecord.fromJson(j)).toList();
      }
      throw ApiException('获取体重历史失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  Future<WeightRecord> addWeight(double weight, String? notes) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/weight'),
            headers: _headers,
            body: json.encode({
              'weight_kg': weight,
              'notes': notes ?? '',
            }),
          )
          .timeout(_timeout);
      if (response.statusCode == 200) {
        return WeightRecord.fromJson(
            json.decode(utf8.decode(response.bodyBytes)));
      }
      throw ApiException('记录体重失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  Future<WeightRecord> updateWeight(int id, double? weight, String? notes) async {
    try {
      final Map<String, dynamic> data = {};
      if (weight != null) data['weight_kg'] = weight;
      if (notes != null) data['notes'] = notes;

      final response = await http
          .patch(
            Uri.parse('$baseUrl/weight/$id'),
            headers: _headers,
            body: json.encode(data),
          )
          .timeout(_timeout);
      if (response.statusCode == 200) {
        return WeightRecord.fromJson(
            json.decode(utf8.decode(response.bodyBytes)));
      }
      throw ApiException('更新失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  Future<void> deleteWeight(int id) async {
    try {
      final response = await http
          .delete(
            Uri.parse('$baseUrl/weight/$id'),
            headers: _headers,
          )
          .timeout(_timeout);
      if (response.statusCode == 200) return;
      throw ApiException('删除失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  // ---------------------------------------------------------------------------
  // Meal Plan
  // ---------------------------------------------------------------------------
  Future<Map<String, dynamic>> generateMealPlan({
    required List<String> ingredients,
    String? preferences,
    String? restrictions,
    double? calorieGoal,
  }) async {
    try {
      // 构建偏好字符串，将热量目标整合进去
      String fullPreferences = preferences ?? '';
      if (calorieGoal != null) {
        final calorieInfo = '每日热量目标: ${calorieGoal.toStringAsFixed(0)} kcal';
        fullPreferences =
            fullPreferences.isEmpty ? calorieInfo : '$fullPreferences, $calorieInfo';
      }

      final response = await http
          .post(
            Uri.parse('$baseUrl/meal-plan'),
            headers: _headers,
            body: json.encode({
              'ingredients': ingredients,
              'preferences': fullPreferences,
              'dietary_restrictions': restrictions ?? '',
            }),
          )
          .timeout(const Duration(seconds: 60)); // AI 生成需要更长超时
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      }
      throw ApiException('生成食谱失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('AI 生成超时，请稍后再试');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  // ---------------------------------------------------------------------------
  // User
  // ---------------------------------------------------------------------------
  Future<UserProfile?> getUser() async {
    try {
      final response =
          await http.get(Uri.parse('$baseUrl/user'), headers: _headers).timeout(_timeout);
      if (response.statusCode == 200) {
        return UserProfile.fromJson(
            json.decode(utf8.decode(response.bodyBytes)));
      }
      return null; // 404 = 用户不存在
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  Future<UserProfile> createUser(UserProfile user) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/user'),
            headers: _headers,
            body: json.encode(user.toJson()),
          )
          .timeout(_timeout);
      if (response.statusCode == 200) {
        return UserProfile.fromJson(
            json.decode(utf8.decode(response.bodyBytes)));
      }
      throw ApiException('创建用户信息失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  Future<UserProfile> updateUser(UserProfile user) async {
    try {
      final response = await http
          .patch(
            Uri.parse('$baseUrl/user'),
            headers: _headers,
            body: json.encode(user.toJson()),
          )
          .timeout(_timeout);
      if (response.statusCode == 200) {
        return UserProfile.fromJson(
            json.decode(utf8.decode(response.bodyBytes)));
      }
      throw ApiException('更新用户信息失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('请求超时，请检查网络连接');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }
}

/// 统一的 API 异常类
class ApiException implements Exception {
  final String message;
  const ApiException(this.message);

  @override
  String toString() => message;
}
