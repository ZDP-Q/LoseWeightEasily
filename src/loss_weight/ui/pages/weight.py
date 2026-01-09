"""
体重记录页面

提供体重打卡、历史记录和趋势图表。
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..styles import COLORS
from .base import Card, ScrollablePage


class WeightChart(QWidget):
    """体重趋势图表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []  # [(date, weight), ...]
        self.setMinimumHeight(300)
        self.setStyleSheet(f"background-color: {COLORS['bg_card']}; border-radius: 16px;")

    def set_data(self, records: list):
        """设置数据"""
        self.data = []
        for record in reversed(records):  # 按时间正序
            # WeightRecord 是 Pydantic 模型，使用属性访问
            recorded_at = record.recorded_at
            weight_kg = record.weight_kg
            if recorded_at and weight_kg:
                # recorded_at 可能是 datetime 或字符串
                if hasattr(recorded_at, "strftime"):
                    date_str = recorded_at.strftime("%Y-%m-%d")
                else:
                    date_str = str(recorded_at)[:10]
                self.data.append((date_str, weight_kg))
        self.update()

    def paintEvent(self, event):
        """绘制图表"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 背景
        painter.fillRect(self.rect(), QColor(COLORS["bg_card"]))

        if len(self.data) < 2:
            # 数据不足，显示提示
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.setFont(QFont("Microsoft YaHei UI", 14))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "需要至少两条记录才能显示趋势图"
            )
            return

        # 计算绘图区域
        padding = 60
        chart_left = padding + 20
        chart_right = self.width() - padding
        chart_top = padding
        chart_bottom = self.height() - padding - 20
        chart_width = chart_right - chart_left
        chart_height = chart_bottom - chart_top

        # 计算数据范围
        weights = [w for _, w in self.data]
        min_weight = min(weights) - 1
        max_weight = max(weights) + 1
        weight_range = max_weight - min_weight

        if weight_range == 0:
            weight_range = 1

        # 绘制网格线和Y轴刻度
        painter.setPen(QPen(QColor(COLORS["border_light"]), 1))
        painter.setFont(QFont("Microsoft YaHei UI", 10))

        num_lines = 5
        for i in range(num_lines + 1):
            y = chart_top + (chart_height * i / num_lines)
            weight = max_weight - (weight_range * i / num_lines)

            # 网格线
            painter.setPen(QPen(QColor(COLORS["border_light"]), 1, Qt.PenStyle.DashLine))
            painter.drawLine(int(chart_left), int(y), int(chart_right), int(y))

            # Y轴刻度
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.drawText(
                int(padding - 10),
                int(y - 8),
                50,
                20,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                f"{weight:.1f}",
            )

        # 计算点的位置
        points = []
        for i, (_date, weight) in enumerate(self.data):
            x = chart_left + (chart_width * i / (len(self.data) - 1))
            y = chart_top + chart_height * (1 - (weight - min_weight) / weight_range)
            points.append(QPointF(x, y))

        # 绘制渐变填充区域
        if points:
            gradient = QLinearGradient(0, chart_top, 0, chart_bottom)
            gradient.setColorAt(0, QColor(99, 102, 241, 80))
            gradient.setColorAt(1, QColor(99, 102, 241, 10))

            fill_path = QPainterPath()
            fill_path.moveTo(points[0].x(), chart_bottom)
            for point in points:
                fill_path.lineTo(point)
            fill_path.lineTo(points[-1].x(), chart_bottom)
            fill_path.closeSubpath()

            painter.fillPath(fill_path, QBrush(gradient))

        # 绘制折线
        painter.setPen(QPen(QColor(COLORS["primary"]), 3))
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        # 绘制数据点
        for point in points:
            # 外圈
            painter.setBrush(QBrush(QColor(COLORS["primary"])))
            painter.setPen(QPen(QColor(COLORS["bg_card"]), 3))
            painter.drawEllipse(point, 6, 6)

        # 绘制X轴日期标签（只显示部分）
        painter.setPen(QColor(COLORS["text_muted"]))
        painter.setFont(QFont("Microsoft YaHei UI", 9))

        # 智能选择要显示的日期数量
        max_labels = min(7, len(self.data))
        step = max(1, len(self.data) // max_labels)

        for i in range(0, len(self.data), step):
            date, _ = self.data[i]
            x = (
                chart_left + (chart_width * i / (len(self.data) - 1))
                if len(self.data) > 1
                else chart_left
            )

            # 显示日期（只显示月-日）
            try:
                display_date = date[5:]  # MM-DD
            except Exception:
                display_date = date

            painter.drawText(
                int(x - 25),
                int(chart_bottom + 8),
                50,
                20,
                Qt.AlignmentFlag.AlignCenter,
                display_date,
            )


class WeightPage(ScrollablePage):
    """体重记录页面"""

    def __init__(self, parent=None):
        self.page_title = "体重记录"
        super().__init__(self.page_title, parent)

        # 使用容器获取 WeightTracker，确保数据库表已创建
        from ...container import get_container

        container = get_container()
        container.ensure_database()  # 确保数据库表存在
        self.tracker = container.weight_tracker

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        """设置界面"""
        # 打卡区域
        checkin_card = Card("📝 今日打卡")

        checkin_layout = QHBoxLayout()
        checkin_layout.setSpacing(16)

        # 体重输入
        weight_label = QLabel("体重 (kg):")
        weight_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        checkin_layout.addWidget(weight_label)

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(20, 300)
        self.weight_input.setDecimals(1)
        self.weight_input.setSingleStep(0.1)
        self.weight_input.setValue(60.0)
        self.weight_input.setMinimumWidth(120)
        self.weight_input.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {COLORS["bg_main"]};
                border: 2px solid {COLORS["border_light"]};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
            QDoubleSpinBox:focus {{
                border-color: {COLORS["primary"]};
            }}
        """)
        checkin_layout.addWidget(self.weight_input)

        # 备注输入
        notes_label = QLabel("备注:")
        notes_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        checkin_layout.addWidget(notes_label)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("可选，如：早餐前、运动后...")
        self.notes_input.setMinimumWidth(200)
        checkin_layout.addWidget(self.notes_input)

        checkin_layout.addStretch()

        # 提交按钮
        self.submit_btn = QPushButton("✓ 记录")
        self.submit_btn.setMinimumWidth(100)
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.setProperty("class", "success")
        self.submit_btn.clicked.connect(self.on_submit)
        checkin_layout.addWidget(self.submit_btn)

        checkin_card.card_layout.addLayout(checkin_layout)
        self.main_layout.addWidget(checkin_card)

        # 趋势图表
        chart_card = Card("📈 体重趋势")

        self.weight_chart = WeightChart()
        chart_card.card_layout.addWidget(self.weight_chart)

        self.main_layout.addWidget(chart_card)

        # 统计信息
        stats_card = Card("📊 统计信息")

        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(40)

        self.stat_labels = {}
        stat_items = [
            ("current", "当前体重", "--"),
            ("change", "总变化", "--"),
            ("average", "平均体重", "--"),
            ("min", "最低体重", "--"),
            ("max", "最高体重", "--"),
            ("records", "记录次数", "--"),
        ]

        for key, label, default in stat_items:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setSpacing(4)

            value_label = QLabel(default)
            value_label.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.Bold))
            value_label.setStyleSheet(f"color: {COLORS['text_primary']};")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(value_label)

            name_label = QLabel(label)
            name_label.setStyleSheet(f"color: {COLORS['text_muted']};")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(name_label)

            self.stat_labels[key] = value_label
            self.stats_layout.addWidget(stat_widget)

        stats_card.card_layout.addLayout(self.stats_layout)
        self.main_layout.addWidget(stats_card)

        # 历史记录表格
        history_card = Card("📋 历史记录")

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["日期", "体重 (kg)", "变化", "备注"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setMinimumHeight(300)
        self.history_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS["bg_main"]};
                border: none;
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 12px;
            }}
            QTableWidget::item:alternate {{
                background-color: {COLORS["bg_card"]};
            }}
        """)

        history_card.card_layout.addWidget(self.history_table)
        self.main_layout.addWidget(history_card)

        self.main_layout.addStretch()

    def on_submit(self):
        """提交体重记录"""
        from ...logging_config import get_logger

        logger = get_logger(__name__)

        weight = self.weight_input.value()
        notes = self.notes_input.text().strip()

        if weight <= 0:
            QMessageBox.warning(self, "提示", "请输入有效的体重")
            return

        try:
            logger.info(f"记录体重: {weight:.1f} kg, 备注: '{notes}'")
            self.tracker.record_weight(weight, notes)
            self.notes_input.clear()
            self.refresh_data()

            # 显示成功提示
            logger.info(f"体重记录成功: {weight:.1f} kg")
            QMessageBox.information(self, "成功", f"✅ 已记录体重: {weight:.1f} kg")

        except Exception as e:
            logger.error(f"体重记录失败: {e}")
            QMessageBox.critical(self, "错误", f"记录失败: {e}")

    def refresh_data(self):
        """刷新数据"""
        try:
            # 获取统计信息 (WeightStatistics 是 Pydantic 模型)
            stats = self.tracker.get_weight_statistics()

            # 更新统计标签
            if stats.latest_weight:
                self.stat_labels["current"].setText(f"{stats.latest_weight:.1f} kg")

            if stats.weight_change is not None:
                change = stats.weight_change
                sign = "+" if change > 0 else ""
                color = COLORS["success"] if change <= 0 else COLORS["danger"]
                self.stat_labels["change"].setText(f"{sign}{change:.1f} kg")
                self.stat_labels["change"].setStyleSheet(
                    f"color: {color}; font-size: 18px; font-weight: bold;"
                )

            if stats.average_weight:
                self.stat_labels["average"].setText(f"{stats.average_weight:.1f} kg")

            if stats.min_weight:
                self.stat_labels["min"].setText(f"{stats.min_weight:.1f} kg")

            if stats.max_weight:
                self.stat_labels["max"].setText(f"{stats.max_weight:.1f} kg")

            self.stat_labels["records"].setText(f"{stats.total_records} 次")

            # 设置默认输入值为最近一次体重
            if stats.latest_weight:
                self.weight_input.setValue(stats.latest_weight)

            # 获取历史记录 (返回 list[WeightRecord])
            records = self.tracker.get_records(50)

            # 更新图表
            self.weight_chart.set_data(records)

            # 更新表格
            self.history_table.setRowCount(len(records))

            for i, record in enumerate(records):
                # 日期 (WeightRecord 是 Pydantic 模型)
                recorded_at = record.recorded_at
                if hasattr(recorded_at, "strftime"):
                    date_str = recorded_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str = str(recorded_at)[:19] if recorded_at else ""
                date_item = QTableWidgetItem(date_str)
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.history_table.setItem(i, 0, date_item)

                # 体重
                weight_item = QTableWidgetItem(f"{record.weight_kg:.1f}")
                weight_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.history_table.setItem(i, 1, weight_item)

                # 变化
                change_text = ""
                if i < len(records) - 1:
                    prev_weight = records[i + 1].weight_kg
                    change = record.weight_kg - prev_weight
                    if abs(change) >= 0.1:
                        sign = "+" if change > 0 else ""
                        change_text = f"{sign}{change:.1f}"

                change_item = QTableWidgetItem(change_text)
                change_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if change_text:
                    color = COLORS["success"] if change_text.startswith("-") else COLORS["danger"]
                    change_item.setForeground(QColor(color))
                self.history_table.setItem(i, 2, change_item)

                # 备注
                notes_item = QTableWidgetItem(record.notes or "")
                self.history_table.setItem(i, 3, notes_item)

        except Exception as e:
            # 记录错误日志
            from ...logging_config import get_logger

            logger = get_logger(__name__)
            logger.debug(f"刷新体重数据失败: {e}")
