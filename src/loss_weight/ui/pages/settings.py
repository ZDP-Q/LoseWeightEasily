"""
设置页面

应用设置和配置管理。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from ...config import config
from ..styles import COLORS
from .base import Card, ScrollablePage


class SettingsPage(ScrollablePage):
    """设置页面"""

    def __init__(self, parent=None):
        self.page_title = "设置"
        super().__init__(self.page_title, parent)
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 关于
        about_card = Card("📱 关于")

        app_info = QLabel("""
<h2 style="margin: 0;">🍎 LossWeightEasily</h2>
<p style="color: #94a3b8; margin-top: 8px;">
    帮助你轻松减重的智能健康管理工具
</p>
<p style="color: #64748b; margin-top: 4px;">
    版本: 0.2.0 | 作者: ZDP-Q
</p>
        """)
        app_info.setTextFormat(Qt.TextFormat.RichText)
        about_card.card_layout.addWidget(app_info)

        self.main_layout.addWidget(about_card)

        # LLM API 配置
        api_card = Card("🤖 LLM API 配置")

        api_info = QLabel(
            "食谱规划功能需要配置 LLM API。支持 OpenAI、DeepSeek 等兼容服务。"
        )
        api_info.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-bottom: 16px;")
        api_info.setWordWrap(True)
        api_card.card_layout.addWidget(api_info)

        # 当前配置状态
        status_text = "✅ 已配置" if config.LLM_API_KEY else "❌ 未配置"
        status_color = COLORS["success"] if config.LLM_API_KEY else COLORS["danger"]

        # 配置来源
        config_source = config.get_config_source("LLM_API_KEY")
        source_text = {
            "env": "环境变量",
            "yaml": "config.yaml",
            "default": "默认值"
        }.get(config_source, "未知")

        status_layout = QHBoxLayout()
        status_label = QLabel("API Key 状态:")
        status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        status_layout.addWidget(status_label)

        status_value = QLabel(f"{status_text} ({source_text})")
        status_value.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        status_layout.addWidget(status_value)
        status_layout.addStretch()

        api_card.card_layout.addLayout(status_layout)

        # 模型配置显示
        model_layout = QHBoxLayout()
        model_label = QLabel("当前模型:")
        model_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        model_layout.addWidget(model_label)

        model_value = QLabel(config.LLM_MODEL)
        model_value.setStyleSheet(f"color: {COLORS['text_primary']};")
        model_layout.addWidget(model_value)
        model_layout.addStretch()

        api_card.card_layout.addLayout(model_layout)

        # Base URL
        url_layout = QHBoxLayout()
        url_label = QLabel("API 地址:")
        url_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        url_layout.addWidget(url_label)

        url_value = QLabel(config.LLM_BASE_URL)
        url_value.setStyleSheet(f"color: {COLORS['text_muted']};")
        url_layout.addWidget(url_value)
        url_layout.addStretch()

        api_card.card_layout.addLayout(url_layout)

        # 配置说明
        config_info = QFrame()
        config_info.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_main"]};
                border-radius: 8px;
                padding: 16px;
                margin-top: 16px;
            }}
        """)

        config_layout = QVBoxLayout(config_info)

        config_title = QLabel("💡 配置方法")
        config_title.setFont(QFont("Microsoft YaHei UI", 12, QFont.Weight.Bold))
        config_layout.addWidget(config_title)

        config_text = QLabel("""
配置方法（任选其一）：

<b>方法 1：编辑 config.yaml 文件</b>
修改项目根目录的 config.yaml 文件：
<code>
llm:
  api_key: "your-api-key"
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
</code>

<b>方法 2：设置环境变量</b>（优先级更高）
PowerShell 示例：
<code>
$env:LOSS_LLM_API_KEY="your-api-key"
$env:LOSS_LLM_BASE_URL="https://api.openai.com/v1"
$env:LOSS_LLM_MODEL="gpt-3.5-turbo"
</code>

配置优先级：环境变量 > config.yaml > 默认值
        """)
        config_text.setStyleSheet(f"color: {COLORS['text_secondary']};")
        config_text.setTextFormat(Qt.TextFormat.RichText)
        config_text.setWordWrap(True)
        config_layout.addWidget(config_text)

        api_card.card_layout.addWidget(config_info)

        self.main_layout.addWidget(api_card)

        # 数据管理
        data_card = Card("💾 数据管理")

        # 数据库状态
        db_status = "✅ 已初始化" if config.database_exists() else "❌ 未初始化"
        db_color = COLORS["success"] if config.database_exists() else COLORS["danger"]

        db_layout = QHBoxLayout()
        db_label = QLabel("数据库状态:")
        db_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        db_layout.addWidget(db_label)

        db_value = QLabel(db_status)
        db_value.setStyleSheet(f"color: {db_color}; font-weight: bold;")
        db_layout.addWidget(db_value)
        db_layout.addStretch()

        data_card.card_layout.addLayout(db_layout)

        # 索引状态
        index_status = "✅ 已构建" if config.index_exists() else "❌ 未构建"
        index_color = COLORS["success"] if config.index_exists() else COLORS["danger"]

        index_layout = QHBoxLayout()
        index_label = QLabel("搜索索引:")
        index_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        index_layout.addWidget(index_label)

        index_value = QLabel(index_status)
        index_value.setStyleSheet(f"color: {index_color}; font-weight: bold;")
        index_layout.addWidget(index_value)
        index_layout.addStretch()

        data_card.card_layout.addLayout(index_layout)

        self.main_layout.addWidget(data_card)

        # 帮助
        help_card = Card("❓ 帮助")

        help_links = QLabel(f"""
<p>📖 <a href="https://github.com/ZDP-Q/LossWeightEasily" style="color: {COLORS['primary']};">GitHub 仓库</a></p>
<p>📝 <a href="https://github.com/ZDP-Q/LossWeightEasily/issues" style="color: {COLORS['primary']};">报告问题</a></p>
<p>💬 <a href="https://github.com/ZDP-Q/LossWeightEasily/discussions" style="color: {COLORS['primary']};">讨论区</a></p>
        """)
        help_links.setTextFormat(Qt.TextFormat.RichText)
        help_links.setOpenExternalLinks(True)
        help_card.card_layout.addWidget(help_links)

        self.main_layout.addWidget(help_card)

        self.main_layout.addStretch()
