class FoodLog {
  final int id;
  final String foodName;
  final double calories;
  final DateTime timestamp;

  FoodLog({
    required this.id,
    required this.foodName,
    required this.calories,
    required this.timestamp,
  });

  factory FoodLog.fromJson(Map<String, dynamic> json) {
    return FoodLog(
      id: json['id'],
      foodName: json['food_name'],
      calories: (json['calories'] as num).toDouble(),
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'food_name': foodName,
      'calories': calories,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}
