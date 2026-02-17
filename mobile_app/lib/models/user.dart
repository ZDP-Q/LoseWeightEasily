class UserProfile {
  final int? id;
  final String name;
  final int age;
  final String gender; // "male" or "female"
  final double heightCm;
  final double initialWeightKg;
  final double targetWeightKg;
  final String activityLevel;
  final double? bmr;
  final double? tdee;
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
    this.activityLevel = 'sedentary',
    this.bmr,
    this.tdee,
    this.dailyCalorieGoal,
    this.createdAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      name: json['name'] ?? '',
      age: json['age'] ?? 0,
      gender: (json['gender'] as String? ?? 'male').toLowerCase(),
      heightCm: (json['height_cm'] as num? ?? 0).toDouble(),
      initialWeightKg: (json['initial_weight_kg'] as num? ?? 0).toDouble(),
      targetWeightKg: (json['target_weight_kg'] as num? ?? 0).toDouble(),
      activityLevel: json['activity_level'] as String? ?? 'sedentary',
      bmr: (json['bmr'] as num?)?.toDouble(),
      tdee: (json['tdee'] as num?)?.toDouble(),
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
      'activity_level': activityLevel,
      'bmr': bmr,
      'tdee': tdee,
      'daily_calorie_goal': dailyCalorieGoal,
    };
  }

  UserProfile copyWith({
    int? id,
    String? name,
    int? age,
    String? gender,
    double? heightCm,
    double? initialWeightKg,
    double? targetWeightKg,
    String? activityLevel,
    double? bmr,
    double? tdee,
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
      activityLevel: activityLevel ?? this.activityLevel,
      bmr: bmr ?? this.bmr,
      tdee: tdee ?? this.tdee,
      dailyCalorieGoal: dailyCalorieGoal ?? this.dailyCalorieGoal,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
