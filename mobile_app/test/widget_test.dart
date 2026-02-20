import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());

    // Wait for animations to settle
    await tester.pumpAndSettle();

    // Verify that the app starts by checking for the MyApp widget
    expect(find.byType(MyApp), findsOneWidget);
  });
}
