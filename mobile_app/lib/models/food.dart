class FoodSearchResult {
  final int fdcId;
  final String description;
  final String? category;
  final double? caloriesPer100g;
  final double? proteinPer100g;
  final double? fatPer100g;
  final double? carbsPer100g;
  final double similarity;

  FoodSearchResult({
    required this.fdcId,
    required this.description,
    this.category,
    this.caloriesPer100g,
    this.proteinPer100g,
    this.fatPer100g,
    this.carbsPer100g,
    required this.similarity,
  });

  factory FoodSearchResult.fromJson(Map<String, dynamic> json) {
    return FoodSearchResult(
      fdcId: json['fdc_id'],
      description: json['description'],
      category: json['food_category'], // 修正后端字段名映射
      caloriesPer100g: json['calories_per_100g']?.toDouble(),
      proteinPer100g: json['protein_per_100g']?.toDouble(),
      fatPer100g: json['fat_per_100g']?.toDouble(),
      carbsPer100g: json['carbs_per_100g']?.toDouble(),
      similarity: (json['similarity'] ?? 0.0).toDouble(),
    );
  }
}
