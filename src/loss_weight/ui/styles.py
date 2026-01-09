"""
全局样式表

现代化、精美的 UI 样式定义。
"""

# 颜色主题
COLORS = {
    "primary": "#6366f1",  # 主色调 - 靛蓝色
    "primary_hover": "#4f46e5",
    "primary_light": "#e0e7ff",
    "secondary": "#10b981",  # 辅助色 - 翠绿色
    "secondary_hover": "#059669",
    "accent": "#f59e0b",  # 强调色 - 琥珀色
    "danger": "#ef4444",  # 危险色 - 红色
    "warning": "#f59e0b",  # 警告色 - 橙色
    "success": "#10b981",  # 成功色 - 绿色
    "bg_dark": "#0f172a",  # 深色背景
    "bg_main": "#1e293b",  # 主背景
    "bg_card": "#334155",  # 卡片背景
    "bg_hover": "#475569",  # 悬停背景
    "text_primary": "#f8fafc",  # 主要文字
    "text_secondary": "#94a3b8",  # 次要文字
    "text_muted": "#64748b",  # 淡化文字
    "border": "#475569",  # 边框
    "border_light": "#334155",  # 浅边框
}

# 全局样式表
GLOBAL_STYLE = f"""
/* ==================== 全局样式 ==================== */
QWidget {{
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 14px;
    color: {COLORS["text_primary"]};
    background-color: transparent;
}}

QMainWindow {{
    background-color: {COLORS["bg_dark"]};
}}

/* ==================== 滚动条 ==================== */
QScrollBar:vertical {{
    background-color: {COLORS["bg_main"]};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["bg_hover"]};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["text_muted"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS["bg_main"]};
    height: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS["bg_hover"]};
    border-radius: 4px;
    min-width: 30px;
}}

/* ==================== 按钮 ==================== */
QPushButton {{
    background-color: {COLORS["primary"]};
    color: {COLORS["text_primary"]};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS["primary_hover"]};
}}

QPushButton:pressed {{
    background-color: #3730a3;
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_hover"]};
    color: {COLORS["text_muted"]};
}}

/* 次要按钮 */
QPushButton[class="secondary"] {{
    background-color: transparent;
    border: 2px solid {COLORS["border"]};
    color: {COLORS["text_secondary"]};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS["bg_hover"]};
    border-color: {COLORS["text_secondary"]};
}}

/* 成功按钮 */
QPushButton[class="success"] {{
    background-color: {COLORS["success"]};
}}

QPushButton[class="success"]:hover {{
    background-color: {COLORS["secondary_hover"]};
}}

/* 危险按钮 */
QPushButton[class="danger"] {{
    background-color: {COLORS["danger"]};
}}

QPushButton[class="danger"]:hover {{
    background-color: #dc2626;
}}

/* ==================== 输入框 ==================== */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS["bg_main"]};
    border: 2px solid {COLORS["border_light"]};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS["text_primary"]};
    selection-background-color: {COLORS["primary"]};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS["primary"]};
}}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
    border-color: {COLORS["bg_hover"]};
}}

/* ==================== 下拉框 ==================== */
QComboBox {{
    background-color: {COLORS["bg_main"]};
    border: 2px solid {COLORS["border_light"]};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS["text_primary"]};
}}

QComboBox:hover {{
    border-color: {COLORS["bg_hover"]};
}}

QComboBox:focus {{
    border-color: {COLORS["primary"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS["text_secondary"]};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS["bg_main"]};
    border: 2px solid {COLORS["border"]};
    border-radius: 8px;
    selection-background-color: {COLORS["primary"]};
    outline: none;
}}

/* ==================== 标签 ==================== */
QLabel {{
    color: {COLORS["text_primary"]};
    background-color: transparent;
}}

QLabel[class="title"] {{
    font-size: 24px;
    font-weight: bold;
}}

QLabel[class="subtitle"] {{
    font-size: 16px;
    color: {COLORS["text_secondary"]};
}}

QLabel[class="muted"] {{
    color: {COLORS["text_muted"]};
}}

/* ==================== 分组框 ==================== */
QGroupBox {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border_light"]};
    border-radius: 12px;
    margin-top: 20px;
    padding: 20px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: {COLORS["text_primary"]};
}}

/* ==================== 表格 ==================== */
QTableWidget {{
    background-color: {COLORS["bg_card"]};
    border: none;
    border-radius: 12px;
    gridline-color: {COLORS["border_light"]};
}}

QTableWidget::item {{
    padding: 12px;
    border-bottom: 1px solid {COLORS["border_light"]};
}}

QTableWidget::item:selected {{
    background-color: {COLORS["primary"]};
}}

QHeaderView::section {{
    background-color: {COLORS["bg_main"]};
    color: {COLORS["text_secondary"]};
    padding: 12px;
    border: none;
    font-weight: bold;
}}

/* ==================== 进度条 ==================== */
QProgressBar {{
    background-color: {COLORS["bg_main"]};
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS["primary"]};
    border-radius: 6px;
}}

/* ==================== 工具提示 ==================== */
QToolTip {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 12px;
}}

/* ==================== SpinBox ==================== */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS["bg_main"]};
    border: 2px solid {COLORS["border_light"]};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS["text_primary"]};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS["primary"]};
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {COLORS["bg_hover"]};
    border: none;
    width: 20px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {COLORS["primary"]};
}}
"""

# 导航栏样式
NAV_STYLE = f"""
QWidget#nav_widget {{
    background-color: {COLORS["bg_main"]};
    border-right: 1px solid {COLORS["border_light"]};
}}

QPushButton#nav_btn {{
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 14px;
    text-align: left;
    font-size: 14px;
    color: {COLORS["text_secondary"]};
}}

QPushButton#nav_btn:hover {{
    background-color: {COLORS["bg_hover"]};
    color: {COLORS["text_primary"]};
}}

QPushButton#nav_btn:checked {{
    background-color: {COLORS["primary"]};
    color: {COLORS["text_primary"]};
}}

QPushButton#nav_toggle {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 8px;
    color: {COLORS["text_secondary"]};
}}

QPushButton#nav_toggle:hover {{
    background-color: {COLORS["bg_hover"]};
}}
"""

# 卡片样式
CARD_STYLE = f"""
QFrame#card {{
    background-color: {COLORS["bg_card"]};
    border-radius: 16px;
    padding: 20px;
}}

QFrame#card_hover:hover {{
    background-color: {COLORS["bg_hover"]};
}}
"""

# 仪表盘统计卡片样式
STAT_CARD_STYLE = f"""
QFrame#stat_card {{
    background-color: {COLORS["bg_card"]};
    border-radius: 16px;
    padding: 20px;
    min-width: 200px;
}}

QLabel#stat_value {{
    font-size: 32px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
}}

QLabel#stat_label {{
    font-size: 14px;
    color: {COLORS["text_secondary"]};
}}

QLabel#stat_change_positive {{
    color: {COLORS["success"]};
    font-size: 13px;
}}

QLabel#stat_change_negative {{
    color: {COLORS["danger"]};
    font-size: 13px;
}}
"""
