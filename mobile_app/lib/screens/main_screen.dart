import 'package:flutter/material.dart';
import 'package:animations/animations.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'dashboard_screen.dart';
import 'search_screen.dart';
import 'weight_screen.dart';
import 'meal_plan_screen.dart';
import 'user_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => MainScreenState();
}

/// 公开 State 类以供 DashboardScreen 通过 findAncestorStateOfType 访问
class MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const DashboardScreen(),
    const SearchScreen(),
    const WeightScreen(),
    const MealPlanScreen(),
    const UserScreen(),
  ];

  /// 供子页面调用以切换 Tab
  void switchTab(int index) {
    if (index >= 0 && index < _screens.length) {
      setState(() => _selectedIndex = index);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageTransitionSwitcher(
        duration: const Duration(milliseconds: 400),
        transitionBuilder: (child, primaryAnimation, secondaryAnimation) {
          return FadeThroughTransition(
            animation: primaryAnimation,
            secondaryAnimation: secondaryAnimation,
            child: child,
          );
        },
        child: _screens[_selectedIndex],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          border: Border(
            top: BorderSide(
              color: Theme.of(context).dividerColor.withValues(alpha: 0.1),
              width: 0.5,
            ),
          ),
        ),
        child: NavigationBar(
          height: 65,
          elevation: 0,
          selectedIndex: _selectedIndex,
          onDestinationSelected: (index) {
            setState(() {
              _selectedIndex = index;
            });
          },
          destinations: const [
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.house, size: 20),
              selectedIcon:
                  Icon(FontAwesomeIcons.house, size: 20, color: Colors.white),
              label: '首页',
            ),
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.magnifyingGlass, size: 20),
              selectedIcon: Icon(FontAwesomeIcons.magnifyingGlass,
                  size: 20, color: Colors.white),
              label: '查食物',
            ),
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.weightScale, size: 20),
              selectedIcon: Icon(FontAwesomeIcons.weightScale,
                  size: 20, color: Colors.white),
              label: '记体重',
            ),
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.utensils, size: 20),
              selectedIcon: Icon(FontAwesomeIcons.utensils,
                  size: 20, color: Colors.white),
              label: '开食谱',
            ),
            NavigationDestination(
              icon: Icon(FontAwesomeIcons.user, size: 20),
              selectedIcon:
                  Icon(FontAwesomeIcons.user, size: 20, color: Colors.white),
              label: '我的',
            ),
          ],
        ),
      ),
    );
  }
}
