"""
命令行入口模块

提供命令行接口 (CLI) 功能。
使用依赖注入容器管理服务。
"""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace


def check_db_exists() -> bool:
    """检查数据库是否存在，不存在则打印错误并返回 False"""
    from .config import get_settings
    from .logging_config import get_logger

    logger = get_logger(__name__)
    settings = get_settings()
    if not settings.database_exists():
        logger.error("数据库不存在，请先运行 'loss-weight init' 初始化")
        return False
    return True


def handle_search(args: Namespace) -> None:
    """处理 search 命令"""
    if not check_db_exists():
        sys.exit(1)

    from .query import query_food_calories

    query_food_calories(args.query, args.db, args.limit)


def handle_interactive(args: Namespace) -> None:
    """处理 interactive 命令"""
    if not check_db_exists():
        sys.exit(1)

    from .query import interactive_query

    interactive_query(args.db)


def handle_init(args: Namespace) -> None:
    """处理 init 命令"""
    from .logging_config import get_logger
    from .query import initialize_system

    logger = get_logger(__name__)
    initialize_system(args.db, force_rebuild=args.force)
    logger.info("初始化完成！")


def handle_stats(args: Namespace) -> None:
    """处理 stats 命令"""
    if not check_db_exists():
        sys.exit(1)

    from .container import get_database
    from .logging_config import get_logger

    logger = get_logger(__name__)
    stats = get_database().get_statistics()

    logger.info(
        f"数据库统计: 食品数量={stats.foods}, 营养素种类={stats.nutrients}, "
        f"食品-营养素关联={stats.food_nutrients}, 份量数据={stats.portions}"
    )


def handle_rebuild_index(args: Namespace) -> None:
    """处理 rebuild-index 命令"""
    if not check_db_exists():
        sys.exit(1)

    from .container import get_search_engine

    get_search_engine().build_index(force_rebuild=True)
    print("\n✅ 索引重建完成！")


def handle_bmr(args: Namespace) -> None:
    """处理 bmr 命令"""
    # 如果参数不全，提示错误
    if not all([args.weight, args.height, args.age, args.gender]):
        print("❌ 请提供完整信息")
        print("用法示例: loss-weight bmr --weight 70 --height 175 --age 25 --gender male")
        return

    from .bmr import calculate_bmr, calculate_tdee

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
            ("very_active", "极重度活动 (体力工作)", "1.9"),
        ]

        for code, desc, _factor in activities:
            tdee = calculate_tdee(bmr, code)
            print(f"   • {desc:<14}: {tdee:.0f} kcal")

    except Exception as e:
        print(f"❌ 计算出错: {e}")


def handle_meal_plan(args: Namespace) -> None:
    """处理 meal-plan 命令"""
    from .meal_planner import interactive_meal_planning

    interactive_meal_planning()


def handle_weight_checkin(args: Namespace) -> None:
    """处理 weight 命令"""
    from .weight_tracker import interactive_weight_checkin

    interactive_weight_checkin()


def handle_weight_history(args: Namespace) -> None:
    """处理 weight-history 命令"""
    from .weight_tracker import show_weight_history

    limit = args.limit if hasattr(args, "limit") else 30
    show_weight_history(limit)


def main() -> None:
    """主入口函数"""
    # 初始化日志系统
    from .container import get_container, get_logger

    container = get_container()
    logger = get_logger(__name__)
    logger.debug("CLI 启动")

    # 懒加载配置
    settings = container.settings

    parser = argparse.ArgumentParser(
        prog="loss-weight", description="🍎 LossWeightEasily - 帮助你轻松减重的智能健康管理工具"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # --- 注册 search 命令 ---
    search_parser = subparsers.add_parser("search", help="搜索食物卡路里")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("-n", "--limit", type=int, default=10, help="结果数量限制")
    search_parser.add_argument("--db", default=settings.DB_PATH, help="数据库路径")
    search_parser.set_defaults(func=handle_search)

    # --- 注册 interactive 命令 ---
    interactive_parser = subparsers.add_parser("interactive", aliases=["i"], help="交互式查询")
    interactive_parser.add_argument("--db", default=settings.DB_PATH, help="数据库路径")
    interactive_parser.set_defaults(func=handle_interactive)

    # --- 注册 init 命令 ---
    init_parser = subparsers.add_parser("init", help="初始化数据库和索引")
    init_parser.add_argument("--force", action="store_true", help="强制重建")
    init_parser.add_argument("--db", default=settings.DB_PATH, help="数据库路径")
    init_parser.set_defaults(func=handle_init)

    # --- 注册 stats 命令 ---
    stats_parser = subparsers.add_parser("stats", help="显示数据库统计")
    stats_parser.add_argument("--db", default=settings.DB_PATH, help="数据库路径")
    stats_parser.set_defaults(func=handle_stats)

    # --- 注册 rebuild-index 命令 ---
    rebuild_parser = subparsers.add_parser("rebuild-index", help="重建搜索索引")
    rebuild_parser.add_argument("--db", default=settings.DB_PATH, help="数据库路径")
    rebuild_parser.set_defaults(func=handle_rebuild_index)

    # --- 注册 bmr 命令 ---
    bmr_parser = subparsers.add_parser("bmr", help="计算基础代谢率 (BMR)")
    bmr_parser.add_argument("-w", "--weight", type=float, help="体重 (kg)")
    bmr_parser.add_argument("-H", "--height", type=float, help="身高 (cm)")  # -h is used for help
    bmr_parser.add_argument("-a", "--age", type=int, help="年龄")
    bmr_parser.add_argument("-g", "--gender", choices=["male", "female"], help="性别 (male/female)")
    bmr_parser.set_defaults(func=handle_bmr)

    # --- 注册 meal-plan 命令 ---
    meal_plan_parser = subparsers.add_parser("meal-plan", help="生成一日三餐食谱")
    meal_plan_parser.set_defaults(func=handle_meal_plan)

    # --- 注册 weight 命令 ---
    weight_parser = subparsers.add_parser("weight", help="每日体重打卡")
    weight_parser.set_defaults(func=handle_weight_checkin)

    # --- 注册 weight-history 命令 ---
    weight_history_parser = subparsers.add_parser("weight-history", help="查看体重历史记录")
    weight_history_parser.add_argument("-n", "--limit", type=int, default=30, help="显示记录数量")
    weight_history_parser.set_defaults(func=handle_weight_history)

    args = parser.parse_args()

    # 如果没有命令，默认启动交互式模式
    if args.command is None:
        if not settings.database_exists():
            print("⚠️  数据库不存在，正在初始化...")
            try:
                from .query import initialize_system

                initialize_system()
            except FileNotFoundError as e:
                print(f"❌ {e}")
                print(f"💡 请确保数据文件位于: {settings.get_json_data_path()}")
                sys.exit(1)

        from .query import interactive_query

        interactive_query()
        return

    # 调用对应的处理函数
    if hasattr(args, "func"):
        args.func(args)
    else:
        # Fallback for unforeseen cases
        parser.print_help()


if __name__ == "__main__":
    main()
