"""
食物搜索页面

提供食物营养信息搜索功能。
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from ..styles import COLORS
from .base import Card, ScrollablePage


class SearchWorker(QThread):
    """搜索工作线程"""

    finished = Signal(list)
    error = Signal(str)

    def __init__(self, query: str, limit: int = 10):
        super().__init__()
        self.query = query
        self.limit = limit

    def run(self):
        """执行搜索"""
        try:
            from ...search import FoodSearchEngine

            engine = FoodSearchEngine()
            engine.ensure_index()
            results = engine.search_with_details(self.query, self.limit)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class FoodSearchPage(ScrollablePage):
    """食物搜索页面"""

    def __init__(self, parent=None):
        self.page_title = "食物搜索"
        super().__init__(self.page_title, parent)
        self.search_worker = None
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 搜索区域
        search_card = Card("🔍 搜索食物")

        search_layout = QHBoxLayout()
        search_layout.setSpacing(16)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入食物名称，支持中英文搜索...")
        self.search_input.setMinimumHeight(45)
        self.search_input.setFont(QFont("Microsoft YaHei UI", 14))
        self.search_input.returnPressed.connect(self.on_search)
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("搜索")
        self.search_btn.setMinimumWidth(100)
        self.search_btn.setMinimumHeight(45)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.on_search)
        search_layout.addWidget(self.search_btn)

        search_card.card_layout.addLayout(search_layout)

        # 搜索提示
        tips_label = QLabel("💡 提示：可以输入食物名称、类别或描述，如\"番茄\"、\"beef\"、\"富含蛋白质\"")
        tips_label.setStyleSheet(f"color: {COLORS['text_muted']}; margin-top: 8px;")
        search_card.card_layout.addWidget(tips_label)

        self.main_layout.addWidget(search_card)

        # 加载指示器
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        self.loading_bar.setMaximumHeight(4)
        self.main_layout.addWidget(self.loading_bar)

        # 结果区域
        results_card = Card("📋 搜索结果")

        self.results_label = QLabel("输入关键词开始搜索")
        self.results_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        results_card.card_layout.addWidget(self.results_label)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "食物名称", "分类", "热量 (kcal/100g)", "常用份量", "相似度"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setMinimumHeight(400)
        self.results_table.setVisible(False)
        self.results_table.setStyleSheet(f"""
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

        results_card.card_layout.addWidget(self.results_table)
        self.main_layout.addWidget(results_card)

        self.main_layout.addStretch()

    def on_search(self):
        """执行搜索"""
        query = self.search_input.text().strip()

        if not query:
            return

        # 显示加载状态
        self.loading_bar.setVisible(True)
        self.search_btn.setEnabled(False)
        self.results_label.setText("正在搜索...")
        self.results_table.setVisible(False)

        # 启动搜索线程
        self.search_worker = SearchWorker(query, limit=20)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.start()

    def on_search_finished(self, results: list):
        """搜索完成"""
        self.loading_bar.setVisible(False)
        self.search_btn.setEnabled(True)

        if not results:
            self.results_label.setText("未找到匹配的食物")
            self.results_table.setVisible(False)
            return

        self.results_label.setText(f"找到 {len(results)} 个结果")
        self.results_table.setVisible(True)
        self.results_table.setRowCount(len(results))

        for i, food in enumerate(results):
            # 食物名称
            name_item = QTableWidgetItem(food.get('name', '--'))
            self.results_table.setItem(i, 0, name_item)

            # 分类
            category_item = QTableWidgetItem(food.get('category', '--'))
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(i, 1, category_item)

            # 热量
            calories = food.get('calories_per_100g')
            calories_text = f"{calories:.1f}" if calories else "--"
            calories_item = QTableWidgetItem(calories_text)
            calories_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(i, 2, calories_item)

            # 常用份量
            portions = food.get('portions', [])
            if portions:
                portion = portions[0]
                portion_text = f"{portion[0]} {portion[1]} ({portion[2]}g)"
            else:
                portion_text = "--"
            portion_item = QTableWidgetItem(portion_text)
            portion_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(i, 3, portion_item)

            # 相似度
            similarity = food.get('similarity', 0)
            similarity_text = f"{similarity * 100:.0f}%"
            similarity_item = QTableWidgetItem(similarity_text)
            similarity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(i, 4, similarity_item)

    def on_search_error(self, error: str):
        """搜索出错"""
        self.loading_bar.setVisible(False)
        self.search_btn.setEnabled(True)
        self.results_label.setText(f"搜索失败: {error}")
        self.results_table.setVisible(False)
