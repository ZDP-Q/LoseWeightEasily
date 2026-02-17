import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../providers/navigation_provider.dart';
import 'dashboard_screen.dart';
import 'xiao_song_screen.dart';
import 'user_screen.dart';
import '../utils/app_colors.dart';

class MainScreen extends StatelessWidget {
  const MainScreen({super.key});

  static const List<Widget> _screens = [
    DashboardScreen(),
    XiaoSongScreen(),
    UserScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final navProvider = context.watch<NavigationProvider>();
    final selectedIndex = navProvider.selectedIndex;

    return Scaffold(
      body: IndexedStack(
        index: selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: NavigationBar(
          height: 70,
          elevation: 0,
          selectedIndex: selectedIndex,
          onDestinationSelected: navProvider.switchTab,
          backgroundColor: Theme.of(context).scaffoldBackgroundColor,
          indicatorColor: AppColors.primary.withValues(alpha: 0.1),
          destinations: const [
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.house, size: 20),
              selectedIcon: Icon(FontAwesomeIcons.house, size: 20, color: AppColors.primary),
              label: '首页',
            ),
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.tree, size: 20),
              selectedIcon: Icon(FontAwesomeIcons.tree, size: 20, color: AppColors.primary),
              label: '小松',
            ),
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.user, size: 20),
              selectedIcon: Icon(FontAwesomeIcons.user, size: 20, color: AppColors.primary),
              label: '我的',
            ),
          ],
        ),
      ),
    );
  }
}
