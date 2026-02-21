import 'package:flutter/foundation.dart';
import '../models/food.dart';
import '../services/api_service.dart';

class SearchProvider extends ChangeNotifier {
  final ApiService _api;

  List<FoodSearchResult> _results = [];
  bool _isSearching = false;
  String? _error;
  String _lastQuery = '';

  SearchProvider(this._api);

  List<FoodSearchResult> get results => _results;
  bool get isSearching => _isSearching;
  String? get error => _error;
  String get lastQuery => _lastQuery;
  bool get hasResults => _results.isNotEmpty;

  Future<void> searchFood(String query) async {
    if (query.trim().isEmpty) return;
    _lastQuery = query.trim();
    _isSearching = true;
    _error = null;
    notifyListeners();
    try {
      _results = await _api.searchFood(_lastQuery);
    } catch (e) {
      _error = '搜索失败: $e';
    } finally {
      _isSearching = false;
      notifyListeners();
    }
  }

  void clearResults() {
    _results = [];
    _lastQuery = '';
    _error = null;
    notifyListeners();
  }

  void reset() {
    _results = [];
    _isSearching = false;
    _error = null;
    _lastQuery = '';
    notifyListeners();
  }
}
