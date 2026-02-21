import 'package:flutter/foundation.dart';

class NavigationProvider extends ChangeNotifier {
  int _selectedIndex = 0;
  VoidCallback? onHomeRefreshed;

  int get selectedIndex => _selectedIndex;

  void switchTab(int index) {
    if (index >= 0 && index < 3) {
      bool isReturningToHome = (index == 0 && _selectedIndex != 0);
      _selectedIndex = index;
      notifyListeners();
      
      if (isReturningToHome && onHomeRefreshed != null) {
        onHomeRefreshed!();
      }
    }
  }

  void reset() {
    _selectedIndex = 0;
    notifyListeners();
  }
}
