"""
LossWeightEasily 主程序入口

这是一个向后兼容的入口文件，实际功能已迁移到 src/loss_weight/ 模块。
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loss_weight.config import config
from loss_weight.query import interactive_query, initialize_system


def main():
    """主入口函数"""
    # 检查数据库是否存在
    if not config.database_exists():
        json_path = config.get_json_data_path()
        if not json_path.exists():
            print(f"❌ 错误: 找不到数据文件 {json_path}")
            print(f"💡 请确保数据文件位于: data/ 目录下")
            return
        
        print("📥 首次运行，正在初始化...")
        initialize_system()
        print("\n✅ 数据初始化完成！\n")
    
    # 启动交互式查询
    interactive_query()


# 导出常用函数（向后兼容）
def query_food_calories(search_term, db_path="food_data.db"):
    """查询食物卡路里（向后兼容接口）"""
    from loss_weight.query import query_food_calories as _query
    _query(search_term, db_path)


if __name__ == "__main__":
    main()
