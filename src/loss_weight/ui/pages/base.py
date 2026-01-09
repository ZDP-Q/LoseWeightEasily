"""
基础页面组件

提供页面通用组件和基类。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..styles import CARD_STYLE, COLORS, STAT_CARD_STYLE


class BasePage(QWidget):
    """页面基类"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.page_title = title
        self.setup_base_ui()

    def setup_base_ui(self):
        """设置基础界面"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(24)

        # 页面标题
        if self.page_title:
            self.title_label = QLabel(self.page_title)
            self.title_label.setFont(QFont("Microsoft YaHei UI", 24, QFont.Weight.Bold))
            self.title_label.setStyleSheet(f"color: {COLORS['text_primary']};")
            self.main_layout.addWidget(self.title_label)

    def refresh_data(self):
        """刷新数据 - 子类实现"""
        pass


class StatCard(QFrame):
    """统计卡片组件"""

    def __init__(
        self,
        title: str,
        value: str,
        icon: str = "",
        change: str = "",
        change_positive: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setStyleSheet(STAT_CARD_STYLE)
        self.setup_ui(title, value, icon, change, change_positive)

    def setup_ui(self, title: str, value: str, icon: str, change: str, change_positive: bool):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        # 顶部：图标和标题
        top_layout = QHBoxLayout()

        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 20))
            top_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("stat_label")
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        # 数值
        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat_value")
        layout.addWidget(self.value_label)

        # 变化
        if change:
            self.change_label = QLabel(change)
            self.change_label.setObjectName(
                "stat_change_positive" if change_positive else "stat_change_negative"
            )
            layout.addWidget(self.change_label)

        layout.addStretch()

    def update_value(self, value: str, change: str = "", change_positive: bool = True):
        """更新数值"""
        self.value_label.setText(value)
        if hasattr(self, "change_label") and change:
            self.change_label.setText(change)
            self.change_label.setObjectName(
                "stat_change_positive" if change_positive else "stat_change_negative"
            )
            self.change_label.style().unpolish(self.change_label)
            self.change_label.style().polish(self.change_label)


class Card(QFrame):
    """通用卡片组件"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(CARD_STYLE)

        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(16)

        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.Bold))
            title_label.setStyleSheet(f"color: {COLORS['text_primary']};")
            self.card_layout.addWidget(title_label)


class ScrollablePage(BasePage):
    """可滚动页面基类"""

    def setup_base_ui(self):
        """设置基础界面"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background-color: transparent;")

        # 内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")

        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(24)

        # 页面标题
        if self.page_title:
            self.title_label = QLabel(self.page_title)
            self.title_label.setFont(QFont("Microsoft YaHei UI", 24, QFont.Weight.Bold))
            self.title_label.setStyleSheet(f"color: {COLORS['text_primary']};")
            self.main_layout.addWidget(self.title_label)

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)
