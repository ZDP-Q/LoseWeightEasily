import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'services/api_service.dart';
import 'providers/navigation_provider.dart';
import 'providers/search_provider.dart';
import 'providers/user_provider.dart';
import 'providers/weight_provider.dart';
import 'providers/meal_plan_provider.dart';
import 'screens/main_screen.dart';
import 'utils/theme.dart';

void main() {
  // 确保 Flutter 绑定初始化
  WidgetsFlutterBinding.ensureInitialized();

  // 禁用运行时从 Google 服务器下载字体，防止网络问题导致卡顿
  GoogleFonts.config.allowRuntimeFetching = false;

  runApp(
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
      child: const LoseWeightEasilyApp(),
    ),
  );
}

class LoseWeightEasilyApp extends StatelessWidget {
  const LoseWeightEasilyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LoseWeightEasily',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme(context),
      home: const MainScreen(),
    );
  }
}
