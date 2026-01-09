"""
LossWeightEasily UI 模块

提供现代化的图形用户界面。
使用依赖注入容器管理服务。
"""

from __future__ import annotations

import sys


def main() -> None:
    """UI 主入口函数"""
    # 延迟导入 PySide6 以加快启动速度
    from PySide6.QtWidgets import QApplication

    from ..container import get_database
    from .main_window import MainWindow
    from .styles import GLOBAL_STYLE

    # 确保数据库表存在
    db_manager = get_database()
    db_manager.create_tables()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
