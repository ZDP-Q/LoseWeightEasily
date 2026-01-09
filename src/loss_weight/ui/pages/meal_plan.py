"""
食谱规划页面

根据食材生成一日三餐食谱。
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...config import config
from ..styles import COLORS
from .base import Card, ScrollablePage


class MealPlanWorker(QThread):
    """食谱生成工作线程"""

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, ingredients: list, preferences: str, restrictions: str):
        super().__init__()
        self.ingredients = ingredients
        self.preferences = preferences
        self.restrictions = restrictions

    def run(self):
        """执行生成"""
        try:
            from ...meal_planner import MealPlanner

            planner = MealPlanner()
            result = planner.generate_meal_plan(
                ingredients=self.ingredients,
                preferences=self.preferences,
                dietary_restrictions=self.restrictions
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MealPlanPage(ScrollablePage):
    """食谱规划页面"""

    def __init__(self, parent=None):
        self.page_title = "食谱规划"
        super().__init__(self.page_title, parent)
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 输入区域
        input_card = Card("🥗 输入你的食材")

        # 食材输入
        ingredients_label = QLabel("可用食材 (用逗号或空格分隔):")
        ingredients_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        input_card.card_layout.addWidget(ingredients_label)

        self.ingredients_input = QLineEdit()
        self.ingredients_input.setPlaceholderText("例如：鸡胸肉, 西兰花, 胡萝卜, 大米, 鸡蛋...")
        self.ingredients_input.setMinimumHeight(45)
        self.ingredients_input.setFont(QFont("Microsoft YaHei UI", 13))
        input_card.card_layout.addWidget(self.ingredients_input)

        # 偏好和限制
        pref_layout = QHBoxLayout()
        pref_layout.setSpacing(20)

        # 饮食偏好
        pref_widget = QWidget()
        pref_v_layout = QVBoxLayout(pref_widget)
        pref_v_layout.setContentsMargins(0, 0, 0, 0)

        pref_label = QLabel("饮食偏好 (可选):")
        pref_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        pref_v_layout.addWidget(pref_label)

        self.preferences_input = QLineEdit()
        self.preferences_input.setPlaceholderText("如：清淡、少油、高蛋白...")
        pref_v_layout.addWidget(self.preferences_input)

        pref_layout.addWidget(pref_widget)

        # 饮食限制
        restrict_widget = QWidget()
        restrict_v_layout = QVBoxLayout(restrict_widget)
        restrict_v_layout.setContentsMargins(0, 0, 0, 0)

        restrict_label = QLabel("饮食限制 (可选):")
        restrict_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        restrict_v_layout.addWidget(restrict_label)

        self.restrictions_input = QLineEdit()
        self.restrictions_input.setPlaceholderText("如：素食、低碳水、无乳糖...")
        restrict_v_layout.addWidget(self.restrictions_input)

        pref_layout.addWidget(restrict_widget)

        input_card.card_layout.addLayout(pref_layout)

        # 生成按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.generate_btn = QPushButton("🍽️ 生成食谱")
        self.generate_btn.setMinimumWidth(200)
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        self.generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_btn.clicked.connect(self.on_generate)
        btn_layout.addWidget(self.generate_btn)

        btn_layout.addStretch()
        input_card.card_layout.addLayout(btn_layout)

        # API 配置提示
        if not config.LLM_API_KEY:
            api_tip = QLabel(
                "⚠️ 未配置 LLM API Key，请设置环境变量 LOSS_LLM_API_KEY"
            )
            api_tip.setStyleSheet(f"""
                color: {COLORS["warning"]};
                background-color: rgba(245, 158, 11, 0.1);
                padding: 10px;
                border-radius: 8px;
            """)
            input_card.card_layout.addWidget(api_tip)

        self.main_layout.addWidget(input_card)

        # 加载指示器
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        self.loading_bar.setMaximumHeight(4)
        self.main_layout.addWidget(self.loading_bar)

        # 结果区域
        self.results_card = Card("📋 生成的食谱")
        self.results_card.setVisible(False)

        self.results_text = QPlainTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(500)
        self.results_text.setFont(QFont("Microsoft YaHei UI", 12))
        self.results_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {COLORS["bg_main"]};
                border: none;
                border-radius: 8px;
                padding: 16px;
                line-height: 1.6;
            }}
        """)

        self.results_card.card_layout.addWidget(self.results_text)

        # 复制按钮
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()

        self.copy_btn = QPushButton("📋 复制食谱")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setProperty("class", "secondary")
        self.copy_btn.clicked.connect(self.on_copy)
        copy_layout.addWidget(self.copy_btn)

        self.results_card.card_layout.addLayout(copy_layout)

        self.main_layout.addWidget(self.results_card)
        self.main_layout.addStretch()

    def on_generate(self):
        """生成食谱"""
        ingredients_text = self.ingredients_input.text().strip()

        if not ingredients_text:
            QMessageBox.warning(self, "提示", "请输入可用的食材")
            return

        if not config.LLM_API_KEY:
            QMessageBox.warning(
                self, "配置错误",
                "未配置 LLM API Key\n\n"
                "请设置环境变量：\n"
                "LOSS_LLM_API_KEY=your-api-key\n\n"
                "可选配置：\n"
                "LOSS_LLM_BASE_URL=https://api.openai.com/v1\n"
                "LOSS_LLM_MODEL=gpt-3.5-turbo"
            )
            return

        # 解析食材
        ingredients = [
            item.strip()
            for item in ingredients_text.replace("，", ",").replace(" ", ",").split(",")
            if item.strip()
        ]

        preferences = self.preferences_input.text().strip()
        restrictions = self.restrictions_input.text().strip()

        # 显示加载状态
        self.loading_bar.setVisible(True)
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("生成中...")
        self.results_card.setVisible(False)

        # 启动工作线程
        self.worker = MealPlanWorker(ingredients, preferences, restrictions)
        self.worker.finished.connect(self.on_generate_finished)
        self.worker.error.connect(self.on_generate_error)
        self.worker.start()

    def on_generate_finished(self, result: str):
        """生成完成"""
        self.loading_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("🍽️ 生成食谱")

        self.results_card.setVisible(True)
        self.results_text.setPlainText(result)

    def on_generate_error(self, error: str):
        """生成出错"""
        self.loading_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("🍽️ 生成食谱")

        QMessageBox.critical(self, "生成失败", f"食谱生成失败：\n{error}")

    def on_copy(self):
        """复制食谱"""
        from PySide6.QtWidgets import QApplication

        text = self.results_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "成功", "食谱已复制到剪贴板")
