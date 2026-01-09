"""
BMR 计算页面

计算基础代谢率和每日总能量消耗。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...bmr import calculate_bmr, calculate_tdee
from ..styles import COLORS
from .base import Card, ScrollablePage, StatCard


class BMRPage(ScrollablePage):
    """BMR 计算页面"""

    def __init__(self, parent=None):
        self.page_title = "代谢计算"
        super().__init__(self.page_title, parent)
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 输入区域
        input_card = Card("📝 输入个人信息")

        form_layout = QGridLayout()
        form_layout.setSpacing(20)
        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(3, 1)

        # 性别
        gender_label = QLabel("性别:")
        gender_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        form_layout.addWidget(gender_label, 0, 0)

        gender_widget = QWidget()
        gender_layout = QHBoxLayout(gender_widget)
        gender_layout.setContentsMargins(0, 0, 0, 0)
        gender_layout.setSpacing(20)

        self.gender_group = QButtonGroup(self)
        self.male_radio = QRadioButton("👨 男")
        self.male_radio.setChecked(True)
        self.male_radio.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.female_radio = QRadioButton("👩 女")
        self.female_radio.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.gender_group.addButton(self.male_radio, 0)
        self.gender_group.addButton(self.female_radio, 1)

        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        gender_layout.addStretch()

        form_layout.addWidget(gender_widget, 0, 1)

        # 年龄
        age_label = QLabel("年龄:")
        age_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        form_layout.addWidget(age_label, 0, 2)

        self.age_input = QSpinBox()
        self.age_input.setRange(10, 120)
        self.age_input.setValue(25)
        self.age_input.setSuffix(" 岁")
        self.age_input.setMinimumWidth(120)
        form_layout.addWidget(self.age_input, 0, 3)

        # 身高
        height_label = QLabel("身高:")
        height_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        form_layout.addWidget(height_label, 1, 0)

        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(100, 250)
        self.height_input.setValue(170)
        self.height_input.setDecimals(1)
        self.height_input.setSuffix(" cm")
        self.height_input.setMinimumWidth(120)
        form_layout.addWidget(self.height_input, 1, 1)

        # 体重
        weight_label = QLabel("体重:")
        weight_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        form_layout.addWidget(weight_label, 1, 2)

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(30, 300)
        self.weight_input.setValue(65)
        self.weight_input.setDecimals(1)
        self.weight_input.setSuffix(" kg")
        self.weight_input.setMinimumWidth(120)
        form_layout.addWidget(self.weight_input, 1, 3)

        # 活动水平
        activity_label = QLabel("活动水平:")
        activity_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        form_layout.addWidget(activity_label, 2, 0)

        self.activity_combo = QComboBox()
        self.activity_combo.addItems(
            [
                "🛋️ 久坐 (办公室工作，很少运动)",
                "🚶 轻度活动 (每周运动 1-3 天)",
                "🏃 中度活动 (每周运动 3-5 天)",
                "💪 重度活动 (每周运动 6-7 天)",
                "🔥 极重度活动 (体力工作或双倍训练)",
            ]
        )
        self.activity_combo.setMinimumWidth(300)
        form_layout.addWidget(self.activity_combo, 2, 1, 1, 3)

        input_card.card_layout.addLayout(form_layout)

        # 计算按钮
        calc_btn_layout = QHBoxLayout()
        calc_btn_layout.addStretch()

        self.calc_btn = QPushButton("🔥 计算代谢率")
        self.calc_btn.setMinimumWidth(200)
        self.calc_btn.setMinimumHeight(50)
        self.calc_btn.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        self.calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.calc_btn.clicked.connect(self.on_calculate)
        calc_btn_layout.addWidget(self.calc_btn)

        calc_btn_layout.addStretch()
        input_card.card_layout.addLayout(calc_btn_layout)

        self.main_layout.addWidget(input_card)

        # 结果区域
        self.results_card = Card("📊 计算结果")
        self.results_card.setVisible(False)

        # BMR 结果
        bmr_layout = QHBoxLayout()
        bmr_layout.setSpacing(40)

        self.bmr_stat = StatCard(
            title="基础代谢率 (BMR)",
            value="-- kcal/天",
            icon="🔥",
            change="身体维持基本功能所需能量",
        )
        bmr_layout.addWidget(self.bmr_stat)

        self.tdee_stat = StatCard(
            title="每日总消耗 (TDEE)",
            value="-- kcal/天",
            icon="⚡",
            change="包含日常活动的总能量消耗",
        )
        bmr_layout.addWidget(self.tdee_stat)

        self.results_card.card_layout.addLayout(bmr_layout)

        # 减重建议
        self.advice_frame = QFrame()
        self.advice_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_main"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        advice_layout = QVBoxLayout(self.advice_frame)

        advice_title = QLabel("💡 减重建议")
        advice_title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        advice_layout.addWidget(advice_title)

        self.advice_content = QLabel()
        self.advice_content.setWordWrap(True)
        self.advice_content.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.6;")
        advice_layout.addWidget(self.advice_content)

        self.results_card.card_layout.addWidget(self.advice_frame)

        # TDEE 各活动水平对比
        self.tdee_compare_frame = QFrame()
        self.tdee_compare_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_main"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        compare_layout = QVBoxLayout(self.tdee_compare_frame)

        compare_title = QLabel("📈 不同活动水平的 TDEE 对比")
        compare_title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        compare_layout.addWidget(compare_title)

        self.tdee_labels = {}
        activities = [
            ("sedentary", "久坐", "🛋️"),
            ("light", "轻度活动", "🚶"),
            ("moderate", "中度活动", "🏃"),
            ("active", "重度活动", "💪"),
            ("very_active", "极重度活动", "🔥"),
        ]

        for key, name, icon in activities:
            row = QHBoxLayout()
            row.setSpacing(20)

            label = QLabel(f"{icon} {name}:")
            label.setMinimumWidth(150)
            label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            row.addWidget(label)

            value = QLabel("--")
            value.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
            self.tdee_labels[key] = value
            row.addWidget(value)

            row.addStretch()
            compare_layout.addLayout(row)

        self.results_card.card_layout.addWidget(self.tdee_compare_frame)

        self.main_layout.addWidget(self.results_card)
        self.main_layout.addStretch()

    def on_calculate(self):
        """执行计算"""
        # 获取输入值
        gender = "male" if self.male_radio.isChecked() else "female"
        age = self.age_input.value()
        height = self.height_input.value()
        weight = self.weight_input.value()

        activity_index = self.activity_combo.currentIndex()
        activity_keys = ["sedentary", "light", "moderate", "active", "very_active"]
        activity_level = activity_keys[activity_index]

        # 计算 BMR
        bmr = calculate_bmr(weight, height, age, gender)

        # 计算 TDEE
        tdee = calculate_tdee(bmr, activity_level)

        # 更新结果显示
        self.results_card.setVisible(True)

        self.bmr_stat.update_value(f"{bmr:.0f} kcal/天")
        self.tdee_stat.update_value(f"{tdee:.0f} kcal/天")

        # 更新各活动水平的 TDEE
        for key in activity_keys:
            tdee_value = calculate_tdee(bmr, key)
            self.tdee_labels[key].setText(f"{tdee_value:.0f} kcal/天")

            # 高亮当前选择的活动水平
            if key == activity_level:
                self.tdee_labels[key].setStyleSheet(
                    f"color: {COLORS['primary']}; font-weight: bold;"
                )
            else:
                self.tdee_labels[key].setStyleSheet(f"color: {COLORS['text_primary']};")

        # 生成减重建议
        deficit_500 = tdee - 500  # 每周减重约0.5kg
        deficit_750 = tdee - 750  # 每周减重约0.75kg

        advice = f"""
根据您的数据，要健康减重，建议：

• 温和减重（每周约 0.5 kg）：每日摄入约 {deficit_500:.0f} kcal
• 中等减重（每周约 0.75 kg）：每日摄入约 {deficit_750:.0f} kcal

⚠️ 注意：每日摄入不应低于 {1200 if gender == "female" else 1500} kcal，以确保基本营养需求。
建议结合适量运动，既能增加能量消耗，又能保持肌肉量。
        """
        self.advice_content.setText(advice.strip())
