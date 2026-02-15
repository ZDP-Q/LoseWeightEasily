import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'utils/theme.dart';
import 'screens/main_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        Provider(create: (_) => ApiService()),
        // Add more providers here as needed
      ],
      child: const LoseWeightApp(),
    ),
  );
}

class LoseWeightApp extends StatelessWidget {
  const LoseWeightApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LoseWeightEasily',
      theme: AppTheme.darkTheme,
      home: const MainScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
