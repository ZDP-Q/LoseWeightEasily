import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mobile_app/main.dart';
import 'package:mobile_app/services/api_service.dart';
import 'package:mobile_app/providers/navigation_provider.dart';
import 'package:mobile_app/providers/search_provider.dart';
import 'package:mobile_app/providers/user_provider.dart';
import 'package:mobile_app/providers/weight_provider.dart';
import 'package:mobile_app/providers/meal_plan_provider.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider(create: (_) => ApiService()),
          ChangeNotifierProvider(create: (_) => NavigationProvider()),
          ChangeNotifierProxyProvider<ApiService, UserProvider>(
            create: (ctx) => UserProvider(ctx.read<ApiService>()),
            update: (_, api, prev) => prev ?? UserProvider(api),
          ),
          ChangeNotifierProxyProvider<ApiService, WeightProvider>(
            create: (ctx) => WeightProvider(ctx.read<ApiService>()),
            update: (_, api, prev) => prev ?? WeightProvider(api),
          ),
          ChangeNotifierProxyProvider<ApiService, SearchProvider>(
            create: (ctx) => SearchProvider(ctx.read<ApiService>()),
            update: (_, api, prev) => prev ?? SearchProvider(api),
          ),
          ChangeNotifierProxyProvider<ApiService, MealPlanProvider>(
            create: (ctx) => MealPlanProvider(ctx.read<ApiService>()),
            update: (_, api, prev) => prev ?? MealPlanProvider(api),
          ),
        ],
        child: const XiaoSongApp(),
      ),
    );

    // Wait for animations to settle
    await tester.pumpAndSettle();

    // Verify that the app starts
    expect(find.byType(XiaoSongApp), findsOneWidget);
  });
}
