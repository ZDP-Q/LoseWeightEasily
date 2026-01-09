"""
命令行入口模块

提供命令行接口 (CLI) 功能。
"""

import argparse
import sys
from pathlib import Path

from .config import config
from .query import interactive_query, query_food_calories, initialize_system
from .database import DatabaseManager
from .search import FoodSearchEngine


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog="loss-weight",
        description="🍎 食物卡路里查询系统 - 基于语义搜索的智能营养查询工具"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索食物卡路里")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("-n", "--limit", type=int, default=10, help="结果数量限制")
    search_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    
    # interactive 命令
    interactive_parser = subparsers.add_parser("interactive", aliases=["i"], help="交互式查询")
    interactive_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化数据库和索引")
    init_parser.add_argument("--force", action="store_true", help="强制重建")
    init_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示数据库统计")
    stats_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    
    # rebuild-index 命令
    rebuild_parser = subparsers.add_parser("rebuild-index", help="重建搜索索引")
    rebuild_parser.add_argument("--db", default=config.DB_PATH, help="数据库路径")
    
    args = parser.parse_args()
    
    # 如果没有命令，默认启动交互式模式
    if args.command is None:
        # 检查是否需要初始化
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
    
    if args.command == "search":
        if not config.database_exists():
            print("❌ 数据库不存在，请先运行 'loss-weight init' 初始化")
            sys.exit(1)
        query_food_calories(args.query, args.db, args.limit)
    
    elif args.command in ["interactive", "i"]:
        if not config.database_exists():
            print("❌ 数据库不存在，请先运行 'loss-weight init' 初始化")
            sys.exit(1)
        interactive_query(args.db)
    
    elif args.command == "init":
        initialize_system(args.db, force_rebuild=args.force)
        print("\n✅ 初始化完成！")
    
    elif args.command == "stats":
        if not config.database_exists():
            print("❌ 数据库不存在")
            sys.exit(1)
        
        db_manager = DatabaseManager(args.db)
        stats = db_manager.get_statistics()
        
        print("\n📊 数据库统计:")
        print(f"   食品数量: {stats['foods']}")
        print(f"   营养素种类: {stats['nutrients']}")
        print(f"   食品-营养素关联: {stats['food_nutrients']}")
        print(f"   份量数据: {stats['portions']}")
    
    elif args.command == "rebuild-index":
        if not config.database_exists():
            print("❌ 数据库不存在，请先运行 'loss-weight init' 初始化")
            sys.exit(1)
        
        engine = FoodSearchEngine(args.db)
        engine.build_index(force_rebuild=True)
        print("\n✅ 索引重建完成！")


if __name__ == "__main__":
    main()
