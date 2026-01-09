"""
LossWeightEasily UI 模块

提供现代化的图形用户界面。
"""

import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .styles import GLOBAL_STYLE


def main():
    """UI 主入口函数"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
