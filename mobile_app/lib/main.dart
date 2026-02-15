import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'providers/user_provider.dart';
import 'providers/weight_provider.dart';
import 'screens/main_screen.dart';
import 'utils/theme.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        Provider(create: (_) => ApiService()),
        ChangeNotifierProxyProvider<ApiService, UserProvider>(
          create: (ctx) => UserProvider(ctx.read<ApiService>()),
          update: (_, api, prev) => prev ?? UserProvider(api),
        ),
        ChangeNotifierProxyProvider<ApiService, WeightProvider>(
          create: (ctx) => WeightProvider(ctx.read<ApiService>()),
          update: (_, api, prev) => prev ?? WeightProvider(api),
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
