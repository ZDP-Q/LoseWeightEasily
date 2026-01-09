"""
命令行入口模块

提供命令行接口 (CLI) 功能。
"""

import argparse
import sys

from .bmr import calculate_bmr, calculate_tdee
from .config import config
from .database import DatabaseManager
from .meal_planner import interactive_meal_planning
from .query import initialize_system, interactive_query, query_food_calories
from .search import FoodSearchEngine


def check_db_exists(db_path: str = None) -> bool:
    """检查数据库是否存在，不存在则打印错误并返回 False"""
    if not config.database_exists():
        print("❌ 数据库不存在，请先运行 'loss-weight init' 初始化")
        return False
    return True


def handle_search(args):
    """处理 search 命令"""
    if not check_db_exists(args.db):
        sys.exit(1)
    query_food_calories(args.query, args.db, args.limit)


def handle_interactive(args):
    """处理 interactive 命令"""
    if not check_db_exists(args.db):
        sys.exit(1)
    interactive_query(args.db)


def handle_init(args):
    """处理 init 命令"""
    initialize_system(args.db, force_rebuild=args.force)
    print("\n✅ 初始化完成！")


def handle_stats(args):
    """处理 stats 命令"""
    if not check_db_exists(args.db):
        sys.exit(1)

    db_manager = DatabaseManager(args.db)
    stats = db_manager.get_statistics()

    print("\n📊 数据库统计:")
    print(f"   食品数量: {stats['foods']}")
    print(f"   营养素种类: {stats['nutrients']}")
    print(f"   食品-营养素关联: {stats['food_nutrients']}")
    print(f"   份量数据: {stats['portions']}")


def handle_rebuild_index(args):
    """处理 rebuild-index 命令"""
    if not check_db_exists(args.db):
        sys.exit(1)

    engine = FoodSearchEngine(args.db)
    engine.build_index(force_rebuild=True)
    print("\n✅ 索引重建完成！")


def handle_bmr(args):
    """处理 bmr 命令"""
    # 如果参数不全，提示错误
    if not all([args.weight, args.height, args.age, args.gender]):
        print("❌ 请提供完整信息")
        print("用法示例: loss-weight bmr --weight 70 --height 175 --age 25 --gender male")
        return

    try:
        bmr = calculate_bmr(args.weight, args.height, args.age, args.gender)
        print("\n👤 基础代谢率 (BMR) 计算结果:")
        print(f"   性别: {'男' if args.gender == 'male' else '女'}")
        print(f"   年龄: {args.age} 岁")
        print(f"   身高: {args.height} cm")
        print(f"   体重: {args.weight} kg")
        print("-" * 30)
        print(f"🔥 BMR: {bmr:.0f} kcal/day")
        print("-" * 30)
        print("📅 每日总能量消耗 (TDEE) 参考:")

        activities = [
            ("sedentary", "久坐 (办公室工作)", "1.2"),
            ("light", "轻度活动 (每周1-3次)", "1.375"),
            ("moderate", "中度活动 (每周3-5次)", "1.55"),
            ("active", "重度活动 (每周6-7次)", "1.725"),
            ("very_active", "极重度活动 (体力工作)", "1.9")
        ]

        for code, desc, _factor in activities:
            tdee = calculate_tdee(bmr, code)
            print(f"   • {desc:<14}: {tdee:.0f} kcal")

    except Exception as e:
        print(f"❌ 计算出错: {e}")


def handle_meal_plan(args):
    """处理 meal-plan 命令"""
    interactive_meal_planning()


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog="loss-weight",
        description="🍎 食物卡路里查询系统 - 基于语义搜索的智能营养查询工具"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # --- 注册 search 命令 ---
    search_parser = subparsers.add_parser("search", help="搜索食物卡路里")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("-n", "--limit", type=int, default=10, help="结果数量限制")
    search_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    search_parser.set_defaults(func=handle_search)

    # --- 注册 interactive 命令 ---
    interactive_parser = subparsers.add_parser("interactive", aliases=["i"], help="交互式查询")
    interactive_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    interactive_parser.set_defaults(func=handle_interactive)

    # --- 注册 init 命令 ---
    init_parser = subparsers.add_parser("init", help="初始化数据库和索引")
    init_parser.add_argument("--force", action="store_true", help="强制重建")
    init_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    init_parser.set_defaults(func=handle_init)

    # --- 注册 stats 命令 ---
    stats_parser = subparsers.add_parser("stats", help="显示数据库统计")
    stats_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    stats_parser.set_defaults(func=handle_stats)

    # --- 注册 rebuild-index 命令 ---
    rebuild_parser = subparsers.add_parser("rebuild-index", help="重建搜索索引")
    rebuild_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    rebuild_parser.set_defaults(func=handle_rebuild_index)

    # --- 注册 bmr 命令 ---
    bmr_parser = subparsers.add_parser("bmr", help="计算基础代谢率 (BMR)")
    bmr_parser.add_argument("-w", "--weight", type=float, help="体重 (kg)")
    bmr_parser.add_argument("-H", "--height", type=float, help="身高 (cm)") # -h is used for help
    bmr_parser.add_argument("-a", "--age", type=int, help="年龄")
    bmr_parser.add_argument("-g", "--gender", choices=["male", "female"], help="性别 (male/female)")
    bmr_parser.set_defaults(func=handle_bmr)

    # --- 注册 meal-plan 命令 ---
    meal_plan_parser = subparsers.add_parser("meal-plan", help="生成一日三餐食谱")
    meal_plan_parser.set_defaults(func=handle_meal_plan)

    args = parser.parse_args()

    # 如果没有命令，默认启动交互式模式
    if args.command is None:
        if not config.database_exists():
            print("⚠️  数据库不存在，正在初始化...")
            try:
                initialize_system()
            except FileNotFoundError as e:
                print(f"❌ {e}")
                print(f"💡 请确保数据文件位于: {config.get_json_data_path()}")
                sys.exit(1)

        interactive_query()
        return

    # 调用对应的处理函数
    if hasattr(args, 'func'):
        args.func(args)
    else:
        # Fallback for unforeseen cases
        parser.print_help()


if __name__ == "__main__":
    main()
