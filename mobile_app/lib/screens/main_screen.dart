import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../providers/navigation_provider.dart';
import 'dashboard_screen.dart';
import 'xiao_song_screen.dart';
import 'user_screen.dart';
import '../utils/app_colors.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  // 记录哪些页面已经被使用过，只构建访问过的页面
  final Set<int> _initializedPages = {0}; // 首页默认加载

  static Widget _buildPage(int index) {
    switch (index) {
      case 0:
        return const DashboardScreen();
      case 1:
        return const XiaoSongScreen();
      case 2:
        return const UserScreen();
      default:
        return const SizedBox.shrink();
    }
  }

  @override
  Widget build(BuildContext context) {
    final navProvider = context.watch<NavigationProvider>();
    final selectedIndex = navProvider.selectedIndex;

    // 懒加载：只在首次切换到该页面时才初始化
    _initializedPages.add(selectedIndex);

    return Scaffold(
      body: IndexedStack(
        index: selectedIndex,
        children: List.generate(3, (index) {
          if (_initializedPages.contains(index)) {
            return _buildPage(index);
          }
          // 未初始化的页面用占位符，避免提前构建
          return const SizedBox.shrink();
        }),
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
