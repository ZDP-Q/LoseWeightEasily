import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/food_log_provider.dart';
import 'providers/navigation_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/user_provider.dart';
import 'providers/weight_provider.dart';
import 'screens/login_screen.dart';
import 'screens/main_screen.dart';
import 'services/api_service.dart';
import 'utils/app_colors.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // 基础 ApiService 实例，单例管理
    final apiService = ApiService();

    return MultiProvider(
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
        
        // 聊天 Provider，注入 ApiService
        ChangeNotifierProvider(create: (_) => ChatProvider(apiService)),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, theme, _) {
          return MaterialApp(
            title: '小松减重助手',
            debugShowCheckedModeBanner: false,
            themeMode: theme.themeMode,
            theme: ThemeData(
              useMaterial3: true,
              colorScheme: ColorScheme.fromSeed(
                seedColor: AppColors.primary,
                primary: AppColors.primary,
                surface: const Color(0xFFF8FAF9),
              ),
              textTheme: GoogleFonts.lexendTextTheme(
                Theme.of(context).textTheme,
              ),
              appBarTheme: const AppBarTheme(
                backgroundColor: Colors.white,
                elevation: 0,
                centerTitle: false,
                titleTextStyle: TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
                iconTheme: IconThemeData(color: AppColors.textPrimary),
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
                seedColor: AppColors.primary,
                primary: AppColors.primary,
                brightness: Brightness.dark,
              ),
              textTheme: GoogleFonts.lexendTextTheme(
                ThemeData.dark().textTheme,
              ),
            ),
            home: const RootNavigator(),
          );
        },
      ),
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
           return const MainScreen();
        }

        return const LoginScreen();
      },
    );
  }
}
