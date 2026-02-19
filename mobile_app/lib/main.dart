import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'services/api_service.dart';
import 'providers/navigation_provider.dart';
import 'providers/search_provider.dart';
import 'providers/user_provider.dart';
import 'providers/weight_provider.dart';
import 'providers/meal_plan_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/food_log_provider.dart';
import 'providers/chat_provider.dart';
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
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
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
        ChangeNotifierProxyProvider<ApiService, FoodLogProvider>(
          create: (ctx) => FoodLogProvider(ctx.read<ApiService>()),
          update: (_, api, prev) => prev ?? FoodLogProvider(api),
        ),
        ChangeNotifierProxyProvider<ApiService, ChatProvider>(
          create: (ctx) => ChatProvider(ctx.read<ApiService>()),
          update: (_, api, prev) => prev ?? ChatProvider(api),
        ),
      ],
      child: const XiaoSongApp(),
    ),
  );
}

class XiaoSongApp extends StatelessWidget {
  const XiaoSongApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return MaterialApp(
      title: '小松',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme(context),
      darkTheme: AppTheme.darkTheme(context),
      themeMode: themeProvider.themeMode,
      home: const MainScreen(),
    );
  }
}
