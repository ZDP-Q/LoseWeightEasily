class UserProfile {
  final int? id;
  final String name;
  final int age;
  final String gender; // "male" or "female" — 统一使用小写
  final double heightCm;
  final double initialWeightKg;
  final double targetWeightKg;
  final double? bmr;
  final double? dailyCalorieGoal;
  final DateTime? createdAt;

  UserProfile({
    this.id,
    required this.name,
    required this.age,
    required this.gender,
    required this.heightCm,
    required this.initialWeightKg,
    required this.targetWeightKg,
    this.bmr,
    this.dailyCalorieGoal,
    this.createdAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      name: json['name'],
      age: json['age'],
      gender: (json['gender'] as String).toLowerCase(),
      heightCm: (json['height_cm'] as num).toDouble(),
      initialWeightKg: (json['initial_weight_kg'] as num).toDouble(),
      targetWeightKg: (json['target_weight_kg'] as num).toDouble(),
      bmr: (json['bmr'] as num?)?.toDouble(),
      dailyCalorieGoal: (json['daily_calorie_goal'] as num?)?.toDouble(),
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'age': age,
      'gender': gender,
      'height_cm': heightCm,
      'initial_weight_kg': initialWeightKg,
      'target_weight_kg': targetWeightKg,
      'bmr': bmr,
      'daily_calorie_goal': dailyCalorieGoal,
    };
  }

  /// 创建修改后的副本
  UserProfile copyWith({
    int? id,
    String? name,
    int? age,
    String? gender,
    double? heightCm,
    double? initialWeightKg,
    double? targetWeightKg,
    double? bmr,
    double? dailyCalorieGoal,
    DateTime? createdAt,
  }) {
    return UserProfile(
      id: id ?? this.id,
      name: name ?? this.name,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      heightCm: heightCm ?? this.heightCm,
      initialWeightKg: initialWeightKg ?? this.initialWeightKg,
      targetWeightKg: targetWeightKg ?? this.targetWeightKg,
      bmr: bmr ?? this.bmr,
      dailyCalorieGoal: dailyCalorieGoal ?? this.dailyCalorieGoal,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
