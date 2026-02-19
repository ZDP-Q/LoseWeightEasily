import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/food.dart';
import '../models/user.dart';
import '../models/weight_record.dart';

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://xiaosong.fucku.top',
  );
  static const Duration _timeout = Duration(seconds: 30);

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
            Uri.parse('$baseUrl/food/search?query=${Uri.encodeComponent(query)}'),
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
          .timeout(const Duration(seconds: 120)); // AI 生成需要更长超时
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
  // AI Chat & Food Recognition
  // ---------------------------------------------------------------------------
  Future<String> chatWithCoach(String message) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/chat'),
            headers: _headers,
            body: json.encode({'message': message}),
          )
          .timeout(const Duration(seconds: 30));
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return data['reply'];
      }
      throw ApiException('对话失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('AI 响应超时');
    } on http.ClientException {
      throw ApiException('网络连接失败');
    }
  }

  Stream<ChatStreamEvent> chatWithCoachStream(String message) async* {
    final client = http.Client();
    try {
      final request = http.Request('POST', Uri.parse('$baseUrl/chat/stream'));
      request.headers.addAll(_headers);
      request.body = json.encode({'message': message});

      final response = await client.send(request);

      if (response.statusCode != 200) {
        throw ApiException('连接失败 (${response.statusCode})');
      }

      String buffer = '';
      await for (final chunk in response.stream.transform(utf8.decoder)) {
        buffer += chunk;
        while (buffer.contains('\n\n')) {
          final index = buffer.indexOf('\n\n');
          final eventString = buffer.substring(0, index);
          buffer = buffer.substring(index + 2);
          
          final event = _parseEvent(eventString);
          if (event.type == 'done') return;
          yield event;
        }
      }
      
      // 处理流结束后的残留 buffer
      if (buffer.trim().isNotEmpty) {
        final event = _parseEvent(buffer);
        if (event.type != 'done') yield event;
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('网络错误: $e');
    } finally {
      client.close();
    }
  }

  ChatStreamEvent _parseEvent(String eventString) {
    final lines = eventString.split('\n');
    String eventType = 'text';
    String data = '';

    for (final line in lines) {
      if (line.startsWith('event: ')) {
        eventType = line.substring(7).trim();
      } else if (line.startsWith('data: ')) {
        data = line.substring(6);
      }
    }

    if (eventType == 'action_result') {
      try {
        final jsonData = json.decode(data);
        return ChatStreamEvent(type: 'action_result', data: jsonData);
      } catch (e) {
        return ChatStreamEvent(type: 'text', text: '[解析动作失败]');
      }
    }
    return ChatStreamEvent(type: eventType, text: data);
  }

  Future<Map<String, dynamic>> recognizeFood(List<int> imageBytes) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/food-analysis/recognize'));
      if (apiKey.isNotEmpty) {
        request.headers['X-API-Key'] = apiKey;
      }
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        imageBytes,
        filename: 'food.jpg',
      ));

      final streamedResponse = await request.send().timeout(const Duration(seconds: 120));
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      }
      throw ApiException('识别失败 (${response.statusCode})');
    } on TimeoutException {
      throw ApiException('识别超时，请重试');
    } catch (e) {
      throw ApiException('网络连接或识别出错: $e');
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

class ChatStreamEvent {
  final String type; // 'text', 'action_result', 'error', 'done'
  final String? text;
  final Map<String, dynamic>? data;

  ChatStreamEvent({required this.type, this.text, this.data});
}
