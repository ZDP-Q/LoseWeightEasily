import 'package:flutter/foundation.dart';

class NavigationProvider extends ChangeNotifier {
  int _selectedIndex = 0;

  int get selectedIndex => _selectedIndex;

  void switchTab(int index) {
    if (index >= 0 && index < 5 && index != _selectedIndex) {
      _selectedIndex = index;
      notifyListeners();
    }
  }
}
