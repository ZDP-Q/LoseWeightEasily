import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/food.dart';
import '../models/user.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000'; // Android Emulator default

  Future<List<FoodSearchResult>> searchFood(String query) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/search?query=${Uri.encodeComponent(query)}'),
      );
      
      if (response.statusCode == 200) {
        List data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((json) => FoodSearchResult.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      throw Exception('网络连接失败: $e');
    }
  }

  Future<Map<String, dynamic>> calculateBmr(double weight, double height, int age, String gender) async {
    final response = await http.post(
      Uri.parse('$baseUrl/calculate/bmr'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'weight_kg': weight,
        'height_cm': height,
        'age': age,
        'gender': gender,
      }),
    );
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception('计算失败');
  }

  Future<List<dynamic>> getWeightHistory({int limit = 100}) async {
    final response = await http.get(Uri.parse('$baseUrl/weight?limit=$limit'));
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception('获取体重历史失败');
  }

  Future<Map<String, dynamic>> addWeight(double weight, String? notes) async {
    final response = await http.post(
      Uri.parse('$baseUrl/weight'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'weight_kg': weight,
        'notes': notes,
      }),
    );
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception('记录体重失败');
  }

  Future<Map<String, dynamic>> generateMealPlan({
    required List<String> ingredients,
    String? preferences,
    String? restrictions,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/meal-plan'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'ingredients': ingredients,
        'preferences': preferences,
        'dietary_restrictions': restrictions,
      }),
    );
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception('生成食谱失败');
  }

  Future<UserProfile?> getUser() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/user'));
      if (response.statusCode == 200) {
        return UserProfile.fromJson(json.decode(utf8.decode(response.bodyBytes)));
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<UserProfile> createUser(UserProfile user) async {
    final response = await http.post(
      Uri.parse('$baseUrl/user'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(user.toJson()),
    );
    if (response.statusCode == 200) {
      return UserProfile.fromJson(json.decode(utf8.decode(response.bodyBytes)));
    }
    throw Exception('创建用户信息失败');
  }

  Future<UserProfile> updateUser(UserProfile user) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/user'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(user.toJson()),
    );
    if (response.statusCode == 200) {
      return UserProfile.fromJson(json.decode(utf8.decode(response.bodyBytes)));
    }
    throw Exception('更新用户信息失败');
  }
}
