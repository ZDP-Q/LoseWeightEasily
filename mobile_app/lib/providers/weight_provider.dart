import 'package:flutter/foundation.dart';
import '../models/weight_record.dart';
import '../services/api_service.dart';

class WeightProvider extends ChangeNotifier {
  final ApiService _api;

  List<WeightRecord> _records = [];
  bool _isLoading = false;
  String? _error;

  WeightProvider(this._api);

  List<WeightRecord> get records => _records;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasRecords => _records.isNotEmpty;

  WeightRecord? get latestRecord => _records.isNotEmpty ? _records.first : null;
  double? get latestWeight => latestRecord?.weightKg;

  /// 计算与初始体重的变化量（需要传入初始体重）
  double? weightChange(double? initialWeight) {
    if (latestWeight == null || initialWeight == null) return null;
    return latestWeight! - initialWeight;
  }

  Future<void> loadHistory() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      _records = await _api.getWeightHistory();
    } catch (e) {
      _error = '加载体重记录失败: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addRecord(double weightKg, {String? notes}) async {
    try {
      await _api.addWeight(weightKg, notes);
      await loadHistory();
    } catch (e) {
      _error = '记录体重失败: $e';
      notifyListeners();
      rethrow;
    }
  }

  Future<void> updateRecord(int id, double? weight, String? notes) async {
    try {
      await _api.updateWeight(id, weight, notes);
      await loadHistory();
    } catch (e) {
      _error = '更新失败: $e';
      notifyListeners();
      rethrow;
    }
  }

  Future<void> deleteRecord(int id) async {
    try {
      await _api.deleteWeight(id);
      await loadHistory();
    } catch (e) {
      _error = '删除失败: $e';
      notifyListeners();
      rethrow;
    }
  }
}
