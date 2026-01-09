"""
仪表盘页面

显示概览统计信息和快捷操作。
"""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ...weight_tracker import WeightTracker
from ..styles import COLORS
from .base import Card, ScrollablePage, StatCard


class DashboardPage(ScrollablePage):
    """仪表盘页面"""

    def __init__(self, parent=None):
        self.page_title = "仪表盘"
        super().__init__(self.page_title, parent)
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        """设置界面"""
        # 欢迎语
        welcome_layout = QHBoxLayout()

        greeting = self.get_greeting()
        welcome_label = QLabel(f"{greeting}，开始今天的健康之旅吧！")
        welcome_label.setFont(QFont("Microsoft YaHei UI", 16))
        welcome_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addStretch()

        # 日期
        date_label = QLabel(datetime.now().strftime("%Y年%m月%d日"))
        date_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        welcome_layout.addWidget(date_label)

        self.main_layout.addLayout(welcome_layout)

        # 统计卡片区域
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self.weight_card = StatCard(
            title="当前体重",
            value="-- kg",
            icon="⚖️",
            change=""
        )
        stats_layout.addWidget(self.weight_card)

        self.target_card = StatCard(
            title="目标体重",
            value="-- kg",
            icon="🎯",
            change=""
        )
        stats_layout.addWidget(self.target_card)

        self.bmr_card = StatCard(
            title="基础代谢",
            value="-- kcal",
            icon="🔥",
            change=""
        )
        stats_layout.addWidget(self.bmr_card)

        self.records_card = StatCard(
            title="打卡天数",
            value="0 天",
            icon="📅",
            change=""
        )
        stats_layout.addWidget(self.records_card)

        self.main_layout.addLayout(stats_layout)

        # 快捷操作区域
        quick_actions_card = Card("快捷操作")

        actions_layout = QGridLayout()
        actions_layout.setSpacing(16)

        actions = [
            ("⚖️", "记录体重", "weight", COLORS["primary"]),
            ("🔍", "搜索食物", "food", COLORS["secondary"]),
            ("🔥", "计算代谢", "bmr", COLORS["accent"]),
            ("🍽️", "生成食谱", "meal", COLORS["success"]),
        ]

        for i, (icon, text, action, color) in enumerate(actions):
            btn = QPushButton(f"{icon}\n{text}")
            btn.setFont(QFont("Segoe UI Emoji", 12))
            btn.setMinimumSize(140, 100)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS["bg_card"]};
                    border: 2px solid {COLORS["border_light"]};
                    border-radius: 12px;
                    color: {COLORS["text_primary"]};
                }}
                QPushButton:hover {{
                    background-color: {color};
                    border-color: {color};
                }}
            """)
            btn.setProperty("action", action)
            btn.clicked.connect(self.on_quick_action)
            actions_layout.addWidget(btn, i // 4, i % 4)

        quick_actions_card.card_layout.addLayout(actions_layout)
        self.main_layout.addWidget(quick_actions_card)

        # 最近记录
        recent_card = Card("最近体重记录")

        self.recent_records_layout = QVBoxLayout()
        self.recent_records_layout.setSpacing(8)
        recent_card.card_layout.addLayout(self.recent_records_layout)

        self.main_layout.addWidget(recent_card)

        # 添加弹性空间
        self.main_layout.addStretch()

    def get_greeting(self) -> str:
        """根据时间返回问候语"""
        hour = datetime.now().hour
        if hour < 6:
            return "夜深了"
        elif hour < 12:
            return "早上好"
        elif hour < 14:
            return "中午好"
        elif hour < 18:
            return "下午好"
        else:
            return "晚上好"

    def refresh_data(self):
        """刷新数据"""
        try:
            tracker = WeightTracker()
            stats = tracker.get_weight_statistics()

            # 更新当前体重
            if stats['latest_weight']:
                weight_text = f"{stats['latest_weight']:.1f} kg"
                change = ""
                change_positive = True

                if stats['weight_change'] is not None and stats['total_records'] > 1:
                    change = f"{'↓' if stats['weight_change'] < 0 else '↑'} {abs(stats['weight_change']):.1f} kg 自首次记录"
                    change_positive = stats['weight_change'] <= 0

                self.weight_card.update_value(weight_text, change, change_positive)

            # 更新打卡天数
            self.records_card.update_value(f"{stats['total_records']} 天")

            # 更新最近记录
            self.update_recent_records(tracker)

        except Exception:
            # 静默处理错误，避免影响 UI 显示
            # 通常是因为还没有数据记录
            pass

    def update_recent_records(self, tracker: WeightTracker):
        """更新最近记录列表"""
        # 清空现有内容
        while self.recent_records_layout.count():
            item = self.recent_records_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        records = tracker.get_records(5)

        if not records:
            empty_label = QLabel("暂无体重记录，点击上方按钮开始记录吧！")
            empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 20px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_records_layout.addWidget(empty_label)
            return

        for i, record in enumerate(records):
            record_frame = QFrame()
            record_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS["bg_main"]};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)

            record_layout = QHBoxLayout(record_frame)
            record_layout.setContentsMargins(16, 12, 16, 12)

            # 日期
            date_label = QLabel(record['recorded_at'][:10] if record['recorded_at'] else "")
            date_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            record_layout.addWidget(date_label)

            # 体重
            weight_label = QLabel(f"{record['weight_kg']:.1f} kg")
            weight_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
            weight_label.setStyleSheet(f"color: {COLORS['text_primary']};")
            record_layout.addWidget(weight_label)

            # 变化（与上一条记录比较）
            if i < len(records) - 1:
                prev_weight = records[i + 1]['weight_kg']
                change = record['weight_kg'] - prev_weight
                if abs(change) >= 0.1:
                    change_text = f"{'↓' if change < 0 else '↑'} {abs(change):.1f}"
                    color = COLORS["success"] if change < 0 else COLORS["danger"]
                    change_label = QLabel(change_text)
                    change_label.setStyleSheet(f"color: {color};")
                    record_layout.addWidget(change_label)

            record_layout.addStretch()

            # 备注
            if record['notes']:
                notes_label = QLabel(record['notes'])
                notes_label.setStyleSheet(f"color: {COLORS['text_muted']};")
                record_layout.addWidget(notes_label)

            self.recent_records_layout.addWidget(record_frame)

    def on_quick_action(self):
        """快捷操作点击"""
        sender = self.sender()
        action = sender.property("action")

        # 通知主窗口切换页面
        main_window = self.window()
        if hasattr(main_window, 'nav_bar'):
            page_map = {
                "weight": 1,
                "food": 2,
                "bmr": 3,
                "meal": 4,
            }
            if action in page_map:
                idx = page_map[action]
                if idx < len(main_window.nav_bar.buttons):
                    main_window.nav_bar.buttons[idx].click()
