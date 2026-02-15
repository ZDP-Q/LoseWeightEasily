import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const LoseWeightEasilyApp());

    // Verify that the app starts (e.g., check for a common tab label)
    expect(find.text('首页'), findsWidgets);
  });
}
