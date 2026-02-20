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

class ChatProvider extends ChangeNotifier {
  final ApiService _apiService;
  List<ChatMessage> _messages = [];
  bool _isLoading = false;
  final _uuid = const Uuid();

  ChatProvider(this._apiService);

  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;

  Future<void> loadHistory() async {
    if (_messages.isNotEmpty) return; // Already loaded

    _isLoading = true;
    notifyListeners();

    try {
      final history = await _apiService.getChatHistory();
      _messages = history.map((m) => ChatMessage.fromJson(m)).toList();
    } catch (e) {
      debugPrint('Error loading chat history: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void addUserMessage(String text) {
    _messages.add(ChatMessage(
      id: _uuid.v4(),
      text: text, 
      isUser: true, 
      timestamp: DateTime.now()
    ));
    notifyListeners();
  }

  void addSystemMessage(String text) {
    _messages.add(ChatMessage(
      id: _uuid.v4(),
      text: text, 
      isUser: false, 
      timestamp: DateTime.now()
    ));
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
     final last = _messages.last;
     _messages[_messages.length - 1] = ChatMessage(
       id: last.id,
       text: last.text + text,
       isUser: last.isUser,
       isStreaming: isStreaming,
       timestamp: last.timestamp,
     );
     notifyListeners();
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
