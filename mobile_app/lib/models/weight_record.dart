class WeightRecord {
  final int id;
  final double weightKg;
  final DateTime recordedAt;
  final String? notes;

  WeightRecord({
    required this.id,
    required this.weightKg,
    required this.recordedAt,
    this.notes,
  });

  factory WeightRecord.fromJson(Map<String, dynamic> json) {
    return WeightRecord(
      id: json['id'],
      weightKg: (json['weight_kg'] as num).toDouble(),
      recordedAt: DateTime.parse(json['recorded_at']),
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'weight_kg': weightKg,
      'notes': notes,
    };
  }
}
