class UserProfile {
  final int? id;
  final String name;
  final int age;
  final String gender;
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
      gender: json['gender'],
      heightCm: json['height_cm'].toDouble(),
      initialWeightKg: json['initial_weight_kg'].toDouble(),
      targetWeightKg: json['target_weight_kg'].toDouble(),
      bmr: json['bmr']?.toDouble(),
      dailyCalorieGoal: json['daily_calorie_goal']?.toDouble(),
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
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
}
