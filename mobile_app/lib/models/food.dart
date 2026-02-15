class FoodSearchResult {
  final int fdcId;
  final String description;
  final String? category;
  final double? caloriesPer100g;
  final double similarity;

  FoodSearchResult({
    required this.fdcId,
    required this.description,
    this.category,
    this.caloriesPer100g,
    required this.similarity,
  });

  factory FoodSearchResult.fromJson(Map<String, dynamic> json) {
    return FoodSearchResult(
      fdcId: json['fdc_id'],
      description: json['description'],
      category: json['category'],
      caloriesPer100g: json['calories_per_100g']?.toDouble(),
      similarity: json['similarity'].toDouble(),
    );
  }
}
