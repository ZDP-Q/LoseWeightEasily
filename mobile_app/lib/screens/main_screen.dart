import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../providers/navigation_provider.dart';
import 'dashboard_screen.dart';
import 'search_screen.dart';
import 'weight_screen.dart';
import 'meal_plan_screen.dart';
import 'user_screen.dart';

class MainScreen extends StatelessWidget {
  const MainScreen({super.key});

  static const List<Widget> _screens = [
    DashboardScreen(),
    SearchScreen(),
    WeightScreen(),
    MealPlanScreen(),
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
          selectedIndex: selectedIndex,
          onDestinationSelected: navProvider.switchTab,
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
