/// BMR（基础代谢率）本地计算器
///
/// 使用 Harris-Benedict 修订公式，无需网络请求。
class BmrCalculator {
  /// 计算 BMR（基础代谢率）
  ///
  /// [weight] 体重 (kg)
  /// [height] 身高 (cm)
  /// [age] 年龄
  /// [gender] 性别 ("male" / "female")
  static double calculateBmr({
    required double weight,
    required double height,
    required int age,
    required String gender,
  }) {
    if (gender.toLowerCase() == 'male') {
      return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
    } else {
      return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
    }
  }

  /// TDEE 活动因子
  static const Map<String, double> activityFactors = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
  };

  /// 计算指定活动强度的 TDEE
  static double calculateTdee(double bmr, String activityLevel) {
    return bmr * (activityFactors[activityLevel] ?? 1.2);
  }

  /// 计算所有活动强度的 TDEE
  static Map<String, double> getAllTdeeLevels(double bmr) {
    return {
      for (final entry in activityFactors.entries)
        entry.key: bmr * entry.value,
    };
  }
}
