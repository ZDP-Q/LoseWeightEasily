import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/food_log_provider.dart';
import 'providers/meal_plan_provider.dart';
import 'providers/navigation_provider.dart';
import 'providers/search_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/user_provider.dart';
import 'providers/weight_provider.dart';
import 'screens/auth_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/main_screen.dart';
import 'services/api_service.dart';
import 'utils/app_colors.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 1. 初始化 ApiService
  final apiService = ApiService();
  await apiService.init();
  
  // 2. 将 MultiProvider 移到最顶层，确保 Provider 生命周期跨越整个应用
  runApp(
    MultiProvider(
      providers: [
        // 认证 Provider
        ChangeNotifierProvider(create: (_) => AuthProvider(apiService)),
        
        // 导航 Provider
        ChangeNotifierProvider(create: (_) => NavigationProvider()),

        // 主题 Provider
        ChangeNotifierProvider(create: (_) => ThemeProvider()),

        // 用户 Provider
        ChangeNotifierProvider(create: (_) => UserProvider(apiService)),
        
        // 体重 Provider
        ChangeNotifierProvider(create: (_) => WeightProvider(apiService)),
        
        // 饮食记录 Provider
        ChangeNotifierProvider(create: (_) => FoodLogProvider(apiService)),
        
        // 饮食计划 Provider
        ChangeNotifierProvider(create: (_) => MealPlanProvider(apiService)),
        
        // 搜索 Provider
        ChangeNotifierProvider(create: (_) => SearchProvider(apiService)),
        
        // 聊天 Provider，注入 ApiService
        ChangeNotifierProvider(create: (_) => ChatProvider(apiService)),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, theme, _) {
        const seedColor = AppColors.primary;

        // 使用固定的基础文本主题
        final lightTextTheme = GoogleFonts.lexendTextTheme(ThemeData.light().textTheme);
        final darkTextTheme = GoogleFonts.lexendTextTheme(ThemeData.dark().textTheme);

        return MaterialApp(
          title: '小松减重助手',
          debugShowCheckedModeBanner: false,
          themeMode: theme.themeMode,
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(
              seedColor: seedColor,
              primary: seedColor,
              surface: const Color(0xFFF8FAF9),
              brightness: Brightness.light,
            ),
            textTheme: lightTextTheme,
            appBarTheme: const AppBarTheme(
              backgroundColor: Colors.white,
              elevation: 0,
              centerTitle: false,
              titleTextStyle: TextStyle(
                color: Colors.black87,
                fontSize: 20,
                fontWeight: FontWeight.bold,
                inherit: true, // 显式声明，确保平滑插值
              ),
              iconTheme: IconThemeData(color: Colors.black87),
            ),
            cardTheme: CardThemeData(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              color: Colors.white,
            ),
            inputDecorationTheme: InputDecorationTheme(
              filled: true,
              fillColor: Colors.grey.withValues(alpha: 0.05),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
              ),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
          ),
          darkTheme: ThemeData(
            useMaterial3: true,
            brightness: Brightness.dark,
            colorScheme: ColorScheme.fromSeed(
              seedColor: seedColor,
              primary: seedColor,
              brightness: Brightness.dark,
            ),
            textTheme: darkTextTheme,
            appBarTheme: const AppBarTheme(
              elevation: 0,
              centerTitle: false,
              titleTextStyle: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                inherit: true,
              ),
            ),
          ),
          home: const RootNavigator(),
          routes: {
            '/home': (context) => const MainScreen(),
            '/auth': (context) => const AuthScreen(),
            '/onboarding': (context) => const OnboardingScreen(),
          },
        );
      },
    );
  }
}

/// 根导航器：根据认证状态决定显示的页面
class RootNavigator extends StatelessWidget {
  const RootNavigator({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        if (auth.isLoading) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        if (auth.isAuthenticated) {
          if (auth.needsOnboarding) {
            return const OnboardingScreen();
          }
          return const MainScreen();
        }

        return const AuthScreen();
      },
    );
  }
}
