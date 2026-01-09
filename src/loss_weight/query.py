"""
查询接口模块

提供用户友好的查询接口和交互式命令行界面。
"""


from .config import config
from .database import DatabaseManager
from .search import FoodSearchEngine


def query_food_calories(
    search_term: str,
    db_path: str = None,
    limit: int = None,
    engine: FoodSearchEngine = None
) -> None:
    """
    查询食物卡路里的主函数

    Args:
        search_term: 搜索关键词
        db_path: 数据库路径
        limit: 结果数量限制
        engine: 搜索引擎实例（可复用）
    """
    db_path = db_path or config.DB_PATH
    limit = limit or config.DEFAULT_SEARCH_LIMIT

    # 使用传入的引擎或创建新引擎
    if engine is None:
        engine = FoodSearchEngine(db_path)
        engine.ensure_index()

    print(f"\n🔍 搜索: {search_term}")
    print("=" * 60)

    # 搜索食物
    results = engine.search(search_term, limit)

    if not results:
        print("❌ 未找到匹配的食物")
        return

    # 分类统计
    results_with_calories = []
    results_without_calories = []

    for fdc_id, description, category, _similarity in results:
        calorie_info = engine.db_manager.get_food_complete_info(fdc_id)
        if calorie_info and calorie_info["calories_per_100g"]:
            results_with_calories.append((fdc_id, description, category, calorie_info))
        else:
            results_without_calories.append((fdc_id, description, category))

    print(f"\n找到 {len(results)} 个匹配结果 (其中 {len(results_with_calories)} 个有热量数据):\n")

    # 优先显示有卡路里数据的结果
    idx = 1
    for _fdc_id, description, category, calorie_info in results_with_calories:
        print(f"{idx}. {description}")
        print(f"   分类: {category or '未分类'}")
        print(f"   📊 热量: {calorie_info['calories_per_100g']:.1f} {calorie_info['unit']}/100g")

        # 显示常用份量的热量
        if calorie_info["portions"]:
            print("   📏 常用份量:")
            for amount, unit, gram_weight in calorie_info["portions"][:2]:
                calories_for_portion = (calorie_info['calories_per_100g'] * gram_weight) / 100
                print(f"      • {amount} {unit} ({gram_weight}g) = {calories_for_portion:.1f} {calorie_info['unit']}")
        print()
        idx += 1

    # 显示没有卡路里数据的结果
    if results_without_calories and len(results_without_calories) <= 5:
        print("⚠️  以下食物暂无热量数据:")
        for _fdc_id, description, category in results_without_calories:
            print(f"{idx}. {description}")
            print(f"   分类: {category or '未分类'}")
            print("   ❌ 暂无热量数据\n")
            idx += 1
    elif results_without_calories:
        print(f"⚠️  另有 {len(results_without_calories)} 个食物暂无热量数据（已隐藏）")


def interactive_query(db_path: str = None) -> None:
    """
    交互式查询界面

    Args:
        db_path: 数据库路径
    """
    db_path = db_path or config.DB_PATH

    print("\n" + "=" * 60)
    print("🍎 LossWeightEasily - 轻松减重助手")
    print("=" * 60)
    print("支持中文和英文搜索，输入 'q' 或 'quit' 退出")
    print("=" * 60)

    # 创建搜索引擎（复用以提高性能）
    engine = FoodSearchEngine(db_path)
    engine.ensure_index()

    while True:
        try:
            search_term = input("\n请输入食物名称: ").strip()

            if not search_term:
                continue

            if search_term.lower() in ['q', 'quit', 'exit', '退出']:
                print("\n👋 再见！")
                break

            query_food_calories(search_term, db_path, engine=engine)

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 查询出错: {e}")


def initialize_system(db_path: str = None, force_rebuild: bool = False) -> None:
    """
    初始化系统（数据库和索引）

    Args:
        db_path: 数据库路径
        force_rebuild: 是否强制重建
    """
    db_path = db_path or config.DB_PATH

    # 检查数据库
    db_manager = DatabaseManager(db_path)

    if not config.database_exists() or force_rebuild:
        json_path = config.get_json_data_path()
        if not json_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {json_path}")

        print("📥 首次运行，正在导入数据...")
        stats = db_manager.import_from_json(str(json_path))
        print("\n📊 导入统计:")
        print(f"   食品数量: {stats['foods']}")
        print(f"   营养素种类: {stats['nutrients']}")
        print(f"   食品-营养素关联: {stats['food_nutrients']}")
        print(f"   份量数据: {stats['portions']}")

    # 构建搜索索引
    engine = FoodSearchEngine(db_path)
    engine.build_index(force_rebuild=force_rebuild)
