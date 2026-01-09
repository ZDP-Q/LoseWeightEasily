"""
主窗口模块

包含主窗口、导航栏和页面切换逻辑。
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .pages.bmr import BMRPage
from .pages.dashboard import DashboardPage
from .pages.food_search import FoodSearchPage
from .pages.meal_plan import MealPlanPage
from .pages.settings import SettingsPage
from .pages.weight import WeightPage
from .styles import COLORS, NAV_STYLE


class NavButton(QPushButton):
    """导航按钮"""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.label_text = text
        self.setObjectName("nav_btn")
        self.setCheckable(True)
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_display(True)

    def update_display(self, expanded: bool):
        """更新显示模式"""
        if expanded:
            self.setText(f"  {self.icon_text}  {self.label_text}")
            self.setToolTip("")
        else:
            self.setText(f"  {self.icon_text}")
            self.setToolTip(self.label_text)


class NavigationBar(QWidget):
    """可收起的导航栏"""

    EXPANDED_WIDTH = 220
    COLLAPSED_WIDTH = 70

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("nav_widget")
        self.expanded = True
        self.buttons: list[NavButton] = []
        self.setup_ui()
        self.setStyleSheet(NAV_STYLE)
        self.setFixedWidth(self.EXPANDED_WIDTH)

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        # Logo 区域
        self.logo_frame = QFrame()
        logo_layout = QHBoxLayout(self.logo_frame)
        logo_layout.setContentsMargins(8, 0, 8, 0)

        self.logo_icon = QLabel("🍎")
        self.logo_icon.setFont(QFont("Segoe UI Emoji", 24))
        logo_layout.addWidget(self.logo_icon)

        self.logo_text = QLabel("轻松减重")
        self.logo_text.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.Bold))
        self.logo_text.setStyleSheet(f"color: {COLORS['text_primary']};")
        logo_layout.addWidget(self.logo_text)
        logo_layout.addStretch()

        layout.addWidget(self.logo_frame)
        layout.addSpacing(20)

        # 导航按钮
        nav_items = [
            ("🏠", "仪表盘", "dashboard"),
            ("⚖️", "体重记录", "weight"),
            ("🔍", "食物搜索", "food_search"),
            ("🔥", "代谢计算", "bmr"),
            ("🍽️", "食谱规划", "meal_plan"),
        ]

        for icon, text, name in nav_items:
            btn = NavButton(icon, text)
            btn.setProperty("page_name", name)
            self.buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # 底部设置按钮
        self.settings_btn = NavButton("⚙️", "设置")
        self.settings_btn.setProperty("page_name", "settings")
        self.buttons.append(self.settings_btn)
        layout.addWidget(self.settings_btn)

        # 收起/展开按钮
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setObjectName("nav_toggle")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_expand)
        layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # 默认选中第一个
        if self.buttons:
            self.buttons[0].setChecked(True)

    def toggle_expand(self):
        """切换展开/收起状态"""
        self.expanded = not self.expanded
        target_width = self.EXPANDED_WIDTH if self.expanded else self.COLLAPSED_WIDTH

        # 动画效果
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation2 = QPropertyAnimation(self, b"maximumWidth")
        self.animation2.setDuration(200)
        self.animation2.setStartValue(self.width())
        self.animation2.setEndValue(target_width)
        self.animation2.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation.start()
        self.animation2.start()

        # 更新显示
        self.toggle_btn.setText("▶" if not self.expanded else "◀")
        self.logo_text.setVisible(self.expanded)

        for btn in self.buttons:
            btn.update_display(self.expanded)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LossWeightEasily - 轻松减重助手")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """设置界面"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 导航栏
        self.nav_bar = NavigationBar()
        main_layout.addWidget(self.nav_bar)

        # 内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 页面堆栈
        self.page_stack = QStackedWidget()
        self.page_stack.setStyleSheet("background-color: transparent;")

        # 添加页面
        self.pages = {
            "dashboard": DashboardPage(),
            "weight": WeightPage(),
            "food_search": FoodSearchPage(),
            "bmr": BMRPage(),
            "meal_plan": MealPlanPage(),
            "settings": SettingsPage(),
        }

        for _name, page in self.pages.items():
            self.page_stack.addWidget(page)

        content_layout.addWidget(self.page_stack)
        main_layout.addWidget(content_widget)

    def connect_signals(self):
        """连接信号"""
        for btn in self.nav_bar.buttons:
            btn.clicked.connect(self.on_nav_clicked)

    def on_nav_clicked(self):
        """导航按钮点击事件"""
        sender = self.sender()
        page_name = sender.property("page_name")

        # 取消其他按钮的选中状态
        for btn in self.nav_bar.buttons:
            if btn != sender:
                btn.setChecked(False)

        sender.setChecked(True)

        # 切换页面
        if page_name in self.pages:
            self.page_stack.setCurrentWidget(self.pages[page_name])

            # 如果是仪表盘页面，刷新数据
            if page_name == "dashboard":
                self.pages["dashboard"].refresh_data()
            elif page_name == "weight":
                self.pages["weight"].refresh_data()
