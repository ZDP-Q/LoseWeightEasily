import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../services/api_service.dart';

class ChatMessage {
  final String id;
  final String text;
  final bool isUser;
  final bool isStreaming;
  final DateTime? timestamp;

  ChatMessage({
    required this.id,
    required this.text,
    required this.isUser,
    this.isStreaming = false,
    this.timestamp,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id']?.toString() ?? const Uuid().v4(),
      text: json['content'],
      isUser: json['role'] == 'user',
      timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp']) : null,
    );
  }
}

class ChatEvent {
  final String type;
  final dynamic data;

  ChatEvent({required this.type, this.data});
}

class ChatProvider extends ChangeNotifier {
  final ApiService _apiService;
  List<ChatMessage> _messages = [];
  bool _isLoading = false;
  final _uuid = const Uuid();
  static const int _maxMessages = 120;
  static const int _historyFetchLimit = 50;
  static const Duration _streamFlushInterval = Duration(milliseconds: 120);
  static const int _streamFlushChars = 96;

  // Ingredient Mode State
  bool _isIngredientMode = false;
  final List<String> _selectedIngredients = [];

  // Stream for UI events (snackbars, etc.)
  final _eventController = StreamController<ChatEvent>.broadcast();
  Stream<ChatEvent> get events => _eventController.stream;

  ChatProvider(this._apiService);

  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  bool get isIngredientMode => _isIngredientMode;
  List<String> get selectedIngredients => List.unmodifiable(_selectedIngredients);

  @override
  void dispose() {
    _eventController.close();
    super.dispose();
  }

  void _trimMessages() {
    if (_messages.length <= _maxMessages) return;
    _messages = _messages.sublist(_messages.length - _maxMessages);
  }

  // --- History Loading ---
  Future<void> loadHistory() async {
    if (_messages.isNotEmpty) return;

    _isLoading = true;
    notifyListeners();

    try {
      final history = await _apiService.getChatHistory(limit: _historyFetchLimit);
      _messages = history.map((m) => ChatMessage.fromJson(m)).toList();
      _trimMessages();
    } catch (e) {
      debugPrint('Error loading chat history: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // --- Ingredient Management ---
  void toggleIngredientMode() {
    _isIngredientMode = !_isIngredientMode;
    if (!_isIngredientMode) {
      _selectedIngredients.clear();
    }
    notifyListeners();
  }

  void addIngredient(String name) {
    final trimmed = name.trim();
    if (trimmed.isNotEmpty && !_selectedIngredients.contains(trimmed)) {
      _selectedIngredients.add(trimmed);
      notifyListeners();
    }
  }

  void removeIngredient(int index) {
    if (index >= 0 && index < _selectedIngredients.length) {
      _selectedIngredients.removeAt(index);
      notifyListeners();
    }
  }

  void clearIngredients() {
    _selectedIngredients.clear();
    notifyListeners();
  }

  // --- Messaging ---
  void addUserMessage(String text) {
    _messages.add(ChatMessage(
      id: _uuid.v4(),
      text: text, 
      isUser: true, 
      timestamp: DateTime.now()
    ));
    _trimMessages();
    notifyListeners();
  }

  void addSystemMessage(String text) {
    _messages.add(ChatMessage(
      id: _uuid.v4(),
      text: text, 
      isUser: false, 
      timestamp: DateTime.now()
    ));
    _trimMessages();
    notifyListeners();
  }

  void updateLastMessage(String text, {bool isStreaming = false}) {
    if (_messages.isEmpty) return;
    final last = _messages.last;
    _messages[_messages.length - 1] = ChatMessage(
      id: last.id,
      text: text,
      isUser: last.isUser,
      isStreaming: isStreaming,
      timestamp: last.timestamp,
    );
    notifyListeners();
  }

  void appendToLastMessage(String text, {bool isStreaming = true}) {
     if (_messages.isEmpty) return;
     final lastIdx = _messages.length - 1;
     final last = _messages[lastIdx];
     _messages[lastIdx] = ChatMessage(
       id: last.id,
       text: last.text + text,
       isUser: last.isUser,
       isStreaming: isStreaming,
       timestamp: last.timestamp,
     );
     notifyListeners();
  }

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    addUserMessage(text);
    
    // Add placeholder for AI response
    addSystemMessage('...');
    final aiMessageIndex = _messages.length - 1;
    setStreaming(aiMessageIndex, true);
    
    try {
      final stream = _apiService.chatWithCoachStream(text);
      updateLastMessage('', isStreaming: true);

      final pendingChunk = StringBuffer();
      var lastFlushAt = DateTime.now();

      void flushPending({bool force = false}) {
        if (pendingChunk.isEmpty) return;

        final now = DateTime.now();
        final intervalOk = now.difference(lastFlushAt) >= _streamFlushInterval;
        final charsOk = pendingChunk.length >= _streamFlushChars;

        if (!force && !intervalOk && !charsOk) return;

        appendToLastMessage(pendingChunk.toString(), isStreaming: true);
        pendingChunk.clear();
        lastFlushAt = now;
      }

      await for (final event in stream) {
        if (event.type == 'text') {
          pendingChunk.write(event.text ?? '');
          flushPending();
        } else if (event.type == 'action_result') {
          flushPending(force: true);
          _eventController.add(ChatEvent(type: 'action_result', data: event.data));
        } else if (event.type == 'error') {
          flushPending(force: true);
          appendToLastMessage('\n\n[服务异常: ${event.text ?? '未知错误'}]', isStreaming: false);
          break;
        } else if (event.type == 'done') {
          flushPending(force: true);
          break;
        }
      }
    } catch (e) {
      appendToLastMessage('\n\n[连接中断: $e]', isStreaming: false);
    } finally {
      setStreaming(aiMessageIndex, false);
    }
  }

  // --- Image Recognition ---
  Future<void> recognizeFood(Uint8List imageBytes) async {
    addSystemMessage('📷 正在分析食物图片...');
    
    try {
      final result = await _apiService.recognizeFood(imageBytes);
      
      final firstRaw = result['raw_data'][0];
      final nutrients = firstRaw['nutrients'] ?? {
        '蛋白质': '待确认',
        '碳水': '待确认',
        '脂肪': '待确认'
      };
      
      // 使用方舟协议 (Ark Protocol) 格式输出，让前端渲染原生卡片
      final protocolMessage = '''我帮你识别出这张图片里的食物啦！
      
```json:food_recognition
{
  "food_name": "${result['final_food_name']}",
  "calories": ${result['final_estimated_calories']},
  "nutrients": {
    "蛋白质": "${nutrients['protein'] ?? nutrients['蛋白质'] ?? '未知'}",
    "碳水": "${nutrients['carbs'] ?? nutrients['碳水'] ?? '未知'}",
    "脂肪": "${nutrients['fat'] ?? nutrients['脂肪'] ?? '未知'}"
  }
}
```''';

      updateLastMessage(protocolMessage, isStreaming: false);
      
      _eventController.add(ChatEvent(type: 'recognition_success', data: result));
    } catch (e) {
      updateLastMessage('❌ 图片识别失败: $e', isStreaming: false);
    }
  }

  void setStreaming(int index, bool isStreaming) {
    if (index < 0 || index >= _messages.length) return;
    final msg = _messages[index];
    _messages[index] = ChatMessage(
      id: msg.id,
      text: msg.text,
      isUser: msg.isUser,
      isStreaming: isStreaming,
      timestamp: msg.timestamp,
    );
    notifyListeners();
  }
}
